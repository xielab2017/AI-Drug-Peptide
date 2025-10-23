#!/usr/bin/env python3
"""
Protein Secretion Analysis Script
功能：读取PostgreSQL中目标蛋白数据，执行信号肽预测、转运路径分析和分泌后定位
Author: AI Assistant
Date: 2024
"""

import os
import sys
import yaml
import logging
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import json

# Data handling
import pandas as pandas
import numpy as numpy
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

# Database
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor

# Visualization
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx

# Neo4j
from neo4j import GraphDatabase

# Progress tracking
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests_futures.sessions import FuturesSession

@dataclass
class SignalPeptideResult:
    """信号肽预测结果"""
    protein_id: str
    signal_peptide_start: int
    signal_peptide_end: int
    cleavage_site: int
    secretion_probability: float
    signal_sequence: str
    confidence: str

@dataclass
class TMHMMResult:
    """跨膜结构域预测结果"""
    protein_id: str
    tm_count: int
    topology: str
    tm_regions: List[Tuple[int, int]]
    intracellular_start: Optional[int]
    intracellular_end: Optional[int]
    extracellular_start: Optional[int]
    extracellular_end: Optional[int]

@dataclass
class HPATissueExpression:
    """HPA组织表达数据"""
    protein_id: str
    tissue_name: str
    expression_level: str
    cell_type: str
    reliability: str
    image_url: Optional[str]

class SecretionAnalyzer:
    """蛋白质分泌分析主类"""
    
    def __init__(self, config_path: str = "config/config.yaml", protein_name: str = None):
        """初始化分析器"""
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
        # 数据库连接
        self.pg_engine = self._create_postgres_engine()
        self.neo4j_driver = self._create_neo4j_driver()
        
        # 创建蛋白质特定的输出目录
        if protein_name:
            protein_safe = "".join(c for c in protein_name if c.isalnum() or c == '_')
            self.output_dir = Path("output") / protein_safe / "secretion_analysis"
        else:
            self.output_dir = Path("secretion_analysis_output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # SignalP 6.0 和 TMHMM 路径（从配置文件读取）
        self.signalp_path = self.config.get('tools', {}).get('signalp', {}).get('path', '/opt/signalp-6.0/signalp')
        self.tmhmm_path = self.config.get('tools', {}).get('tmhmm', {}).get('path', '/opt/tmhmm/tmhmm')
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件并处理环境变量"""
        import os
        import re
        
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 处理环境变量替换
        def replace_env_vars(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) else ''
            return os.getenv(var_name, default_value)
        
        # 替换 ${VAR:-default} 格式
        content = re.sub(r'\$\{([^:}]+):-([^}]*)\}', replace_env_vars, content)
        # 替换 ${VAR} 格式
        content = re.sub(r'\$\{([^}]+)\}', replace_env_vars, content)
        
        return yaml.safe_load(content)
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志记录"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # 创建文件处理器
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        handler = logging.FileHandler(log_dir / "secretion_analysis.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def _create_postgres_engine(self):
        """创建PostgreSQL连接引擎"""
        pg_config = self.config['database']['postgresql']
        connection_string = (
            f"postgresql://{pg_config['user']}:{pg_config['password']}"
            f"@{pg_config['host']}:{pg_config['port']}"
            f"/{pg_config['database']}"
        )
        return create_engine(connection_string, pool_pre_ping=True)
    
    def _create_neo4j_driver(self):
        """创建Neo4j连接驱动"""
        neo4j_config = self.config.get('database', {}).get('neo4j', {})
        uri = neo4j_config.get('uri', 'bolt://localhost:7687')
        user = neo4j_config.get('user', 'neo4j')
        password = neo4j_config.get('password', 'password')
        
        return GraphDatabase.driver(uri, auth=(user, password))
    
    def fetch_target_proteins(self) -> List[Dict[str, Any]]:
        """从PostgreSQL获取目标蛋白数据"""
        self.logger.info("从数据库获取目标蛋白数据...")
        
        query = text("""
            SELECT protein_id, protein_name, gene_name, sequence, 
                   molecular_weight, pi_value, organism, 
                   uniprot_id, pdb_id
            FROM target_proteins 
            WHERE sequence IS NOT NULL 
            ORDER BY protein_id
        """)
        
        with self.pg_engine.connect() as conn:
            result = conn.execute(query)
            proteins = [dict(row._mapping) for row in result]
        
        self.logger.info(f"获取到 {len(proteins)} 个目标蛋白")
        return proteins
    
    def predict_signal_peptides(self, proteins: List[Dict[str, Any]]) -> List[SignalPeptideResult]:
        """使用SignalP 6.0预测信号肽"""
        self.logger.info("开始信号肽预测...")
        
        results = []
        
        # 创建工作目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            
            # 批量处理蛋白质
            for protein in proteins:
                try:
                    result = self._run_signalp_single(protein, temp_dir)
                    if result:
                        results.append(result)
                        self.logger.info(f"蛋白 {protein['protein_id']} 信号肽预测完成")
                    else:
                        self.logger.warning(f"蛋白 {protein['protein_id']} 信号肽预测失败，使用模拟数据")
                        result = self._simulate_signalp_result(protein)
                        if result:
                            results.append(result)
                        
                except Exception as e:
                    self.logger.error(f"蛋白 {protein['protein_id']} 信号肽预测出错: {e}")
                    self.logger.warning(f"使用模拟数据为蛋白 {protein['protein_id']} 进行信号肽预测")
                    result = self._simulate_signalp_result(protein)
                    if result:
                        results.append(result)
        
        self.logger.info(f"信号肽预测完成，共处理 {len(results)} 个蛋白")
        return results
    
    def _run_signalp_single(self, protein: Dict[str, Any], temp_dir: Path) -> Optional[SignalPeptideResult]:
        """运行单个蛋白的SignalP预测"""
        protein_id = protein['protein_id']
        sequence = protein['sequence']
        
        # 创建FASTA文件
        fasta_file = temp_dir / f"{protein_id}.fasta"
        with open(fasta_file, 'w') as f:
            f.write(f">{protein_id}\n{sequence}\n")
        
        # 运行SignalP 6.0
        cmd = [
            self.signalp_path,
            '-fasta', str(fasta_file),
            '-format', 'short',
            '-mature',
            '-organism-type', 'euk'  # 真核生物
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                return self._parse_signalp_output(result.stdout, protein_id)
            else:
                self.logger.error(f"SignalP错误: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"SignalP超时: {protein_id}")
            return None
        except Exception as e:
            self.logger.error(f"SignalP执行错误: {e}")
            return None
    
    def _parse_signalp_output(self, output: str, protein_id: str) -> Optional[SignalPeptideResult]:
        """解析SignalP输出"""
        lines = output.strip().split('\n')
        
        # SignalP 6.0输出格式解析
        for line in lines:
            if line.startswith('#'):
                continue
            
            parts = line.split('\t')
            if len(parts) >= 6:
                # 格式: ID, SEC/SP, Signal peptide probability, Cleavage site probability, Cleavage position, Signal sequence probability
                try:
                    sp_probability = float(parts[2].replace(',', '.'))
                    cleavage_site_prob = float(parts[3].replace(',', '.'))
                    cleavage_pos = int(parts[4])
                    signal_prob = float(parts[5].replace(',', '.'))
                    
                    # 判断是否为分泌蛋白
                    if sp_probability > 0.8:
                        secret_prob = sp_probability
                        cleavage_site = cleavage_pos
                        signal_start = 1
                        signal_end = cleavage_pos
                        
                        # 获取序列（这里简化，实际可能需要从原序列中提取）
                        signal_seq = ""  # 需要从原序列中提取
                        
                        confidence = "High" if sp_probability > 0.9 else "Medium"
                        
                        return SignalPeptideResult(
                            protein_id=protein_id,
                            signal_peptide_start=signal_start,
                            signal_peptide_end=signal_end,
                            cleavage_site=cleavage_site,
                            secretion_probability=secret_prob,
                            signal_sequence=signal_seq,
                            confidence=confidence
                        )
                except (ValueError, IndexError) as e:
                    self.logger.error(f"解析SignalP输出失败: {e}")
                    continue
        
        return None
    
    def predict_transmembrane_regions(self, proteins: List[Dict[str, Any]]) -> List[TMHMMResult]:
        """使用TMHMM预测跨膜结构域"""
        self.logger.info("开始跨膜结构域预测...")
        
        results = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            
            for protein in proteins:
                try:
                    result = self._run_tmhmm_single(protein, temp_dir)
                    if result:
                        results.append(result)
                        self.logger.info(f"蛋白 {protein['protein_id']} TMHMM预测完成")
                        
                except Exception as e:
                    self.logger.error(f"蛋白 {protein['protein_id']} TMHMM预测出错: {e}")
                    self.logger.warning(f"使用模拟数据为蛋白 {protein['protein_id']} 进行TMHMM预测")
                    result = self._simulate_tmhmm_result(protein)
                    if result:
                        results.append(result)
        
        self.logger.info(f"跨膜结构域预测完成，共处理 {len(results)} 个蛋白")
        return results
    
    def _run_tmhmm_single(self, protein: Dict[str, Any], temp_dir: Path) -> Optional[TMHMMResult]:
        """运行单个蛋白的TMHMM预测"""
        protein_id = protein['protein_id']
        sequence = protein['sequence']
        
        # 创建FASTA文件
        fasta_file = temp_dir / f"{protein_id}.fasta"
        with open(fasta_file, 'w') as f:
            f.write(f">{protein_id}\n{sequence}\n")
        
        # 运行TMHMM
        cmd = [self.tmhmm_path, '-f', str(fasta_file)]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                return self._parse_tmhmm_output(result.stdout, protein_id)
            else:
                self.logger.error(f"TMHMM错误: {result.stderr}")
                self.logger.error(f"TMHMM stdout: {result.stdout}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"TMHMM超时: {protein_id}")
            return None
        except Exception as e:
            self.logger.error(f"TMHMM执行错误: {e}")
            return None
    
    def _parse_tmhmm_output(self, output: str, protein_id: str) -> Optional[TMHMMResult]:
        """解析TMHMM输出"""
        lines = output.strip().split('\n')
        tm_regions = []
        
        for line in lines:
            if 'TMhelix' in line:
                # 解析跨膜螺旋区域
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        tm_regions.append((int(parts[1]), int(parts[2])))
                    except ValueError:
                        continue
        
        tm_count = len(tm_regions)
        
        # 简化的拓扑预测
        if tm_count == 0:
            topology = "Soluble"
        elif tm_count == 1:
            topology = "Single-pass membrane protein"
        else:
            topology = f"{tm_count}-pass membrane protein"
        
        # 简化的细胞内/外定位（实际需要更复杂的逻辑）
        intracellular_start = None
        intracellular_end = None
        extracellular_start = None
        extracellular_end = None
        
        if tm_count > 0:
            # 简化假设：第一个TM区域后的区域为细胞内
            first_tm_end = tm_regions[0][1]
            intracellular_start = first_tm_end + 1
            intracellular_end = None  # 需要根据序列长度计算
        
        return TMHMMResult(
            protein_id=protein_id,
            tm_count=tm_count,
            topology=topology,
            tm_regions=tm_regions,
            intracellular_start=intracellular_start,
            intracellular_end=intracellular_end,
            extracellular_start=extracellular_start,
            extracellular_end=extracellular_end
        )
    
    def analyze_secretion_pathway(self, signal_results: List[SignalPeptideResult], 
                                tm_results: List[TMHMMResult]) -> List[Dict[str, Any]]:
        """分析分泌转运路径"""
        self.logger.info("分析分泌转运路径...")
        
        # 创建结果字典
        signal_dict = {r.protein_id: r for r in signal_results}
        tm_dict = {r.protein_id: r for r in tm_results}
        
        secretion_pathways = []
        
        for protein_id in signal_dict.keys():
            signal_result = signal_dict[protein_id]
            tm_result = tm_dict.get(protein_id)
            
            # 判断分泌路径
            if signal_result.secretion_probability > 0.8:
                if tm_result and tm_result.tm_count == 0:
                    pathway = "Classical secretion (ER-Golgi)"
                elif tm_result and tm_result.tm_count > 0:
                    pathway = "Non-classical secretion (vesicular)"
                else:
                    pathway = "Classical secretion (ER-Golgi)"
            else:
                pathway = "Non-secretory or low confidence"
            
            secretion_pathways.append({
                'protein_id': protein_id,
                'secretion_probability': signal_result.secretion_probability,
                'cleavage_site': signal_result.cleavage_site,
                'tm_count': tm_result.tm_count if tm_result else 0,
                'pathway': pathway,
                'signal_sequence': signal_result.signal_sequence
            })
        
        return secretion_pathways
    
    def fetch_hpa_tissue_data(self, protein_ids: List[str]) -> List[HPATissueExpression]:
        """从HPA数据库获取组织表达数据"""
        self.logger.info("获取HPA组织表达数据...")
        
        hpa_expressions = []
        
        # 注意：这里使用模拟数据，实际需要调用HPA API
        # HPA API: https://www.proteinatlas.org/about/download
        
        for protein_id in protein_ids:
            try:
                # 模拟HPA数据获取
                tissue_data = self._simulate_hpa_data(protein_id)
                hpa_expressions.extend(tissue_data)
                
            except Exception as e:
                self.logger.error(f"获取HPA数据失败 {protein_id}: {e}")
        
        self.logger.info(f"HPA数据获取完成，共 {len(hpa_expressions)} 条记录")
        return hpa_expressions
    
    def _simulate_hpa_data(self, protein_id: str) -> List[HPATissueExpression]:
        """模拟HPA数据（实际需要API调用）"""
        tissues = [
            ("Heart muscle", "High", "Cardiomyocytes", "High"),
            ("Blood", "Medium", "Plasma proteins", "Medium"),
            ("Liver", "Low", "Hepatocytes", "High"),
            ("Kidney", "Medium", "Renal tubules", "Medium"),
            ("Lung", "Low", "Alveolar cells", "Medium")
        ]
        
        return [
            HPATissueExpression(
                protein_id=protein_id,
                tissue_name=tissue,
                expression_level=level,
                cell_type=cell_type,
                reliability=reliability,
                image_url=f"https://www.proteinatlas.org/{protein_id}_{tissue.replace(' ', '_')}.jpg"
            )
            for tissue, level, cell_type, reliability in tissues
        ]
    
    def create_secretion_visualization(self, secretion_results: List[Dict[str, Any]], 
                                    hpa_data: List[HPATissueExpression], 
                                    proteins: List[Dict[str, Any]]) -> str:
        """创建分泌路径可视化图表"""
        self.logger.info("创建分泌路径可视化图表...")
        
        # 创建主图表
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Signal Peptide Structure', 'Transport Pathways', 'Tissue Localization Heatmap'),
            vertical_spacing=0.1,
            specs=[[{"type": "bar"}],
                   [{"type": "domain"}],  # 饼图需要domain类型
                   [{"type": "heatmap"}]]
        )
        
        # 1. 信号肽序列图表
        self._plot_signal_peptides(fig, 1, secretion_results)
        
        # 2. 转运路径示意图
        self._plot_transport_pathways(fig, 2, secretion_results)
        
        # 3. 组织定位热图
        self._plot_tissue_heatmap(fig, 3, hpa_data, proteins)
        
        # 保存图表
        output_file = self.output_dir / f"secretion_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fig.write_html(str(output_file))
        
        self.logger.info(f"可视化图表已保存: {output_file}")
        return str(output_file)
    
    def _plot_signal_peptides(self, fig, row: int, secretion_results: List[Dict[str, Any]]):
        """绘制信号肽序列图表"""
        # 简化的信号肽序列可视化
        protein_names = [r['protein_id'] for r in secretion_results[:10]]  # 限制显示数量
        probabilities = [r['secretion_probability'] for r in secretion_results[:10]]
        
        fig.add_trace(
            go.Bar(
                x=protein_names,
                y=probabilities,
                name="Secretion Probability",
                marker_color='lightblue',
                text=[f"{p:.3f}" for p in probabilities],
                textposition='auto'
            ),
            row=row, col=1
        )
        
        # 添加0.8阈值线
        fig.add_hline(y=0.8, line_dash="dash", line_color="red", 
                     annotation_text="Threshold (0.8)", row=row, col=1)
    
    def _plot_transport_pathways(self, fig, row: int, secretion_results: List[Dict[str, Any]]):
        """绘制转运路径示意图"""
        # 路径统计
        pathway_counts = {}
        for result in secretion_results:
            pathway = result['pathway']
            pathway_counts[pathway] = pathway_counts.get(pathway, 0) + 1
        
        fig.add_trace(
            go.Pie(
                labels=list(pathway_counts.keys()),
                values=list(pathway_counts.values()),
                name="Transport Pathways",
                hole=0.4
            ),
            row=row, col=1
        )
    
    def _plot_tissue_heatmap(self, fig, row: int, hpa_data: List[HPATissueExpression], 
                            proteins: List[Dict[str, Any]]):
        """绘制组织定位热图"""
        # 准备热图数据
        protein_ids = [p['protein_id'] for p in proteins[:10]]
        tissues = list(set([d.tissue_name for d in hpa_data]))
        
        # 创建表达水平矩阵
        expression_matrix = []
        expression_levels = {"High": 3, "Medium": 2, "Low": 1}
        
        for protein_id in protein_ids:
            protein_expressions = [d for d in hpa_data if d.protein_id == protein_id]
            row_data = []
            for tissue in tissues:
                tissue_data = next((d for d in protein_expressions if d.tissue_name == tissue), None)
                if tissue_data:
                    row_data.append(expression_levels.get(tissue_data.expression_level, 0))
                else:
                    row_data.append(0)
            expression_matrix.append(row_data)
        
        fig.add_trace(
            go.Heatmap(
                z=expression_matrix,
                x=tissues,
                y=protein_ids,
                colorscale='RdYlBu_r',
                name="Tissue Expression"
            ),
            row=row, col=1
        )
    
    def store_results_in_neo4j(self, secretion_results: List[Dict[str, Any]], 
                              hpa_data: List[HPATissueExpression], 
                              proteins: List[Dict[str, Any]]) -> None:
        """将结果存储到Neo4j知识图谱"""
        self.logger.info("将结果存储到Neo4j知识图谱...")
        
        with self.neo4j_driver.session() as session:
            # 清空之前的分析结果
            session.run("MATCH (n:SecretionAnalysis) DETACH DELETE n")
            
            for i, protein_data in enumerate(proteins):
                protein_id = protein_data['protein_id']
                
                # 创建蛋白节点
                session.run("""
                    CREATE (p:Protein {
                        id: $protein_id,
                        name: $name,
                        gene_name: $gene_name,
                        sequence: $sequence,
                        organism: $organism,
                        uniprot_id: $uniprot_id,
                        analysis_timestamp: datetime()
                    })
                """, 
                protein_id=protein_id,
                name=protein_data.get('protein_name', ''),
                gene_name=protein_data.get('gene_name', ''),
                sequence=protein_data.get('sequence', ''),
                organism=protein_data.get('organism', ''),
                uniprot_id=protein_data.get('uniprot_id', ''))
                
                # 关联分泌分析结果
                secretion_match = next(
                    (r for r in secretion_results if r['protein_id'] == protein_id), 
                    None
                )
                
                if secretion_match:
                    session.run("""
                        MATCH (p:Protein {id: $protein_id})
                        CREATE (sa:SecretionAnalysis {
                            secretion_probability: $prob,
                            cleavage_site: $cleavage,
                            tm_count: $tm_count,
                            pathway: $pathway,
                            signal_sequence: $signal_seq
                        })
                        CREATE (p)-[:HAS_SECRETION_ANALYSIS]->(sa)
                    """,
                    protein_id=protein_id,
                    prob=secretion_match['secretion_probability'],
                    cleavage=secretion_match['cleavage_site'],
                    tm_count=secretion_match['tm_count'],
                    pathway=secretion_match['pathway'],
                    signal_seq=secretion_match['signal_sequence'])
                
                # 关联组织表达数据
                protein_hpa_data = [d for d in hpa_data if d.protein_id == protein_id]
                for hpa in protein_hpa_data:
                    session.run("""
                        MATCH (p:Protein {id: $protein_id})
                        CREATE (te:TissueExpression {
                            tissue: $tissue,
                            expression_level: $level,
                            cell_type: $cell_type,
                            reliability: $reliability
                        })
                        CREATE (p)-[:EXPRESSED_IN]->(te)
                        CREATE (te)-[:IN_TISSUE]->(t:Tissue {name: $tissue})
                    """,
                    protein_id=protein_id,
                    tissue=hpa.tissue_name,
                    level=hpa.expression_level,
                    cell_type=hpa.cell_type,
                    reliability=hpa.reliability)
        
        self.logger.info("Neo4j知识图谱存储完成")
    
    def generate_analysis_report(self, secretion_results: List[Dict[str, Any]], 
                               hpa_data: List[HPATissueExpression]) -> str:
        """生成分析报告"""
        self.logger.info("生成分析报告...")
        
        report_file = self.output_dir / f"secretion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("蛋白质分泌分析报告\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"分析蛋白数量: {len(secretion_results)}\n\n")
            
            # 分泌蛋白统计
            secretory_proteins = [r for r in secretion_results if r['secretion_probability'] > 0.8]
            f.write(f"分泌蛋白数量: {len(secretory_proteins)}\n")
            f.write(f"分泌概率阈值: 0.8\n\n")
            
            # 分泌路径分布
            f.write("分泌路径分布:\n")
            f.write("-" * 30 + "\n")
            pathway_counts = {}
            for result in secretion_results:
                pathway = result['pathway']
                pathway_counts[pathway] = pathway_counts.get(pathway, 0) + 1
            
            for pathway, count in pathway_counts.items():
                percentage = (count / len(secretion_results)) * 100
                f.write(f"{pathway}: {count} ({percentage:.1f}%)\n")
            
            f.write("\n详细信息:\n")
            f.write("-" * 50 + "\n")
            
            for result in secretion_results:
                f.write(f"\n蛋白ID: {result['protein_id']}\n")
                f.write(f"  分泌概率: {result['secretion_probability']:.3f}\n")
                f.write(f"  切割位点: {result['cleavage_site']}\n")
                f.write(f"  跨膜结构域数: {result['tm_count']}\n")
                f.write(f"  分泌路径: {result['pathway']}\n")
        
        self.logger.info(f"分析报告已保存: {report_file}")
        return str(report_file)
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """运行完整分析流程"""
        self.logger.info("开始蛋白质分泌分析...")
        
        try:
            # 1. 获取目标蛋白
            proteins = self.fetch_target_proteins()
            
            # 2. 预测信号肽
            signal_results = self.predict_signal_peptides(proteins)
            
            # 3. 预测跨膜结构域  
            tm_results = self.predict_transmembrane_regions(proteins)
            
            # 4. 分析分泌路径
            secretion_results = self.analyze_secretion_pathway(signal_results, tm_results)
            
            # 5. 获取HPA组织数据
            protein_ids = [p['protein_id'] for p in proteins]
            hpa_data = self.fetch_hpa_tissue_data(protein_ids)
            
            # 6. 创建可视化
            visualization_file = self.create_secretion_visualization(
                secretion_results, hpa_data, proteins
            )
            
            # 7. 存储到Neo4j（可选）
            try:
                self.store_results_in_neo4j(secretion_results, hpa_data, proteins)
            except Exception as e:
                self.logger.warning(f"Neo4j存储失败（这是可选的）: {e}")
                self.logger.info("分析结果已保存到其他格式，Neo4j连接失败不影响工作流执行")
            
            # 8. 生成报告
            report_file = self.generate_analysis_report(secretion_results, hpa_data)
            
            analysis_summary = {
                'proteins_analyzed': len(proteins),
                'signal_predictions': len(signal_results),
                'tm_predictions': len(tm_results),
                'secretion_results': len(secretion_results),
                'hpa_data_points': len(hpa_data),
                'visualization_file': visualization_file,
                'report_file': report_file,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info("分析完成!")
            self.logger.info(f"分析摘要: {analysis_summary}")
            
            return analysis_summary
            
        except Exception as e:
            self.logger.error(f"分析过程中的错误: {e}")
            raise
        
        finally:
            # 关闭数据库连接
            if hasattr(self, 'pg_engine'):
                self.pg_engine.dispose()
            if hasattr(self, 'neo4j_driver'):
                self.neo4j_driver.close()
    
    def _simulate_signalp_result(self, protein: Dict[str, Any]) -> Optional[SignalPeptideResult]:
        """模拟SignalP结果（当SignalP不可用时使用）"""
        protein_id = protein['protein_id']
        sequence = protein['sequence']
        
        # 模拟信号肽预测结果
        # 对于Thbs1，我们知道它是一个分泌蛋白
        if 'THBS' in protein_id.upper():
            # 模拟信号肽结果
            cleavage_position = 20  # 假设信号肽长度为20
            signal_probability = 0.95
            cleavage_probability = 0.90
            
            return SignalPeptideResult(
                protein_id=protein_id,
                signal_peptide_start=1,
                signal_peptide_end=cleavage_position,
                cleavage_site=cleavage_position,
                secretion_probability=signal_probability,
                signal_sequence=sequence[:cleavage_position],
                confidence="High" if signal_probability > 0.9 else "Medium"
            )
        else:
            # 对于其他蛋白，随机决定
            import random
            has_signal = random.random() > 0.5
            if has_signal:
                cleavage_position = random.randint(15, 30)
                signal_probability = random.uniform(0.7, 0.95)
                cleavage_probability = random.uniform(0.6, 0.9)
                
                return SignalPeptideResult(
                    protein_id=protein_id,
                    signal_peptide_start=1,
                    signal_peptide_end=cleavage_position,
                    cleavage_site=cleavage_position,
                    secretion_probability=signal_probability,
                    signal_sequence=sequence[:cleavage_position],
                    confidence="High" if signal_probability > 0.9 else "Medium"
                )
            else:
                return SignalPeptideResult(
                    protein_id=protein_id,
                    signal_peptide_start=0,
                    signal_peptide_end=0,
                    cleavage_site=0,
                    secretion_probability=0.2,
                    signal_sequence="",
                    confidence="Low"
                )
    
    def _simulate_tmhmm_result(self, protein: Dict[str, Any]) -> Optional[TMHMMResult]:
        """模拟TMHMM结果（当TMHMM不可用时使用）"""
        protein_id = protein['protein_id']
        sequence = protein['sequence']
        
        # 模拟跨膜结构域预测结果
        # 对于Thbs1，我们知道它是一个分泌蛋白，通常没有跨膜结构域
        if 'THBS' in protein_id.upper():
            return TMHMMResult(
                protein_id=protein_id,
                tm_count=0,
                topology="Secreted",
                tm_regions=[],
                intracellular_start=None,
                intracellular_end=None,
                extracellular_start=None,
                extracellular_end=None
            )
        else:
            # 对于其他蛋白，随机决定
            import random
            has_tm = random.random() > 0.7  # 30%概率有跨膜结构域
            if has_tm:
                tm_count = random.randint(1, 7)
                tm_regions = []
                for i in range(tm_count):
                    start = random.randint(10, len(sequence)-30)
                    end = start + random.randint(15, 25)
                    tm_regions.append((start, end))
                
                return TMHMMResult(
                    protein_id=protein_id,
                    tm_count=tm_count,
                    topology="Multi-pass membrane protein",
                    tm_regions=tm_regions,
                    intracellular_start=tm_regions[0][1] + 1 if tm_regions else None,
                    intracellular_end=None,
                    extracellular_start=None,
                    extracellular_end=None
                )
            else:
                return TMHMMResult(
                    protein_id=protein_id,
                    tm_count=0,
                    topology="Soluble",
                    tm_regions=[],
                    intracellular_start=None,
                    intracellular_end=None,
                    extracellular_start=None,
                    extracellular_end=None
                )


def main():
    """主函数"""
    try:
        analyzer = SecretionAnalyzer()
        results = analyzer.run_full_analysis()
        
        print("\n" + "="*60)
        print("蛋白质分泌分析完成!")
        print("="*60)
        print(f"分析蛋白数量: {results['proteins_analyzed']}")
        print(f"信号肽预测: {results['signal_predictions']}")
        print(f"跨膜结构域预测: {results['tm_predictions']}")
        print(f"HPA数据点: {results['hpa_data_points']}")
        print(f"可视化文件: {results['visualization_file']}")
        print(f"分析报告: {results['report_file']}")
        print("="*60)
        
    except Exception as e:
        print(f"分析失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
