#!/usr/bin/env python3
"""
AI-Drug Peptide - 主入口文件
整合所有核心模块，提供统一的应用程序接口
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# 导入核心模块
from core import (
    DataManager,
    AnalysisEngine,
    WorkflowOrchestrator,
    ReportGeneratorFactory,
    ToolFactory
)

# 设置日志
def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """设置日志配置"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )

def load_config(config_path: Path) -> Dict[str, Any]:
    """加载配置文件"""
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_default_config() -> Dict[str, Any]:
    """创建默认配置"""
    return {
        "paths": {
            "cache_dir": "./data/cache",
            "output_dir": "./data/output",
            "temp_dir": "./data/temp",
            "log_dir": "./logs"
        },
        "database": {
            "postgresql": {
                "host": "localhost",
                "port": 5432,
                "database": "peptide_research",
                "user": "postgres",
                "password": "password"
            },
            "neo4j": {
                "uri": "bolt://localhost:7687",
                "user": "neo4j",
                "password": "password"
            }
        },
        "analysis": {
            "string": {
                "confidence_threshold": 0.9,
                "max_interactions": 100
            },
            "docking": {
                "energy_threshold": -7.0,
                "exhaustiveness": 8
            },
            "conservation": {
                "conservation_threshold": 0.8,
                "min_species": 3
            }
        },
        "tools": {
            "blast": {
                "command": "blastp",
                "version": "2.13.0+",
                "required": True
            },
            "clustalw": {
                "command": "clustalw",
                "version": "2.1",
                "required": False
            },
            "vina": {
                "command": "vina",
                "version": "1.2.3",
                "required": False
            }
        },
        "network": {
            "max_retries": 3,
            "timeout": 30,
            "user_agent": "AI-Drug-Peptide/1.0"
        },
        "logging": {
            "level": "INFO",
            "file": "app.log"
        }
    }

def save_config(config: Dict[str, Any], config_path: Path):
    """保存配置文件"""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def check_environment(config: Dict[str, Any]) -> bool:
    """检查环境配置"""
    logger = logging.getLogger(__name__)
    
    # 检查工具可用性
    tool_manager = ToolFactory.create_tool_manager(config)
    required_tools = tool_manager.get_required_tools_status()
    
    missing_tools = [tool for tool, available in required_tools.items() if not available]
    if missing_tools:
        logger.warning(f"Missing required tools: {missing_tools}")
        logger.warning("Some features may not work properly")
    
    # 检查目录权限
    paths = config.get('paths', {})
    for path_name, path_value in paths.items():
        path = Path(path_value)
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ {path_name} directory: {path}")
        except Exception as e:
            logger.error(f"✗ Cannot create {path_name} directory {path}: {e}")
            return False
    
    return True

def run_analysis(config: Dict[str, Any], protein_id: str, 
                analysis_steps: list, start_step: Optional[str] = None,
                species_list: Optional[list] = None):
    """运行分析流程"""
    logger = logging.getLogger(__name__)
    
    try:
        # 处理物种列表
        if species_list:
            logger.info(f"指定物种: {species_list}")
            # 这里可以添加物种验证逻辑
            # from bin.species_mapping import validate_species_list
            # valid_species, invalid_species = validate_species_list(species_list)
            # if invalid_species:
            #     logger.warning(f"无效物种: {invalid_species}")
        
        # 初始化核心组件
        logger.info("Initializing core components...")
        data_manager = DataManager(config)
        analysis_engine = AnalysisEngine(config, data_manager)
        orchestrator = WorkflowOrchestrator(config, analysis_engine)
        
        # 注册分析模块（这里需要根据实际模块进行调整）
        logger.info("Registering analysis modules...")
        # TODO: 注册实际的分析模块
        # analysis_engine.register_module("string_interaction", StringInteractionModule(config, data_manager))
        # analysis_engine.register_module("docking", DockingModule(config, data_manager))
        # analysis_engine.register_module("conservation", ConservationModule(config, data_manager))
        
        # 定义工作流步骤
        logger.info("Defining workflow steps...")
        orchestrator.add_step("step1_init", "parameter_initialization")
        orchestrator.add_step("step2_string", "string_interaction", dependencies=["step1_init"])
        orchestrator.add_step("step3_docking", "docking_analysis", dependencies=["step2_string"])
        orchestrator.add_step("step4_conservation", "conservation_analysis", dependencies=["step3_docking"])
        orchestrator.add_step("step5_report", "report_generation", dependencies=["step4_conservation"])
        
        # 运行工作流
        logger.info(f"Starting analysis for protein: {protein_id}")
        success = orchestrator.run_workflow(start_step=start_step)
        
        if success:
            logger.info("✓ Analysis completed successfully")
            
            # 生成报告
            logger.info("Generating reports...")
            report_generator = ReportGeneratorFactory.create_generator(config)
            
            # 模拟报告生成（需要实际的分析结果）
            mock_results = {
                'string_analysis': {'total_interactions': 5, 'confidence_scores': [0.95, 0.88, 0.82]},
                'docking_analysis': [{'receptor_id': 'EGFR', 'binding_energy': -8.5}],
                'conservation_analysis': {'avg_conservation': 0.85, 'is_conservative': True}
            }
            
            # 创建模拟请求对象
            class MockRequest:
                def __init__(self):
                    self.protein_id = protein_id
                    self.analysis_steps = analysis_steps
                    self.species_id = 9606
                    self.confidence_threshold = config['analysis']['string']['confidence_threshold']
                    self.energy_threshold = config['analysis']['docking']['energy_threshold']
                    self.conservation_threshold = config['analysis']['conservation']['conservation_threshold']
                    self.target_species = ['human', 'mouse']
            
            mock_request = MockRequest()
            
            # 生成报告（异步调用）
            import asyncio
            report_files = asyncio.run(report_generator.generate_report(mock_request, mock_results))
            
            logger.info("Report files generated:")
            for format_type, file_path in report_files.items():
                logger.info(f"  {format_type.upper()}: {file_path}")
            
        else:
            logger.error("✗ Analysis failed")
            return False
            
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        return False
    
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AI-Drug Peptide Development Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 使用默认配置运行完整分析
  python main.py --protein-id THBS4
  
  # 使用自定义配置文件和多物种分析
  python main.py --config config.json --protein-id THBS4 --species "Human,Mouse,Rat"
  
  # 从特定步骤开始运行
  python main.py --protein-id THBS4 --start-step step3_docking --species "Human,Mouse"
  
  # 只运行特定分析步骤
  python main.py --protein-id THBS4 --steps string docking --species "Human"
  
  # 创建默认配置文件
  python main.py --create-config
        """
    )
    
    parser.add_argument(
        "--config", 
        type=Path, 
        default=Path("config/config.json"),
        help="Path to configuration file"
    )
    parser.add_argument(
        "--protein-id", 
        type=str,
        help="Protein ID to analyze"
    )
    parser.add_argument(
        "--species", 
        type=str,
        help="Species list (comma-separated, e.g., 'Human,Mouse,Rat')"
    )
    parser.add_argument(
        "--steps", 
        nargs="+",
        choices=["string", "docking", "conservation", "secretion"],
        default=["string", "docking", "conservation"],
        help="Analysis steps to run"
    )
    parser.add_argument(
        "--start-step", 
        type=str,
        help="Start workflow from specific step"
    )
    parser.add_argument(
        "--create-config", 
        action="store_true",
        help="Create default configuration file"
    )
    parser.add_argument(
        "--log-level", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    parser.add_argument(
        "--log-file", 
        type=str,
        help="Log file path"
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger(__name__)
    
    try:
        # 创建默认配置文件
        if args.create_config:
            config = create_default_config()
            save_config(config, args.config)
            logger.info(f"✓ Default configuration saved to: {args.config}")
            return 0
        
        # 加载配置
        if not args.config.exists():
            logger.error(f"Configuration file not found: {args.config}")
            logger.info("Use --create-config to create a default configuration file")
            return 1
        
        config = load_config(args.config)
        logger.info(f"✓ Configuration loaded from: {args.config}")
        
        # 检查环境
        if not check_environment(config):
            logger.error("Environment check failed")
            return 1
        
        # 检查必需参数
        if not args.protein_id:
            logger.error("Protein ID is required")
            parser.print_help()
            return 1
        
        # 解析物种列表
        species_list = None
        if args.species:
            species_list = [s.strip() for s in args.species.split(',')]
            logger.info(f"指定物种: {species_list}")
        
        # 运行分析
        success = run_analysis(config, args.protein_id, args.steps, args.start_step, species_list)
        
        if success:
            logger.info("✓ Pipeline completed successfully")
            return 0
        else:
            logger.error("✗ Pipeline failed")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        return 130
    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())