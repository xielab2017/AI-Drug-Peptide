#!/usr/bin/env python3
"""
Prefect工作流脚本 - 肽段药物开发完整流程
==========================================

功能：
1. 定义5个任务：参数初始化→数据拉取→分泌路径+受体分析→肽段优化→可视化+报告生成
2. 任务依赖：参数初始化完成→数据拉取→分析→优化→报告
3. 配置告警：任意任务失败时，自动发送邮件至指定邮箱（配置在config.json）
4. 支持"断点续跑"：某一步失败修复后，从失败步骤重新执行
5. 执行完成后，输出"流程总结报告"（TXT），显示各步骤耗时、成功/失败状态

作者：AI-Drug Peptide Project
日期：2024
"""

import os
import sys
import json
import time
import logging
import smtplib
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Prefect imports
from prefect import flow, task, get_run_logger
from prefect.task_runners import ConcurrentTaskRunner
from prefect.blocks.system import Secret
from prefect.artifacts import create_markdown_artifact
from prefect.filesystems import LocalFileSystem

# 项目模块导入
try:
    from input_init import ProteinInputInitializer
    from data_fetch_robust import DataFetcher
    from secretion_analysis import SecretionAnalyzer
    from peptide_optim import PeptideOptimizationPipeline
    from report_generator import ReportGenerator
except ImportError as e:
    print(f"Warning: Some modules not available: {e}")
    # 定义占位符类
    class ProteinInputInitializer:
        def run(self): return None
    class DataFetcher:
        def run_all(self): return None
    class SecretionAnalyzer:
        def run_analysis(self): return None
    class PeptideOptimizationPipeline:
        def optimize_peptides(self): return None
    class ReportGenerator:
        def generate_report(self): return None

# 配置常量
CONFIG_FILE = "config/config.json"
WORKFLOW_STATE_FILE = "workflow_state.json"
SUMMARY_REPORT_FILE = "workflow_summary_report.txt"

@dataclass
class TaskResult:
    """任务执行结果"""
    task_name: str
    success: bool
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    checkpoint_data: Optional[Dict[str, Any]] = None

@dataclass
class WorkflowState:
    """工作流状态管理"""
    current_step: int = 1
    completed_steps: List[int] = None
    failed_steps: List[int] = None
    task_results: List[TaskResult] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.completed_steps is None:
            self.completed_steps = []
        if self.failed_steps is None:
            self.failed_steps = []
        if self.task_results is None:
            self.task_results = []

class WorkflowManager:
    """工作流管理器 - 负责状态管理和断点续跑"""
    
    def __init__(self, state_file: str = WORKFLOW_STATE_FILE):
        self.state_file = Path(state_file)
        self.state = self.load_state()
    
    def load_state(self) -> WorkflowState:
        """加载工作流状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 转换datetime字符串
                if data.get('start_time'):
                    data['start_time'] = datetime.fromisoformat(data['start_time'])
                if data.get('end_time'):
                    data['end_time'] = datetime.fromisoformat(data['end_time'])
                
                # 转换TaskResult对象
                if data.get('task_results'):
                    task_results = []
                    for tr_data in data['task_results']:
                        if tr_data.get('start_time'):
                            tr_data['start_time'] = datetime.fromisoformat(tr_data['start_time'])
                        if tr_data.get('end_time'):
                            tr_data['end_time'] = datetime.fromisoformat(tr_data['end_time'])
                        task_results.append(TaskResult(**tr_data))
                    data['task_results'] = task_results
                
                return WorkflowState(**data)
            except Exception as e:
                logging.warning(f"Failed to load state file: {e}")
        
        return WorkflowState()
    
    def save_state(self):
        """保存工作流状态"""
        try:
            # 转换为可序列化的格式
            state_data = {
                'current_step': self.state.current_step,
                'completed_steps': self.state.completed_steps,
                'failed_steps': self.state.failed_steps,
                'task_results': [],
                'start_time': self.state.start_time.isoformat() if self.state.start_time else None,
                'end_time': self.state.end_time.isoformat() if self.state.end_time else None
            }
            
            # 转换TaskResult对象
            for tr in self.state.task_results:
                tr_data = {
                    'task_name': tr.task_name,
                    'success': tr.success,
                    'start_time': tr.start_time.isoformat(),
                    'end_time': tr.end_time.isoformat() if tr.end_time else None,
                    'duration': tr.duration,
                    'error_message': tr.error_message,
                    'output_data': tr.output_data,
                    'checkpoint_data': tr.checkpoint_data
                }
                state_data['task_results'].append(tr_data)
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Workflow state saved to {self.state_file}")
        except Exception as e:
            logging.error(f"Failed to save state: {e}")
    
    def can_resume_from_step(self, step: int) -> bool:
        """检查是否可以从指定步骤恢复"""
        return step in self.state.completed_steps
    
    def mark_step_completed(self, step: int, result: TaskResult):
        """标记步骤完成"""
        if step not in self.state.completed_steps:
            self.state.completed_steps.append(step)
        
        # 移除失败记录（如果存在）
        if step in self.state.failed_steps:
            self.state.failed_steps.remove(step)
        
        # 更新任务结果
        self.state.task_results.append(result)
        self.save_state()
    
    def mark_step_failed(self, step: int, error_message: str):
        """标记步骤失败"""
        if step not in self.state.failed_steps:
            self.state.failed_steps.append(step)
        
        # 记录失败结果
        failed_result = TaskResult(
            task_name=f"Step_{step}",
            success=False,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration=0.0,
            error_message=error_message
        )
        self.state.task_results.append(failed_result)
        self.save_state()

class CacheManager:
    """缓存管理器 - 负责清理和分析相关的缓存"""
    
    def __init__(self, cache_base_dir: str = "./data/cache"):
        self.cache_base_dir = Path(cache_base_dir)
        self.cache_base_dir.mkdir(parents=True, exist_ok=True)
    
    def clear_all_cache(self) -> bool:
        """清理所有缓存文件"""
        try:
            if self.cache_base_dir.exists():
                import shutil
                shutil.rmtree(self.cache_base_dir)
                self.cache_base_dir.mkdir(parents=True, exist_ok=True)
                logging.info(f"Cleared all cache in {self.cache_base_dir}")
                return True
        except Exception as e:
            logging.error(f"Failed to clear cache: {e}")
            return False
    
    def clear_protein_specific_cache(self, protein_id: str) -> bool:
        """清理特定蛋白质的缓存"""
        try:
            # 清理与特定蛋白质相关的缓存文件
            cache_patterns = [
                f"*{protein_id}*",
                "sequence_cache.csv",
                "geo_cache.csv", 
                "hsd_cache.csv",
                "pdb_cache/*.pdb",
                "docking_logs/*.log",
                "conservation_results.csv",
                "binding_energy_chart.png",
                "conservation_heatmap.png"
            ]
            
            cleared_files = 0
            for pattern in cache_patterns:
                for file_path in self.cache_base_dir.glob(pattern):
                    if file_path.is_file():
                        file_path.unlink()
                        cleared_files += 1
                    elif file_path.is_dir():
                        import shutil
                        shutil.rmtree(file_path)
                        cleared_files += 1
            
            logging.info(f"Cleared {cleared_files} cache files for protein {protein_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to clear protein-specific cache: {e}")
            return False
    
    def clear_workflow_state(self) -> bool:
        """清理工作流状态文件"""
        try:
            state_files = [
                "workflow_state.json",
                "workflow_summary_report.txt",
                "workflow.log"
            ]
            
            for state_file in state_files:
                file_path = Path(state_file)
                if file_path.exists():
                    file_path.unlink()
                    logging.info(f"Cleared state file: {state_file}")
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to clear workflow state: {e}")
            return False

class EmailNotifier:
    """邮件通知系统"""
    
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config = self.load_config(config_file)
        self.smtp_config = self.config.get('email_notification', {})
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"Failed to load config file {config_file}: {e}")
            return {}
    
    def send_notification(self, subject: str, message: str, 
                         attachment_path: Optional[str] = None,
                         is_error: bool = False) -> bool:
        """发送邮件通知"""
        if not self.smtp_config.get('enabled', False):
            logging.info("Email notifications disabled")
            return True
        
        try:
            # 邮件配置
            smtp_server = self.smtp_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.smtp_config.get('smtp_port', 587)
            sender_email = self.smtp_config.get('sender_email')
            sender_password = self.smtp_config.get('sender_password')
            recipient_email = self.smtp_config.get('recipient_email')
            
            if not all([sender_email, sender_password, recipient_email]):
                logging.warning("Email configuration incomplete")
                return False
            
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # 邮件正文
            body = f"""
工作流通知 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{message}

---
此邮件由Prefect工作流系统自动发送
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 添加附件（如果有）
            if attachment_path and Path(attachment_path).exists():
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {Path(attachment_path).name}'
                    )
                    msg.attach(part)
            
            # 发送邮件
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, recipient_email, text)
            server.quit()
            
            logging.info(f"Email notification sent: {subject}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email notification: {e}")
            return False

# Prefect任务定义
@task(name="缓存清理", retries=1, retry_delay_seconds=10)
def task_cache_clearing(protein_id: str = None) -> TaskResult:
    """任务0：缓存清理（可选）"""
    logger = get_run_logger()
    start_time = datetime.now()
    
    try:
        logger.info("开始缓存清理任务...")
        
        cache_manager = CacheManager()
        
        if protein_id:
            # 清理特定蛋白质的缓存
            success = cache_manager.clear_protein_specific_cache(protein_id)
            logger.info(f"清理蛋白质 {protein_id} 的缓存: {'成功' if success else '失败'}")
        else:
            # 清理所有缓存
            success = cache_manager.clear_all_cache()
            logger.info(f"清理所有缓存: {'成功' if success else '失败'}")
        
        # 清理工作流状态
        state_cleared = cache_manager.clear_workflow_state()
        logger.info(f"清理工作流状态: {'成功' if state_cleared else '失败'}")
        
        logger.info("缓存清理完成")
        return TaskResult(
            task_name="缓存清理",
            success=True,
            start_time=start_time,
            end_time=datetime.now(),
            duration=(datetime.now() - start_time).total_seconds(),
            output_data={"cache_cleared": success, "state_cleared": state_cleared},
            checkpoint_data={"cache_cleared": success}
        )
            
    except Exception as e:
        logger.error(f"缓存清理失败: {str(e)}")
        return TaskResult(
            task_name="缓存清理",
            success=False,
            start_time=start_time,
            end_time=datetime.now(),
            duration=(datetime.now() - start_time).total_seconds(),
            error_message=str(e)
        )

@task(name="参数初始化", retries=2, retry_delay_seconds=30)
def task_parameter_initialization() -> TaskResult:
    """任务1：参数初始化"""
    logger = get_run_logger()
    start_time = datetime.now()
    
    try:
        logger.info("开始参数初始化任务...")
        
        # 检查配置文件是否存在
        config_file = Path(CONFIG_FILE)
        if not config_file.exists():
            logger.warning(f"配置文件 {CONFIG_FILE} 不存在，创建默认配置")
            # 创建默认配置
            default_config = {
                "target_protein": {
                    "name": "THBS4",
                    "structure_path": "./structures/thbs4.pdb"
                },
                "conservation_analysis": {
                    "target_species": {
                        "human": {"taxonomy_id": 9606, "scientific_name": "Homo sapiens"},
                        "mouse": {"taxonomy_id": 10090, "scientific_name": "Mus musculus"}
                    },
                    "conservation_threshold": 0.8
                },
                "docking": {
                    "box_size": [20, 20, 20],
                    "energy_threshold": -7.0,
                    "max_runs": 3
                },
                "paths": {
                    "cache_dir": "./cache",
                    "dump_dir": "./cache/docking_logs",
                    "receptor_cache_dir": "./cache/receptors"
                }
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        # 加载配置文件
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        logger.info("参数初始化完成")
        return TaskResult(
            task_name="参数初始化",
            success=True,
            start_time=start_time,
            end_time=datetime.now(),
            duration=(datetime.now() - start_time).total_seconds(),
            output_data={"config_file": str(config_file), "config_data": config_data},
            checkpoint_data={"config_file": str(config_file)}
        )
            
    except Exception as e:
        logger.error(f"参数初始化失败: {str(e)}")
        return TaskResult(
            task_name="参数初始化",
            success=False,
            start_time=start_time,
            end_time=datetime.now(),
            duration=(datetime.now() - start_time).total_seconds(),
            error_message=str(e)
        )

@task(name="数据拉取", retries=3, retry_delay_seconds=60)
def task_data_fetching(init_result: TaskResult, protein_id: str = None) -> TaskResult:
    """任务2：数据拉取"""
    logger = get_run_logger()
    start_time = datetime.now()
    
    try:
        logger.info("开始数据拉取任务...")
        
        # 使用健壮的数据获取器
        fetcher = DataFetcher(protein_id=protein_id, force_refresh=True)
        fetcher.run_all()
        
        logger.info("数据拉取完成")
        return TaskResult(
            task_name="数据拉取",
            success=True,
            start_time=start_time,
            end_time=datetime.now(),
            duration=(datetime.now() - start_time).total_seconds(),
            checkpoint_data={"cache_dir": "./cache"}
        )
        
    except Exception as e:
        logger.error(f"数据拉取失败: {str(e)}")
        return TaskResult(
            task_name="数据拉取",
            success=False,
            start_time=start_time,
            end_time=datetime.now(),
            duration=(datetime.now() - start_time).total_seconds(),
            error_message=str(e)
        )

@task(name="分泌路径分析", retries=2, retry_delay_seconds=45)
def task_secretion_analysis(fetch_result: TaskResult, protein_id: str = None) -> TaskResult:
    """任务3：分泌路径分析"""
    logger = get_run_logger()
    start_time = datetime.now()
    
    try:
        logger.info("开始分泌路径分析任务...")
        
        # 执行分泌路径分析
        # 从数据库获取蛋白质名称，优先使用传入的protein_id
        protein_name = "UnknownProtein"  # 默认值
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine('postgresql://postgres:password@localhost:5432/peptide_research')
            with engine.connect() as conn:
                if protein_id:
                    # 使用传入的protein_id查询
                    result = conn.execute(text('SELECT protein_name FROM target_proteins WHERE protein_id = :protein_id'), 
                                        {'protein_id': protein_id})
                else:
                    # 使用默认查询
                    result = conn.execute(text('SELECT protein_name FROM target_proteins LIMIT 1'))
                row = result.fetchone()
                if row and row[0]:
                    protein_name = row[0]
                else:
                    # 如果没有找到，使用protein_id作为名称
                    protein_name = protein_id or "UnknownProtein"
        except Exception as e:
            logger.warning(f"Failed to get protein name from database: {e}")
            protein_name = protein_id or "UnknownProtein"
        
        # 创建蛋白特定的输出目录
        protein_safe_name = "".join(c for c in protein_name if c.isalnum() or c == '_')
        output_base_dir = Path("output") / protein_safe_name
        output_base_dir.mkdir(parents=True, exist_ok=True)
        
        analyzer = SecretionAnalyzer(protein_name=protein_name)
        analysis_result = analyzer.run_full_analysis()
        
        logger.info("分泌路径分析完成")
        return TaskResult(
            task_name="分泌路径分析",
            success=True,
            start_time=start_time,
            end_time=datetime.now(),
            duration=(datetime.now() - start_time).total_seconds(),
            output_data=analysis_result,
            checkpoint_data={"secretion_analysis": "completed"}
        )
        
    except Exception as e:
        logger.error(f"分泌路径分析失败: {str(e)}")
        return TaskResult(
            task_name="分泌路径分析",
            success=False,
            start_time=start_time,
            end_time=datetime.now(),
            duration=(datetime.now() - start_time).total_seconds(),
            error_message=str(e)
        )

@task(name="STRING相互作用分析", retries=2, retry_delay_seconds=60)
def task_string_interaction_analysis(secretion_result: TaskResult, protein_id: str = None) -> TaskResult:
    """任务4：STRING相互作用分析"""
    logger = get_run_logger()
    start_time = datetime.now()
    
    try:
        logger.info("开始STRING相互作用分析任务...")
        
        # 导入STRING分析模块
        from step1_string_interaction import STRINGInteractionAnalysis
        
        # 创建配置
        config = {
            'target_protein_id': protein_id,
            'species_id': 9606,  # Homo sapiens
            'confidence_threshold': 0.9,
            'output_dir': 'cache'
        }
        
        # 初始化分析器
        analysis = STRINGInteractionAnalysis(config=config)
        
        # 运行分析
        receptor_candidates = analysis.analyze_interactions(confidence_threshold=0.9)
        
        if not receptor_candidates.empty:
            # 保存结果
            output_file = analysis.save_results(receptor_candidates, "string_receptors.csv")
            logger.info(f"STRING分析完成，识别出 {len(receptor_candidates)} 个潜在受体")
            logger.info(f"结果保存到: {output_file}")
            
            analysis_result = {
                "receptor_count": len(receptor_candidates),
                "output_file": output_file,
                "top_candidates": receptor_candidates.head(10).to_dict('records')
            }
        else:
            logger.warning("未识别出潜在受体")
            analysis_result = {
                "receptor_count": 0,
                "output_file": None,
                "top_candidates": []
            }
        
        return TaskResult(
            task_name="STRING相互作用分析",
            success=True,
            start_time=start_time,
            end_time=datetime.now(),
            duration=(datetime.now() - start_time).total_seconds(),
            output_data=analysis_result,
            checkpoint_data={"string_analysis": "completed"}
        )
        
    except Exception as e:
        logger.error(f"STRING相互作用分析失败: {str(e)}")
        return TaskResult(
            task_name="STRING相互作用分析",
            success=False,
            start_time=start_time,
            end_time=datetime.now(),
            duration=(datetime.now() - start_time).total_seconds(),
            error_message=str(e)
        )

@task(name="分子对接预测", retries=2, retry_delay_seconds=90)
def task_docking_prediction(string_result: TaskResult, protein_id: str = None) -> TaskResult:
    """任务5：分子对接预测"""
    logger = get_run_logger()
    start_time = datetime.now()
    
    try:
        logger.info("开始分子对接预测任务...")
        
        # 导入对接预测模块
        from step2_docking_prediction import AutoDockDockingPredictor
        
        # 初始化预测器
        predictor = AutoDockDockingPredictor()
        
        # 运行预测
        predictor.run_prediction("cache/string_receptors.csv")
        
        logger.info("分子对接预测完成")
        
        analysis_result = {
            "docking_completed": True,
            "receptor_file": "cache/string_receptors.csv",
            "results_file": "cache/docking_results.csv"
        }
        
        return TaskResult(
            task_name="分子对接预测",
            success=True,
            start_time=start_time,
            end_time=datetime.now(),
            duration=(datetime.now() - start_time).total_seconds(),
            output_data=analysis_result,
            checkpoint_data={"docking_prediction": "completed"}
        )
        
    except Exception as e:
        logger.error(f"分子对接预测失败: {str(e)}")
        return TaskResult(
            task_name="分子对接预测",
            success=False,
            start_time=start_time,
            end_time=datetime.now(),
            duration=(datetime.now() - start_time).total_seconds(),
            error_message=str(e)
        )

@task(name="肽段优化", retries=2, retry_delay_seconds=60)
def task_peptide_optimization(analysis_result: TaskResult) -> TaskResult:
    """任务4：肽段优化"""
    logger = get_run_logger()
    start_time = datetime.now()
    
    try:
        logger.info("开始肽段优化任务...")
        
        # 执行肽段优化
        optimizer = PeptideOptimizationPipeline()
        optimization_result = optimizer.optimize_peptides()
        
        logger.info("肽段优化完成")
        return TaskResult(
            task_name="肽段优化",
            success=True,
            start_time=start_time,
            end_time=datetime.now(),
            duration=(datetime.now() - start_time).total_seconds(),
            output_data=optimization_result,
            checkpoint_data={"optimized_peptides": "completed"}
        )
        
    except Exception as e:
        logger.error(f"肽段优化失败: {str(e)}")
        return TaskResult(
            task_name="肽段优化",
            success=False,
            start_time=start_time,
            end_time=datetime.now(),
            duration=(datetime.now() - start_time).total_seconds(),
            error_message=str(e)
        )

@task(name="可视化+报告生成", retries=1, retry_delay_seconds=30)
def task_visualization_reporting(optimization_result: TaskResult, protein_id: str = None) -> TaskResult:
    """任务5：可视化+报告生成"""
    logger = get_run_logger()
    start_time = datetime.now()
    
    try:
        logger.info("开始可视化和报告生成任务...")
        
        # 生成综合报告
        reporter = ReportGenerator(config_path="config/config.yaml")
        
        # 从数据库获取实际的蛋白质信息，优先使用传入的protein_id
        protein_name = "UnknownProtein"  # 默认值
        organism = "Unknown"  # 默认值
        
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine('postgresql://postgres:password@localhost:5432/peptide_research')
            with engine.connect() as conn:
                if protein_id:
                    # 使用传入的protein_id查询
                    result = conn.execute(text('SELECT protein_name, organism FROM target_proteins WHERE protein_id = :protein_id'), 
                                        {'protein_id': protein_id})
                else:
                    # 使用默认查询
                    result = conn.execute(text('SELECT protein_name, organism FROM target_proteins LIMIT 1'))
                row = result.fetchone()
                if row:
                    protein_name = row[0] or (protein_id or "UnknownProtein")
                    organism = row[1] or "Unknown"
                else:
                    protein_name = protein_id or "UnknownProtein"
        except Exception as e:
            logger.warning(f"Failed to get protein info from database: {e}")
            protein_name = protein_id or "UnknownProtein"
        
        report_result = reporter.generate_report(protein_name=protein_name, species_list=[organism])
        
        logger.info("可视化和报告生成完成")
        return TaskResult(
            task_name="可视化+报告生成",
            success=True,
            start_time=start_time,
            end_time=datetime.now(),
            duration=(datetime.now() - start_time).total_seconds(),
            output_data=report_result,
            checkpoint_data={"reports_generated": "completed"}
        )
        
    except Exception as e:
        logger.error(f"可视化和报告生成失败: {str(e)}")
        return TaskResult(
            task_name="可视化+报告生成",
            success=False,
            start_time=start_time,
            end_time=datetime.now(),
            duration=(datetime.now() - start_time).total_seconds(),
            error_message=str(e)
        )

@task(name="生成流程总结报告")
def task_generate_summary_report(all_results: List[TaskResult]) -> str:
    """生成流程总结报告"""
    logger = get_run_logger()
    
    try:
        logger.info("生成流程总结报告...")
        
        # 计算总体统计
        total_tasks = len(all_results)
        successful_tasks = sum(1 for r in all_results if r.success)
        failed_tasks = total_tasks - successful_tasks
        
        total_duration = sum(r.duration or 0 for r in all_results)
        
        # 生成报告内容
        report_content = f"""
肽段药物开发工作流执行总结报告
=====================================

执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
工作流ID: {os.getenv('PREFECT_FLOW_RUN_ID', 'N/A')}

总体统计
--------
总任务数: {total_tasks}
成功任务数: {successful_tasks}
失败任务数: {failed_tasks}
成功率: {(successful_tasks/total_tasks*100):.1f}%
总耗时: {total_duration:.2f} 秒 ({total_duration/60:.1f} 分钟)

详细任务执行情况
----------------
"""
        
        for i, result in enumerate(all_results, 1):
            status = "✅ 成功" if result.success else "❌ 失败"
            duration_str = f"{result.duration:.2f}秒" if result.duration else "N/A"
            
            report_content += f"""
任务 {i}: {result.task_name}
状态: {status}
开始时间: {result.start_time.strftime('%H:%M:%S')}
结束时间: {result.end_time.strftime('%H:%M:%S') if result.end_time else 'N/A'}
耗时: {duration_str}
"""
            
            if result.error_message:
                report_content += f"错误信息: {result.error_message}\n"
            
            if result.checkpoint_data:
                report_content += f"检查点数据: {json.dumps(result.checkpoint_data, ensure_ascii=False)}\n"
            
            report_content += "-" * 50 + "\n"
        
        # 失败任务分析
        if failed_tasks > 0:
            report_content += f"""
失败任务分析
------------
"""
            for result in all_results:
                if not result.success:
                    report_content += f"""
• {result.task_name}: {result.error_message}
"""
        
        # 建议和下一步
        report_content += f"""
建议和下一步
------------
"""
        if failed_tasks == 0:
            report_content += """
🎉 所有任务执行成功！

建议下一步操作：
1. 查看生成的报告文件
2. 分析优化后的肽段结果
3. 进行实验验证
4. 准备下一轮优化
"""
        else:
            report_content += f"""
⚠️ 发现 {failed_tasks} 个失败任务

建议操作：
1. 检查失败任务的错误信息
2. 修复相关问题后重新运行工作流
3. 使用断点续跑功能从失败步骤继续
4. 联系技术支持获取帮助

断点续跑命令：
python workflow.py --resume-from-step [失败步骤号]
"""
        
        # 保存报告到文件
        report_file = Path(SUMMARY_REPORT_FILE)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"流程总结报告已生成: {report_file}")
        
        # 创建Prefect artifact
        create_markdown_artifact(
            key="workflow-summary-report",
            markdown=report_content,
            description="肽段药物开发工作流执行总结报告"
        )
        
        return str(report_file)
        
    except Exception as e:
        logger.error(f"生成总结报告失败: {str(e)}")
        return ""

# 主工作流
@flow(name="肽段药物开发工作流", 
      task_runner=ConcurrentTaskRunner(),
      description="完整的肽段药物开发分析流程")
def peptide_drug_development_workflow(protein_id: str = None, resume_from_step: int = 1, 
                                      clear_cache: bool = True, species_list: List[str] = ["Human", "Mouse"]) -> Dict[str, Any]:
    """
    主工作流：肽段药物开发完整流程
    
    Args:
        protein_id: 蛋白质ID
        resume_from_step: 断点续跑起始步骤（1-5）
        clear_cache: 是否在开始前清理缓存
        species_list: 物种列表
    
    Returns:
        工作流执行结果
    """
    logger = get_run_logger()
    workflow_manager = WorkflowManager()
    email_notifier = EmailNotifier()
    
    # 初始化工作流状态
    if not workflow_manager.state.start_time:
        workflow_manager.state.start_time = datetime.now()
    
    logger.info(f"开始肽段药物开发工作流 (从步骤 {resume_from_step} 开始)")
    
    # 任务结果列表
    all_results = []
    
    # 缓存清理（如果需要）
    if clear_cache and resume_from_step == 1:
        logger.info("执行缓存清理...")
        cache_result = task_cache_clearing(protein_id=protein_id)
        all_results.append(cache_result)
        
        if not cache_result.success:
            logger.warning(f"缓存清理失败: {cache_result.error_message}")
        else:
            logger.info("缓存清理完成")
    
    try:
        # 任务1：参数初始化
        if resume_from_step <= 1:
            logger.info("执行任务1：参数初始化")
            init_result = task_parameter_initialization()
            all_results.append(init_result)
            
            if init_result.success:
                workflow_manager.mark_step_completed(1, init_result)
                logger.info("任务1完成：参数初始化")
            else:
                workflow_manager.mark_step_failed(1, init_result.error_message)
                raise Exception(f"任务1失败: {init_result.error_message}")
        else:
            logger.info("跳过任务1：参数初始化（断点续跑）")
        
        # 任务2：数据拉取
        if resume_from_step <= 2:
            logger.info("执行任务2：数据拉取")
            fetch_result = task_data_fetching(
                all_results[0] if all_results else TaskResult(
                    task_name="参数初始化", success=True, start_time=datetime.now()
                ),
                protein_id=protein_id
            )
            all_results.append(fetch_result)
            
            if fetch_result.success:
                workflow_manager.mark_step_completed(2, fetch_result)
                logger.info("任务2完成：数据拉取")
            else:
                workflow_manager.mark_step_failed(2, fetch_result.error_message)
                raise Exception(f"任务2失败: {fetch_result.error_message}")
        else:
            logger.info("跳过任务2：数据拉取（断点续跑）")
        
        # 任务3：分泌路径分析
        if resume_from_step <= 3:
            logger.info("执行任务3：分泌路径分析")
            secretion_result = task_secretion_analysis(
                all_results[1] if len(all_results) > 1 else TaskResult(
                    task_name="数据拉取", success=True, start_time=datetime.now()
                ),
                protein_id=protein_id
            )
            all_results.append(secretion_result)
            
            if secretion_result.success:
                workflow_manager.mark_step_completed(3, secretion_result)
                logger.info("任务3完成：分泌路径分析")
            else:
                workflow_manager.mark_step_failed(3, secretion_result.error_message)
                raise Exception(f"任务3失败: {secretion_result.error_message}")
        else:
            logger.info("跳过任务3：分泌路径分析（断点续跑）")
        
        # 任务4：STRING相互作用分析
        if resume_from_step <= 4:
            logger.info("执行任务4：STRING相互作用分析")
            string_result = task_string_interaction_analysis(
                all_results[2] if len(all_results) > 2 else TaskResult(
                    task_name="分泌路径分析", success=True, start_time=datetime.now()
                ),
                protein_id=protein_id
            )
            all_results.append(string_result)
            
            if string_result.success:
                workflow_manager.mark_step_completed(4, string_result)
                logger.info("任务4完成：STRING相互作用分析")
            else:
                workflow_manager.mark_step_failed(4, string_result.error_message)
                raise Exception(f"任务4失败: {string_result.error_message}")
        else:
            logger.info("跳过任务4：STRING相互作用分析（断点续跑）")
        
        # 任务5：分子对接预测
        if resume_from_step <= 5:
            logger.info("执行任务5：分子对接预测")
            docking_result = task_docking_prediction(
                all_results[3] if len(all_results) > 3 else TaskResult(
                    task_name="STRING相互作用分析", success=True, start_time=datetime.now()
                ),
                protein_id=protein_id
            )
            all_results.append(docking_result)
            
            if docking_result.success:
                workflow_manager.mark_step_completed(5, docking_result)
                logger.info("任务5完成：分子对接预测")
            else:
                workflow_manager.mark_step_failed(5, docking_result.error_message)
                raise Exception(f"任务5失败: {docking_result.error_message}")
        else:
            logger.info("跳过任务5：分子对接预测（断点续跑）")
        
        # 任务6：肽段优化
        if resume_from_step <= 6:
            logger.info("执行任务6：肽段优化")
            optimization_result = task_peptide_optimization(all_results[4] if len(all_results) > 4 else TaskResult(
                task_name="分子对接预测", success=True, start_time=datetime.now()
            ))
            all_results.append(optimization_result)
            
            if optimization_result.success:
                workflow_manager.mark_step_completed(6, optimization_result)
                logger.info("任务6完成：肽段优化")
            else:
                workflow_manager.mark_step_failed(6, optimization_result.error_message)
                raise Exception(f"任务6失败: {optimization_result.error_message}")
        else:
            logger.info("跳过任务6：肽段优化（断点续跑）")
        
        # 任务7：可视化+报告生成
        if resume_from_step <= 7:
            logger.info("执行任务7：可视化+报告生成")
            report_result = task_visualization_reporting(
                all_results[5] if len(all_results) > 5 else TaskResult(
                    task_name="肽段优化", success=True, start_time=datetime.now()
                ),
                protein_id=protein_id
            )
            all_results.append(report_result)
            
            if report_result.success:
                workflow_manager.mark_step_completed(7, report_result)
                logger.info("任务7完成：可视化+报告生成")
            else:
                workflow_manager.mark_step_failed(7, report_result.error_message)
                raise Exception(f"任务7失败: {report_result.error_message}")
        else:
            logger.info("跳过任务7：可视化+报告生成（断点续跑）")
        
        # 生成总结报告
        logger.info("生成流程总结报告")
        summary_report = task_generate_summary_report(all_results)
        
        # 更新工作流状态
        workflow_manager.state.end_time = datetime.now()
        workflow_manager.save_state()
        
        # 发送成功通知
        success_message = f"""
工作流执行成功完成！

执行统计：
- 总任务数: {len(all_results)}
- 成功任务数: {sum(1 for r in all_results if r.success)}
- 总耗时: {(workflow_manager.state.end_time - workflow_manager.state.start_time).total_seconds():.2f} 秒

总结报告已生成: {summary_report}
        """
        
        email_notifier.send_notification(
            subject="肽段药物开发工作流执行成功",
            message=success_message,
            attachment_path=summary_report
        )
        
        logger.info("工作流执行成功完成")
        
        return {
            "success": True,
            "total_tasks": len(all_results),
            "successful_tasks": sum(1 for r in all_results if r.success),
            "failed_tasks": sum(1 for r in all_results if not r.success),
            "total_duration": (workflow_manager.state.end_time - workflow_manager.state.start_time).total_seconds(),
            "summary_report": summary_report,
            "task_results": all_results
        }
        
    except Exception as e:
        logger.error(f"工作流执行失败: {str(e)}")
        
        # 发送失败通知
        error_message = f"""
工作流执行失败！

错误信息: {str(e)}
失败时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

请检查日志文件并修复问题后重新运行。
        """
        
        email_notifier.send_notification(
            subject="肽段药物开发工作流执行失败",
            message=error_message,
            is_error=True
        )
        
        # 更新失败状态
        workflow_manager.state.end_time = datetime.now()
        workflow_manager.save_state()
        
        raise e

# 断点续跑功能
def resume_workflow_from_step(step: int, protein_id: str = None):
    """从指定步骤恢复工作流"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"从步骤 {step} 恢复工作流...")
        
        # 验证步骤号
        if not 1 <= step <= 5:
            raise ValueError("步骤号必须在1-5之间")
        
        # 执行工作流
        result = peptide_drug_development_workflow(protein_id=protein_id, resume_from_step=step)
        
        logger.info("工作流恢复执行完成")
        return result
        
    except Exception as e:
        logger.error(f"工作流恢复失败: {str(e)}")
        raise e

# 部署配置
def create_deployment():
    """创建Prefect部署 - 使用现代Prefect方法"""
    # 使用flow.serve()方法创建部署
    peptide_drug_development_workflow.serve(
        name="peptide-drug-development",
        version="1.0.0",
        description="肽段药物开发完整工作流",
        tags=["peptide", "drug-development", "bioinformatics"],
        parameters={"resume_from_step": 1}
    )
    return "Deployment created successfully"

# 命令行接口
def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="肽段药物开发Prefect工作流")
    parser.add_argument("--protein-id", type=str, 
                       help="蛋白质ID")
    parser.add_argument("--species", type=str, 
                       help="物种列表 (逗号分隔，如: Human,Mouse,Rat)")
    parser.add_argument("--resume-from-step", type=int, default=1, 
                       help="断点续跑起始步骤 (1-5)")
    parser.add_argument("--clear-cache", action="store_true", default=True,
                       help="在开始前清理缓存")
    parser.add_argument("--no-clear-cache", action="store_true",
                       help="跳过缓存清理")
    parser.add_argument("--deploy", action="store_true", 
                       help="创建Prefect部署")
    parser.add_argument("--config", type=str, default=CONFIG_FILE,
                       help="配置文件路径")
    
    args = parser.parse_args()
    
    # 处理缓存清理参数
    clear_cache = args.clear_cache and not args.no_clear_cache
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('workflow.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    try:
        if args.deploy:
            # 创建部署
            logging.info("创建Prefect部署...")
            result = create_deployment()
            logging.info(f"部署创建成功: {result}")
        else:
            # 解析物种列表
            species_list = None
            if args.species:
                species_list = [s.strip() for s in args.species.split(',')]
                logging.info(f"指定物种: {species_list}")
            
            # 执行工作流
            if args.resume_from_step > 1:
                logging.info(f"断点续跑模式：从步骤 {args.resume_from_step} 开始")
                result = resume_workflow_from_step(args.resume_from_step, args.protein_id)
            else:
                logging.info("正常执行模式")
                result = peptide_drug_development_workflow(
                    protein_id=args.protein_id, 
                    clear_cache=clear_cache,
                    species_list=species_list
                )
            
            # 输出结果
            print(f"\n工作流执行完成!")
            print(f"成功任务数: {result['successful_tasks']}/{result['total_tasks']}")
            print(f"总耗时: {result['total_duration']:.2f} 秒")
            print(f"总结报告: {result['summary_report']}")
            
    except Exception as e:
        logging.error(f"执行失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
