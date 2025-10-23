#!/usr/bin/env python3
"""
Step 3: Conservation Analysis Script
功能：对比目标物种（如人/小鼠）的候选受体结合口袋保守性分析

主要功能：
1. 从docking_results.csv读取候选受体信息
2. 查询NCBI HomoloGene数据库获取同源蛋白序列
3. 定位结合口袋区域并提取序列
4. 使用ClustalW进行多序列比对
5. 计算保守性并筛选>80%的受体
6. 生成保守性热图可视化

作者：Peptide Research Tool
日期：2024-12-19
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
import requests
import time
from pathlib import Path
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Align import MultipleSeqAlignment
from Bio.Align.Applications import ClustalwCommandline
from Bio.SeqUtils import seq1
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import warnings

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./cache/conservation_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConservationAnalyzer:
    """保守性分析器类"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """初始化保守性分析器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.cache_dir = Path(self.config['paths']['cache_dir'])
        self.results_file = self.cache_dir / "conservation_results.csv"
        self.heatmap_file = self.cache_dir / "conservation_heatmap.png"
        
        # 创建缓存目录
        self.cache_dir.mkdir(exist_ok=True)
        
        # NCBI API 参数
        self.ncbi_base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.rate_limit = 1.0  # NCBI API 限制
        
        # 物种配置
        self.species = self.config['conservation_analysis']['target_species']
        self.conservation_threshold = self.config['conservation_analysis']['conservation_threshold']
        self.binding_window = self.config['conservation_analysis']['binding_pocket_window']
        
        logger.info("保守性分析器初始化完成")

    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            raise

    def run_conservation_analysis(self) -> pd.DataFrame:
        """运行完整的保守性分析流程"""
        logger.info("开始保守性分析...")
        
        try:
            # 步骤1: 读取对接结果
            docking_data = self._load_docking_results()
            logger.info(f"成功加载 {len(docking_data)} 个候选受体")
            
            # 步骤2: 获取同源蛋白序列
            homolog_data = self._fetch_homolog_sequences(docking_data)
            logger.info(f"成功获取 {len(homolog_data)} 个受体的同源序列")
            
            # 步骤3: 定位结合口袋区域
            pocket_data = self._locate_binding_pockets(homolog_data, docking_data)
            logger.info(f"成功定位 {len(pocket_data)} 个结合口袋")
            
            # 步骤4: 多序列比对
            alignment_data = self._perform_multiple_alignment(pocket_data)
            logger.info(f"完成 {len(alignment_data)} 个序列比对")
            
            # 步骤5: 计算保守性
            conservation_results = self._calculate_conservation(alignment_data)
            logger.info(f"完成 {len(conservation_results)} 个保守性计算")
            
            # 步骤6: 保存结果
            self._save_results(conservation_results)
            
            # 步骤7: 生成可视化
            self._generate_conservation_heatmap(conservation_results)
            
            logger.info("保守性分析完成!")
            return conservation_results
            
        except Exception as e:
            logger.error(f"保守性分析失败: {e}")
            raise

    def _load_docking_results(self) -> pd.DataFrame:
        """加载对接结果文件"""
        docking_file = self.cache_dir / "docking_results.csv"
        
        if not docking_file.exists():
            logger.error(f"对接结果文件不存在: {docking_file}")
            raise FileNotFoundError(f"对接结果文件不存在: {docking_file}")
        
        try:
            data = pd.read_csv(docking_file)
            logger.info(f"成功加载对接结果: {data.shape[0]} 行, {data.shape[1]} 列")
            return data
        except Exception as e:
            logger.error(f"读取对接结果失败: {e}")
            raise

    def _fetch_homolog_sequences(self, docking_data: pd.DataFrame) -> List[Dict]:
        """从NCBI HomoloGene获取同源蛋白序列
        
        Args:
            docking_data: 对接结果数据
            
        Returns:
            包含同源序列信息的列表
        """
        logger.info("开始获取同源蛋白序列...")
        homolog_data = []
        
        for _, row in docking_data.iterrows():
            receptor_id = row.get('receptor_id', 'unknown')
            uniprot_id = row.get('uniprot_id', '')
            
            if not uniprot_id:
                logger.warning(f"受体 {receptor_id} 缺少UniProt ID")
                continue
            
            # 获取每个物种的同源序列
            homolog_info = {
                'receptor_id': receptor_id,
                'original_uniprot_id': uniprot_id,
                'species_sequences': {}
            }
            
            for species_name, species_info in self.species.items():
                try:
                    # 查询NCBI获取同序列信息
                    sequence_data = self._query_ncbi_homolog(uniprot_id, species_info)
                    homolog_info['species_sequences'][species_name] = sequence_data
                    
                    time.sleep(self.rate_limit)  # API 限制
                    
                except Exception as e:
                    logger.warning(f"获取 {species_name} 同源序列失败: {e}")
                    homolog_info['species_sequences'][species_name] = None
            
            # 只保留有两个物种数据的记录
            valid_species = {
                k: v for k, v in homolog_info['species_sequences'].items() 
                if v is not None
            }
            
            if len(valid_species) >= 2:
                homolog_info['species_sequences'] = valid_species
                homolog_data.append(homolog_info)
                logger.info(f"成功获取受体 {receptor_id} 的 {len(valid_species)} 个物种序列")
            else:
                logger.warning(f"受体 {receptor_id} 的同源序列数据不足")
        
        logger.info(f"完成同源序列获取: {len(homolog_data)} 个受体")
        return homolog_data

    def _query_ncbi_homolog(self, uniprot_id: str, species_info: Dict) -> Dict:
        """查询NCBI获取特定物种的同源蛋白序列
        
        Args:
            uniprot_id: UniProt蛋白ID
            species_info: 物种信息字典
            
        Returns:
            包含序列信息的字典
        """
        try:
            # 步骤1: 搜索基因ID
            gene_id = self._search_gene_by_uniprot(uniprot_id)
            if not gene_id:
                raise ValueError(f"未找到基因ID: {uniprot_id}")
            
            # 步骤2: 获取HomoloGene组ID
            homolog_group = self._get_homolog_group(gene_id, species_info['taxonomy_id'])
            if not homolog_group:
                raise ValueError(f"未找到同源组: {gene_id}")
            
            # 步骤3: 获取目标物种的序列
            gene_info = self._get_gene_sequence_by_taxonomy(
                homolog_group, 
                species_info['taxonomy_id']
            )
            
            return gene_info
            
        except Exception as e:
            logger.error(f"NCBI查询失败: {e}")
            raise

    def _search_gene_by_uniprot(self, uniprot_id: str) -> Optional[str]:
        """通过UniProt ID搜索NCBI基因ID"""
        try:
            # 构建查询URL
            query_term = f"{uniprot_id}[Accession] AND refseq[filter]"
            url = f"{self.ncbi_base_url}esearch.fcgi"
            params = {
                'db': 'gene',
                'term': query_term,
                'retmax': 1,
                'retmode': 'json'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            gene_ids = data.get('esearchresult', {}).get('idlist', [])
            
            if gene_ids:
                return gene_ids[0]
            else:
                logger.warning(f"未找到基因ID: {uniprot_id}")
                return None
                
        except Exception as e:
            logger.error(f"搜索基因ID失败: {e}")
            return None

    def _get_homolog_group(self, gene_id: str, target_taxonomy: int) -> Optional[str]:
        """获取HomoloGene组ID"""
        try:
            # 获取基因的HomoloGene组
            url = f"{self.ncbi_base_url}elink.fcgi"
            params = {
                'dbfrom': 'gene',
                'db': 'homologene',
                'id': gene_id,
                'retmode': 'json'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            links = data.get('elinkset', [])
            
            if links and len(links) > 0:
                homolog_links = links[0].get('linksetdbs', [])
                if homolog_links:
                    homolog_list = homolog_links[0].get('links', [])
                    if homolog_list:
                        return homolog_list[0].get('id')
            
            return None
            
        except Exception as e:
            logger.error(f"获取HomoloGene组失败: {e}")
            return None

    def _get_gene_sequence_by_taxonomy(self, homolog_group: str, taxonomy_id: int) -> Dict:
        """通过分类ID获取基因序列"""
        try:
            # 获取HomoloGene组中的所有基因
            url = f"{self.ncbi_base_url}efetch.fcgi"
            params = {
                'db': 'homologene',
                'id': homolog_group,
                'retmode': 'json'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            homolog_data = data.get('taxset', [])
            
            # 查找目标物种的基因
            for homolog_entry in homolog_data:
                if homolog_entry.get('taxid') == str(taxonomy_id):
                    gene_id = homolog_entry.get('geneid')
                    if gene_id:
                        # 获取基因序列
                        return self._fetch_protein_sequence(gene_id)
            
            raise ValueError(f"未找到分类ID {taxonomy_id} 的基因")
            
        except Exception as e:
            logger.error(f"获取基因序列失败: {e}")
            raise

    def _fetch_protein_sequence(self, gene_id: str) -> Dict:
        """从NCBI获取蛋白质序列"""
        try:
            # 获取蛋白质序列
            url = f"{self.ncbi_base_url}efetch.fcgi"
            params = {
                'db': 'protein',
                'id': gene_id,
                'rettype': 'fasta',
                'retmode': 'text'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            sequence_text = response.text
            
            if not sequence_text or sequence_text.startswith('Error'):
                raise ValueError(f"无效的序列响应: {gene_id}")
            
            # 解析FASTA格式
            lines = sequence_text.strip().split('\n')
            header = lines[0] if lines else ""
            sequence = ''.join(lines[1:]) if len(lines) > 1 else ""
            
            return {
                'gene_id': gene_id,
                'header': header,
                'sequence': sequence,
                'length': len(sequence)
            }
            
        except Exception as e:
            logger.error(f"获取蛋白质序列失败: {e}")
            raise

    def _locate_binding_pockets(self, homolog_data: List[Dict], docking_data: pd.DataFrame) -> List[Dict]:
        """定位结合口袋区域"""
        logger.info("开始定位结合口袋区域...")
        
        pocket_data = []
        
        for homolog_info in homolog_data:
            receptor_id = homolog_info['receptor_id']
            
            # 从对接数据中获取结合位点信息
            receptor_docking = docking_data[
                docking_data['receptor_id'] == receptor_id
            ]
            
            if receptor_docking.empty:
                logger.warning(f"未找到受体 {receptor_id} 的对接信息")
                continue
            
            # 提取结合口袋区域（基于对接结果的残基位置）
            pocket_info = {
                'receptor_id': receptor_id,
                'binding_pockets': {},
                'docking_data': receptor_docking.iloc[0].to_dict()
            }
            
            # 为每个物种提取结合口袋序列
            for species_name, sequence_data in homolog_info['species_sequences'].items():
                if sequence_data is None:
                    continue
                
                sequence = sequence_data['sequence']
                sequence_length = sequence_data['length']
                
                # 从对接结果推断结合口袋位置（简化版，实际应基于复杂算法）
                binding_region = self._infer_binding_pocket_location(
                    sequence_length, 
                    receptor_docking.iloc[0]
                )
                
                # 提取口袋序列
                start_pos = max(0, binding_region['start'])
                end_pos = min(sequence_length, binding_region['end'])
                
                pocket_sequence = sequence[start_pos:end_pos]
                
                pocket_info['binding_pockets'][species_name] = {
                    'sequence': pocket_sequence,
                    'start_pos': start_pos,
                    'end_pos': end_pos,
                    'length': end_pos - start_pos,
                    'full_sequence_data': sequence_data
                }
            
            pocket_data.append(pocket_info)
            logger.info(f"完成受体 {receptor_id} 结合口袋定位")
        
        logger.info(f"完成结合口袋定位: {len(pocket_data)} 个受体")
        return pocket_data

    def _infer_binding_pocket_location(self, sequence_length: int, docking_row: pd.Series) -> Dict:
        """推断结合口袋位置（简化版本）"""
        # 这是一个简化的实现
        # 实际应用中应该基于对接结果的原子坐标来定位口袋
        
        center_position = int(sequence_length * 0.4)  # 假设在前40%位置
        window_size = self.binding_window
        
        start_pos = center_position - window_size // 2
        end_pos = start_pos + window_size
        
        return {
            'start': start_pos,
            'end': end_pos,
            'center': center_position
        }

    def _perform_multiple_alignment(self, pocket_data: List[Dict]) -> List[Dict]:
        """执行多序列比对"""
        logger.info("开始多序列比对...")
        
        alignment_data = []
        
        for pocket_info in pocket_data:
            receptor_id = pocket_info['receptor_id']
            binding_pockets = pocket_info['binding_pockets']
            
            if len(binding_pockets) < 2:
                logger.warning(f"受体 {receptor_id} 的物种数据不足，跳过比对")
                continue
            
            # 准备序列进行比对
            sequences = []
            species_names = []
            
            for species_name, pocket_data_species in binding_pockets.items():
                if pocket_data_species['sequence']:
                    sequences.append(pocket_data_species['sequence'])
                    species_names.append(species_name)
            
            if len(sequences) < 2:
                logger.warning(f"受体 {receptor_id} 的有效序列不足")
                continue
            
            try:
                # 创建FASTA格式的序列记录
                seq_records = [
                    SeqRecord(Seq(seq), id=species, description="")
                    for species, seq in zip(species_names, sequences)
                ]
                
                # 执行ClustalW比对
                alignment_result = self._run_clustalw_alignment(seq_records)
                
                if alignment_result:
                    alignment_info = {
                        'receptor_id': receptor_id,
                        'alignment': alignment_result,
                        'species_names': species_names,
                        'original_sequences': sequences,
                        'pocket_data': pocket_info
                    }
                    alignment_data.append(alignment_info)
                    logger.info(f"完成受体 {receptor_id} 序列比对")
                else:
                    logger.warning(f"受体 {receptor_id} 序列比对失败")
                    
            except Exception as e:
                logger.error(f"受体 {receptor_id} 序列比对异常: {e}")
                continue
        
        logger.info(f"完成多序列比对: {len(alignment_data)} 个受体")
        return alignment_data

    def _run_clustalw_alignment(self, seq_records: List[SeqRecord]) -> Optional[MultipleSeqAlignment]:
        """运行ClustalW比对"""
        try:
            # 创建临时序列文件
            temp_input = self.cache_dir / "temp_alignment_input.fasta"
            temp_output = self.cache_dir / "temp_alignment_output.aln"
            
            # 写入序列到临时文件
            with open(temp_input, 'w') as f:
                SeqIO.write(seq_records, f, 'fasta')
            
            # 检查ClustalW是否可用
            try:
                clustalw_cline = ClustalwCommandline(
                    "clustalw2",
                    infile=str(temp_input),
                    outfile=str(temp_output),
                    output="FASTA"
                )
                
                stdout, stderr = clustalw_cline()
                
                if os.path.exists(temp_output):
                    alignment = SeqIO.read(temp_output, 'fasta')
                    os.remove(temp_input)
                    os.remove(temp_output)
                    return MultipleSeqAlignment(alignment)
                else:
                    logger.warning("ClustalW输出文件未生成")
                    return None
                    
            except Exception as clustalw_error:
                logger.warning(f"ClustalW不可用，使用BioPython内部比对: {clustalw_error}")
                
                # 使用BioPython的内置比对功能（简化版）
                from Bio.Align import PairwiseAligner
                
                if len(seq_records) == 2:
                    aligner = PairwiseAligner()
                    aligner.mode = 'global'
                    alignments = aligner.align(seq_records[0].seq, seq_records[1].seq)
                    best_alignment = max(alignments, key=lambda x: x.score)
                    
                    # 创建MultipleSeqAlignment对象
                    aligned_seqs = [best_alignment.query, best_alignment.target]
                    alignment = MultipleSeqAlignment([SeqRecord(seq, id=seq_records[i].id) 
                                                   for i, seq in enumerate(aligned_seqs)])
                    return alignment
                else:
                    logger.error("BioPython比对仅支持双序列比对")
                    return None
                    
        except Exception as e:
            logger.error(f"序列比对失败: {e}")
            return None

    def _calculate_conservation(self, alignment_data: List[Dict]) -> pd.DataFrame:
        """计算保守性得分"""
        logger.info("开始计算保守性得分...")
        
        conservation_results = []
        
        for alignment_info in alignment_data:
            receptor_id = alignment_info['receptor_id']
            alignment = alignment_info['alignment']
            species_names = alignment_info['species_names']
            pocket_info = alignment_info['pocket_data']
            
            try:
                # 计算序列一致性
                identity_scores = self._calculate_sequence_identity(alignment)
                
                # 计算平均保守性
                avg_conservation = np.mean(identity_scores.values()) if identity_scores else 0.0
                
                # 判断是否保守
                is_conservative = avg_conservation >= self.conservation_threshold
                
                # 准备结果数据
                result_row = {
                    'receptor_id': receptor_id,
                    'species_count': len(species_names),
                    'species_names': ','.join(species_names),
                    'avg_conservation': avg_conservation,
                    'max_identity': max(identity_scores.values()) if identity_scores else 0.0,
                    'min_identity': min(identity_scores.values()) if identity_scores else 0.0,
                    'is_conservative': is_conservative,
                    'alignment_length': len(alignment[0]) if alignment else 0,
                    'conservation_threshold': self.conservation_threshold
                }
                
                # 添加物种特定信息
                for species_name, pocket_data_species in pocket_info['binding_pockets'].items():
                    result_row[f'{species_name}_sequence'] = pocket_data_species['sequence']
                    result_row[f'{species_name}_start_pos'] = pocket_data_species['start_pos']
                    result_row[f'{species_name}_end_pos'] = pocket_data_species['end_pos']
                
                conservation_results.append(result_row)
                logger.info(f"完成受体 {receptor_id} 保守性计算: {avg_conservation:.3f}")
                
            except Exception as e:
                logger.error(f"受体 {receptor_id} 保守性计算失败: {e}")
                continue
        
        conservation_df = pd.DataFrame(conservation_results)
        
        # 筛选保守性受体
        if not conservation_df.empty:
            conservative_count = len(conservation_df[conservation_df['is_conservative']])
        else:
            conservative_count = 0
        logger.info(f"保守性计算完成: {len(conservation_df)} 个受体, {conservative_count} 个保守")
        
        return conservation_df

    def _calculate_sequence_identity(self, alignment: MultipleSeqAlignment) -> Dict[str, float]:
        """计算序列比对中的一致性得分"""
        identity_scores = {}
        
        try:
            sequences = alignment
            if len(sequences) < 2:
                return identity_scores
            
            # 计算所有可能的配对
            for i in range(len(sequences)):
                for j in range(i + 1, len(sequences)):
                    seq1 = sequences[i]
                    seq2 = sequences[j]
                    
                    if len(seq1) != len(seq2):
                        continue
                    
                    # 计算一致性
                    matches = sum(1 for a, b in zip(seq1, seq2) if a == b and a != '-' and b != '-')
                    total_positions = len([a for a in seq1 if a != '-'])
                    
                    if total_positions > 0:
                        identity = matches / total_positions
                        pair_key = f"{seq1.id}_vs_{seq2.id}"
                        identity_scores[pair_key] = identity
            
        except Exception as e:
            logger.error(f"序列一致性计算失败: {e}")
        
        return identity_scores

    def _save_results(self, conservation_results: pd.DataFrame):
        """保存保守性分析结果"""
        logger.info("保存保守性分析结果...")
        
        try:
            # 保存详细结果
            conservation_results.to_csv(self.results_file, index=False, encoding='utf-8')
            
            # 筛选并保存保守性受体
            if not conservation_results.empty:
                conservative_receptors = conservation_results[
                    conservation_results['is_conservative']
                ]
            else:
                conservative_receptors = pd.DataFrame()
            
            conservative_file = self.cache_dir / "conservative_receptors.csv"
            conservative_receptors.to_csv(conservative_file, index=False, encoding='utf-8')
            
            logger.info(f"结果已保存:")
            logger.info(f"  完整结果: {self.results_file} ({len(conservation_results)} 个受体)")
            logger.info(f"  保守性受体: {conservative_file} ({len(conservative_receptors)} 个受体)")
            
        except Exception as e:
            logger.error(f"保存结果失败: {e}")
            raise

    def _generate_conservation_heatmap(self, conservation_results: pd.DataFrame):
        """生成保守性热图"""
        logger.info("生成保守性热图...")
        
        try:
            if conservation_results.empty:
                logger.warning("没有数据生成热图")
                return
            
            # 设置图形样式
            plt.style.use('default')
            sns.set_palette("viridis")
            
            # 创建主热图
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('候选受体结合口袋保守性分析', fontsize=16, fontweight='bold')
            
            # 热图1: 保守性分布
            ax1 = axes[0, 0]
            conservation_data = conservation_results[['receptor_id', 'avg_conservation', 'is_conservative']].copy()
            conservation_data = conservation_data.loc[conservation_data.index[:20]]  # 限制显示数量
            
            pivot_data = conservation_data.pivot_table(
                values='avg_conservation', 
                index='receptor_id', 
                columns='is_conservative',
                aggfunc='mean'
            )
            
            if not pivot_data.empty:
                sns.heatmap(pivot_data, annot=True, cmap='RdYlGn', 
                           vmin=0, vmax=1, ax=ax1, cbar_kws={'label': '保守性得分'})
                ax1.set_title('保守性得分分布')
                ax1.set_xlabel('保守性分类')
            
            # 热图2: 物种对比
            ax2 = axes[0, 1]
            species_columns = [col for col in conservation_results.columns if col.endswith('_sequence')]
            
            if species_columns and len(species_columns) >= 2:
                species_data = []
                for _, row in conservation_results.head(10).iterrows():  # 限制显示数量
                    species_row = {'receptor_id': row['receptor_id'], 'avg_conservation': row['avg_conservation']}
                    for col in species_columns:
                        species_name = col.replace('_sequence', '')
                        species_row[species_name] = len(row[col]) if pd.notna(row[col]) else 0
                    species_data.append(species_row)
                
                if species_data:
                    species_df = pd.DataFrame(species_data)
                    species_numeric = species_df.select_dtypes(include=[np.number])
                    if len(species_numeric.columns) > 1:
                        sns.heatmap(species_numeric.T, annot=True, cmap='Blues', ax=ax2, 
                                   cbar_kws={'label': '序列长度'})
                        ax2.set_title('不同物种序列长度对比')
            
            # 热图3: 保守性阈值分布
            ax3 = axes[1, 0]
            
            conservation_pivot = conservation_data.copy()
            conservation_pivot['conservation_bin'] = pd.cut(
                conservation_data['avg_conservation'], 
                bins=[0, 0.5, 0.7, 0.8, 0.9, 1.0],
                labels=['<50%', '50-70%', '70-80%', '80-90%', '>90%']
            )
            
            bin_counts = conservation_pivot['conservation_bin'].value_counts()
            
            bin_counts.plot(kind='bar', ax=ax3, color='skyblue', edgecolor='black')
            ax3.set_title('保守性分布统计')
            ax3.set_xlabel('保守性范围')
            ax3.set_ylabel('受体数量')
            ax3.tick_params(axis='x', rotation=45)
            
            # 热图4: 保守性vs受体数量
            ax4 = axes[1, 1]
            
            threshold_data = conservation_results.groupby('is_conservative').size()
            
            colors = ['lightcoral', 'lightgreen']
            threshold_data.plot(kind='bar', ax=ax4, color=[colors[i] for i in threshold_data.index],
                              edgecolor='black')
            ax4.set_title('保守性受体统计')
            ax4.set_xlabel('保守性状态')
            ax4.set_ylabel('受体数量')
            ax4.set_xticklabels(['非保守', '保守'], rotation=0)
            
            # 添加数值标签
            for i, v in enumerate(threshold_data.values):
                ax4.text(i, v + 0.1, str(v), ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            plt.savefig(self.heatmap_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"保守性热图已保存: {self.heatmap_file}")
            
        except Exception as e:
            logger.error(f"生成热图失败: {e}")
            logger.warning("继续执行其他步骤...")

    def run_demo_conservation_analysis(self) -> pd.DataFrame:
        """运行演示模式的保守性分析"""
        logger.info("运行演示模式保守性分析...")
        
        try:
            # 创建示例数据
            demo_data = []
            
            # 模拟3个受体的数据
            receptors = [
                {'receptor_id': 'EGFR_DEMO', 'avg_conservation': 0.92, 'is_conservative': True},
                {'receptor_id': 'MET_DEMO', 'avg_conservation': 0.78, 'is_conservative': False},
                {'receptor_id': 'VEGFR2_DEMO', 'avg_conservation': 0.85, 'is_conservative': True}
            ]
            
            for receptor in receptors:
                result_row = {
                    'receptor_id': receptor['receptor_id'],
                    'species_count': 2,
                    'species_names': 'human,mouse',
                    'avg_conservation': receptor['avg_conservation'],
                    'max_identity': receptor['avg_conservation'] + 0.05,
                    'min_identity': receptor['avg_conservation'] - 0.05,
                    'is_conservative': receptor['is_conservative'],
                    'alignment_length': 30,
                    'conservation_threshold': self.conservation_threshold,
                    'human_sequence': 'MKWVTFISLLFLFSSAYS',
                    'mouse_sequence': 'MKWVTFIALLFLFSSAYS',
                    'human_start_pos': 50,
                    'human_end_pos': 80,
                    'mouse_start_pos': 48,
                    'mouse_end_pos': 78
                }
                demo_data.append(result_row)
            
            conservation_df = pd.DataFrame(demo_data)
            
            # 保存结果
            self._save_results(conservation_df)
            
            # 生成可视化
            self._generate_conservation_heatmap(conservation_df)
            
            logger.info("演示模式分析完成!")
            return conservation_df
            
        except Exception as e:
            logger.error(f"演示模式分析失败: {e}")
            raise


def main():
    """主函数"""
    import sys
    
    try:
        # 创建分析器实例
        analyzer = ConservationAnalyzer()
        
        # 检查是否有演示模式参数
        if '--demo' in sys.argv:
            logger.info("运行演示模式...")
            results = analyzer.run_demo_conservation_analysis()
        else:
            # 运行保守性分析
            results = analyzer.run_conservation_analysis()
        
        # 打印总结信息
        total_receptors = len(results)
        if not results.empty:
            conservative_receptors = len(results[results['is_conservative']])
        else:
            conservative_receptors = 0
        
        print("\n" + "="*60)
        print("保守性分析完成!")
        print("="*60)
        print(f"总受体数量: {total_receptors}")
        print(f"保守性受体数量 (>80%): {conservative_receptors}")
        print(f"保守性比例: {conservative_receptors/total_receptors*100:.1f}%" if total_receptors > 0 else "无法计算")
        print(f"详细结果: {analyzer.results_file}")
        print(f"热图可视化: {analyzer.heatmap_file}")
        print("="*60)
        
        return 0
        
    except Exception as e:
        logger.error(f"保守性分析失败: {e}")
        print(f"\n错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
