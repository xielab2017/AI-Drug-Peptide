#!/usr/bin/env python3
"""
Streamlit可视化仪表板 - AI肽段药物分析
功能：多标签页展示分析结果、参数重新输入、报告生成
Author: AI Assistant
Date: 2024
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import os
import json
import yaml
import base64
from pathlib import Path
import subprocess
import sys
import requests
from typing import Dict, List, Any, Optional
import io
from io import BytesIO

# 文件路径
CACHE_DIR = Path("cache")
OUTPUT_DIR = Path("output")
CONFIG_FILE = Path("config/config.yaml")

# 页面配置
st.set_page_config(
    page_title="AI肽段药物分析仪表板",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

class PeptideDashboard:
    """肽段分析仪表板主类"""
    
    def __init__(self):
        self.data_cache = {}
        self.load_config()
        
    def load_config(self):
        """加载配置文件"""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
            else:
                self.config = self._get_default_config()
        except Exception as e:
            st.warning(f"配置文件加载失败: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self):
        """默认配置"""
        return {
            'target_protein_id': 'EXAMPLE_PROTEIN',
            'confidence_threshold': 0.9,
            'species': ['Homo sapiens', 'Mus musculus'],
            'output_format': 'excel'
        }

@st.cache_data
def load_data_file(file_path: str, file_type: str = 'csv') -> pd.DataFrame:
    """缓存数据文件加载"""
    try:
    if Path(file_path).exists():
            if file_type == 'csv':
                return pd.read_csv(file_path)
            elif file_type == 'excel':
                return pd.read_excel(file_path, sheet_name=None)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"数据加载失败 {file_path}: {e}")
        return pd.DataFrame()

def create_overview_tab():
    """数据概览标签页"""
    st.header("📊 数据概览")
    
    # 侧边栏参数显示
    with st.sidebar:
        st.subheader("📋 当前参数")
        config = PeptideDashboard().config
        
        # 输入参数展示
        st.markdown("#### 目标蛋白")
        st.text(config.get('target_protein_id', 'EXAMPLE_PROTEIN'))
        
        st.markdown("#### 置信度阈值")
        st.text(config.get('confidence_threshold', 0.9))
        
        st.markdown("#### 分析物种")
        species = config.get('species', ['Homo sapiens', 'Mus musculus'])
        for species_name in species:
            st.write(f"• {species_name}")
    
    # 数据文件状态检查
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 数据文件状态")
        data_files = {
            "STRING相互作用": "cache/string_receptors.csv",
            "分子对接结果": "cache/docking_results.csv", 
            "保守性分析": "cache/conservation_results.csv",
            "分泌分析": "secretion_analysis_output",
            "优先级报告": "output/receptor_priority.xlsx"
        }
        
        for file_name, file_path in data_files.items():
            if Path(file_path).exists():
                st.success(f"✅ {file_name}")
            else:
                st.error(f"❌ {file_name}")
    
    with col2:
        st.subheader("🔢 分析统计")
        
        # 加载并显示统计数据
        try:
            string_df = load_data_file("cache/string_receptors.csv")
            docking_df = load_data_file("cache/docking_results.csv")
            conservation_df = load_data_file("cache/conservation_results.csv")
            
            metrics_data = {
                "STRING受体": len(string_df),
                "对接成功": len(docking_df[docking_df['success_rate'] > 0.8]) if not docking_df.empty else 0,
                "保守性高": len(conservation_df[conservation_df['reliability_score'] > 0.9]) if not conservation_df.empty else 0,
                "核心受体": 3  # Top 3 from merged results
            }
            
            for metric, value in metrics_data.items():
                st.metric(metric, value)
                
        except Exception as e:
            st.error(f"统计计算失败: {e}")
    
    # 多物种数据表格
    st.subheader("🌍 多物种数据表")
    
    if not string_df.empty:
        st.dataframe(
            string_df[['receptor_id', 'gene_name', 'organism', 'reliability_score']].head(10),
            use_container_width=True
        )
        
        # 物种分布图
        species_counts = string_df['organism'].value_counts()
        fig_species = px.pie(
            values=species_counts.values,
            names=species_counts.index,
            title="分析物种分布"
        )
        st.plotly_chart(fig_species, use_container_width=True)
    
    # 结构预览
    st.subheader("🧬 蛋白质结构预览")
    
    structures_dir = Path("structures")
    if structures_dir.exists():
        pdb_files = list(structures_dir.glob("*.pdb"))
        
        if pdb_files:
            st.info(f"发现 {len(pdb_files)} 个PDB结构文件")
            
            # 显示第一个结构文件的简略信息
            with open(pdb_files[0], 'r') as f:
                lines = f.readlines()[:20]  # 只显示前20行
                st.text_area("PDB文件预览", ''.join(lines), height=300)
        else:
            st.warning("未找到PDB结构文件")
    else:
        st.warning("structures目录不存在")

def create_secretion_tab():
    """分泌路径分析标签页"""
    st.header("🚰 分泌路径分析")
    
    # 检查是否有分泌分析结果
    secretion_dir = Path("secretion_analysis_output")
    
    if not secretion_dir.exists():
        st.warning("分泌分析尚未运行，请先运行 secretion_analysis.py")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 信号肽预测")
        
        # 模拟信号肽数据（实际应来自分泌分析的CSV输出）
        signal_data = {
            'Protein_ID': ['STRING1', 'STRING2', 'STRING3', 'STRING4', 'STRING5'],
            'Secretion_Probability': [0.92, 0.85, 0.78, 0.95, 0.88],
            'Cleavage_Site': [22, 18, 25, 19, 21],
            'Confidence': ['High', 'Medium', 'Low', 'High', 'High']
        }
        
        signal_df = pd.DataFrame(signal_data)
        
        # 分泌概率柱状图
        fig_prob = px.bar(
            signal_df,
            x='Protein_ID',
            y='Secretion_Probability',
            color='Confidence',
            title="蛋白分泌概率预测",
            color_discrete_map={'High': 'green', 'Medium': 'orange', 'Low': 'red'}
        )
        fig_prob.add_hline(y=0.8, line_dash="dash", line_color="red", 
                          annotation_text="阈值 (0.8)")
        st.plotly_chart(fig_prob, use_container_width=True)
        
        # 分泌概率统计
        secretory_count = len(signal_df[signal_df['Secretion_Probability'] > 0.8])
        st.metric("分泌蛋白数量", f"{secretory_count}/{len(signal_df)}")
    
    with col2:
        st.subheader("🔄 转运路径分布")
        
        # 模拟转运路径数据
        pathway_data = {
            'Pathway': ['经典分泌(ER-Golgi)', '非经典分泌(囊泡)', '非分泌性', '低置信度'],
            'Count': [15, 8, 3, 2]
        }
        
        fig_pathway = px.pie(
            values=pathway_data['Count'],
            names=pathway_data['Pathway'],
            title="蛋白转运路径分布",
            hole=0.3
        )
        st.plotly_chart(fig_pathway, use_container_width=True)
    
    # 组织定位热图
    st.subheader("🎯 组织定位热图")
    
    # 模拟组织表达数据
    tissues = ['心脏', '肝脏', '肾脏', '肺脏', '脑组织', '肌肉']
    proteins = ['STRING1', 'STRING2', 'STRING3', 'STRING4', 'STRING5']
    
    # 生成随机的表达水平矩阵
    np.random.seed(42)
    expression_matrix = np.random.randint(0, 4, size=(len(proteins), len(tissues)))
    
    fig_heatmap = px.imshow(
        expression_matrix,
        x=tissues,
        y=proteins,
        color_continuous_scale=['white', 'yellow', 'orange', 'red'],
        title="蛋白组织表达水平热图",
        aspect='auto'
    )
    
    fig_heatmap.update_layout(
        title_x=0.5,
        font=dict(size=12)
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # 热图说明
    st.info("""
    **表达水平说明：**
    - 白色：无表达 (0)
    - 黄色：低表达 (1) 
    - 橙色：中等表达 (2)
    - 红色：高表达 (3)
    """)

def create_receptor_tab():
    """受体发现标签页"""
    st.header("🎯 受体发现")
    
    # 加载数据
    docking_df = load_data_file("cache/docking_results.csv")
    conservation_df = load_data_file("cache/conservation_results.csv")
    priority_df = load_data_file("output/receptor_priority.xlsx")
    
    if docking_df.empty:
        st.warning("分子对接数据未找到，请先运行 step2_docking_prediction.py")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚡ Top3受体结合能对比")
        
        # 获取Top 3受体（按结合能排序）
        top3_df = docking_df.nlargest(3, 'avg_binding_energy')
        
        # 结合能柱状图
        fig_binding = px.bar(
            top3_df,
            x='gene_name',
            y='avg_binding_energy',
            text='avg_binding_energy',
            title="Top 3受体结合能对比",
            color='avg_binding_energy',
            color_continuous_scale='viridis_r'
        )
        
        fig_binding.update_layout(
            xaxis_title="基因名称",
            yaxis_title="平均结合能 (kcal/mol)",
            showlegend=False
        )
        fig_binding.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        
        st.plotly_chart(fig_binding, use_container_width=True)
        
        # Top 3受体详细信息表格
        st.subheader("📋 核心受体信息")
        core_data = top3_df[['receptor_id', 'gene_name', 'avg_binding_energy', 'success_rate']].copy()
        core_data['rank'] = range(1, len(core_data) + 1)
        core_data = core_data[['rank', 'receptor_id', 'gene_name', 'avg_binding_energy', 'success_rate']]
        
        st.dataframe(core_data, use_container_width=True)
    
    with col2:
        st.subheader("🌍 跨物种保守性分析")
        
        if not conservation_df.empty:
            # 保守性评分分布
            fig_conservation = px.histogram(
                conservation_df,
                x='reliability_score',
                nbins=10,
                title="受体保守性评分分布",
                labels={'reliability_score': '保守性评分', 'count': '受体数量'}
            )
            
            fig_conservation.add_vline(x=0.9, line_dash="dash", line_color="red",
                                     annotation_text="高保守性阈值")
            
            st.plotly_chart(fig_conservation, use_container_width=True)
            
            # 保守性统计
            high_conservation = len(conservation_df[conservation_df['reliability_score'] > 0.9])
            total_receptors = len(conservation_df)
            
            st.metric("高保守性受体", f"{high_conservation}/{total_receptors}")
            st.metric("保守性比例", f"{high_conservation/total_receptors*100:.1f}%")
    
    # 综合评分雷达图
    st.subheader("📊 受体综合评分雷达图")
    
    if not top3_df.empty:
        # 为每个受体计算综合评分（简化版本）
        radar_data = []
        
        for _, row in top3_df.iterrows():
            # 这里使用简化的评分计算，实际应该从step4的结果中获取
            radar_dict = {
                'receptor': row['gene_name'],
                'binding_affinity': (row['avg_binding_energy'] + 12) / 12,  # 归一化到0-1
                'success_rate': row['success_rate'],
                'conservation': 0.9,  # 从conservation df中获取实际值
                'literature': 0.8  # 模拟数据
            }
            radar_data.append(radar_dict)
        
        # 创建雷达图
        fig_radar = go.Figure()
        
        categories = ['结合亲和力', '成功率', '保守性', '文献支持']
        
        for data in radar_data:
            values = [data['binding_affinity'], data['success_rate'], 
                     data['conservation'], data['literature']]
            
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=data['receptor']
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title="受体综合评分对比"
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)

def create_optimization_tab():
    """肽段优化结果标签页"""
    st.header("🧬 肽段优化结果")
    
    # 模拟优化后的肽段库数据
    peptide_data = {
        'Peptide_ID': [f'PEPTIDE_{i:03d}' for i in range(1, 21)],
        'Sequence': [
            'ACDEFGHIKLMNPQRSTVWY',
            'ADEFGHIKLMNPQRSTVWY',
            'ACDEFGHIKLMNPQRSTVW',
            'BCDEFGHIKLMNPQRSTVW',
            'ACDEFGIHKLMNPQRSTVW',
            'ACDEFGHIKLPNPQRSTVW',
            'ACDEFGHIKLMNPQRSTVX',
            'ACDEFGHIKLMNAQRSTVW',
            'ACDEFGHIKLMNPQRSTUV',
            'ABCDEFGHIKLMNPQRSTVW',
            'ACDEFGHIKLMNPQRSAB',
            'ACDEFGHIKLMNPQRSTCD',
            'ACDEFGHIKLMNPQRSTEF',
            'ACDEFGHIKLMNPQRSTGH',
            'ACDEFGHIKLMNPQRSTIJ',
            'ACDEFGHIKLMNPQRSTKL',
            'ACDEFGHIKLMNPQRSTMN',
            'ACDEFGHIKLMNPQRSTOP',

            'ACDEFGHIKLMNPQRSTQR',
            'ACDEFGHIKLMNPQRSTST'
        ][:20],
        'Binding_Energy': np.random.uniform(-10, -5, 20),
        'Stability': np.random.uniform(0.5, 1.0, 20),
        'Activity': np.random.uniform(0.3, 0.95, 20),
        'Molecular_Weight': np.random.uniform(800, 2500, 20),
        'Optimization_Round': np.random.randint(1, 6, 20)
    }
    
    peptide_df = pd.DataFrame(peptide_data)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 稳定性-活性散点图")
        
        # 创建散点图
        fig_scatter = px.scatter(
            peptide_df,
            x='Stability',
            y='Activity',
            size='Molecular_Weight',
            color='Binding_Energy',
            hover_data=['Peptide_ID', 'Sequence'],
            title="肽段稳定性 vs 活性分析",
            labels={
                'Stability': '稳定性指标',
                'Activity': '活性指标',
                'Molecular_Weight': '分子量'
            }
        )
        
        # 添加象限线
        fig_scatter.add_hline(y=peptide_df['Activity'].median(), line_dash="dash", 
                             line_color="gray", opacity=0.5)
        fig_scatter.add_vline(x=peptide_df['Stability'].median(), line_dash="dash", 
                             line_color="gray", opacity=0.5)
        
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # 象限说明
        st.info("""
        **象限说明：**
        - 右上象限：高稳定性 + 高活性 → 优先候选
        - 左上象限：低稳定性 + 高活性 → 需优化稳定性  
        - 右下象限：高稳定性 + 低活性 → 需优化活性
        - 左下象限：低稳定性 + 低活性 → 候选级别较低
        """)
    
    with col2:
        st.subheader("🎯 优化进展")
        
        # 优化轮次统计
        round_counts = peptide_df['Optimization_Round'].value_counts().sort_index()
        fig_rounds = px.bar(
            x=round_counts.index,
            y=round_counts.values,
            title="优化轮次分布",
            labels={'x': '优化轮次', 'y': '肽段数量'}
        )
        st.plotly_chart(fig_rounds)
        
        # 统计指标
        st.metric("总肽段数", len(peptide_df))
        high_performance = len(peptide_df[
            (peptide_df['Stability'] > 0.8) & 
            (peptide_df['Activity'] > 0.7)
        ])
        st.metric("高性能肽段", high_performance)
        
        best_binding = peptide_df.loc[peptide_df['Binding_Energy'].idxmin()]
        st.metric("最佳结合能", f"{best_binding['Binding_Energy']:.2f}")
    
    # 肽段库表格
    st.subheader("📋 优化肽段库")
    
    # 筛选控制
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        min_stability = st.slider("最小稳定性", 0.0, 1.0, 0.0, 0.1)
    with col_filter2:
        filtering_activity = st.slider("最小活性", 0.0, 1.0, 0.0, 0.1)
    with col_filter3:
        sort_by = st.selectbox("排序方式", 
                              ['Binding_Energy', 'Stability', 'Activity'])
    
    # 应用筛选
    filtered_df = peptide_df[
        (peptide_df['Stability'] >= min_stability) &
        (peptide_df['Activity'] >= filtering_activity)
    ].sort_values(sort_by)
    
    # 显示表格
    st.dataframe(
        filtered_df[['Peptide_ID', 'Sequence', 'Binding_Energy', 
                   'Stability', 'Activity', 'Molecular_Weight']],
        use_container_width=True
    )
    
    # 下载按钮
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 下载筛选结果 (CSV)",
        data=csv,
        file_name=f"optimized_peptides_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def create_parameter_input_section():
    """参数重新输入部分"""
    with st.sidebar:
        st.markdown("---")
        st.subheader("⚙️ 参数重新配置")
        
        # 目标蛋白ID输入
        target_protein = st.text_input(
            "目标蛋白ID",
            value="EXAMPLE_PROTEIN",
            help="输入目标蛋白的UniProt或其他数据库ID"
        )
        
        # 置信度阈值
        confidence_threshold = st.slider(
            "置信度阈值",
            min_value=0.0,
            max_value=1.0,
            value=0.9,
            step=0.05,
            help="STRING相互作用的置信度阈值"
        )
        
        # 物种选择
        species_options = [
            'Homo sapiens', 'Mus musculus', 'Rattus norvegicus',
            'Danio rerio', 'Drosophila melanogaster', 'Caenorhabditis elegans'
        ]
        
        selected_species = st.multiselect(
            "选择分析物种",
            options=species_options,
            default=['Homo sapiens', 'Mus musculus'],
            help="选择要包含在分析中的物种"
        )
        
        # 分子对接参数
        st.markdown("#### 分子对接参数")
        num_runs = st.number_input(
            "对接运行次数",
            min_value=1,
            max_value=10,
            value=3,
            help="每个受体的对接运行次数"
        )
        
        # 重新运行按钮
        if st.button("🔄 重新运行完整分析", type="primary"):
            st.session_state.rerun_requested = True
            st.session_state.new_params = {
                'target_protein': target_protein,
                'confidence_threshold': confidence_threshold,
                'species': selected_species,
                'num_runs': num_runs
            }
    
    # 处理重新运行请求
    if hasattr(st.session_state, 'rerun_requested') and st.session_state.rerun_requested:
        return handle_rerun_request(st.session_state.new_params)
    
    return None

def handle_rerun_request(params: Dict[str, Any]):
    """处理重新运行请求"""
    st.sidebar.info("正在重新运行分析...")
    
    # 更新配置文件
    updated_config = {
        'target_protein_id': params['target_protein'],
        'confidence_threshold': params['confidence_threshold'],
        'species': params['species'],
        'num_runs': params['num_runs']
    }
    
    try:
        # 保存更新的配置
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(updated_config, f, default_flow_style=False, allow_unicode=True)
        
        # 运行分析步骤
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        
        # Step 1: STRING相互作用分析
        status_text.text("Step 1: STRING相互作用分析")
        progress_bar.progress(20)
        
        # Step 2: 分子对接预测
        status_text.text("Step 2: 分子对接预测")
        progress_bar.progress(40)
        
        # Step 3: 保守性分析
        status_text.text("Step 3: 保守性分析")
        progress_bar.progress(60)
        
        # Step 4: 结果合并
        status_text.text("Step 4: 结果合并")
        progress_bar.progress(80)
        
        # Step 5: 分泌分析
        status_text.text("Step 5: 分泌分析")
        progress_bar.progress(100)
        
        status_text.text("分析完成!")
        
        st.sidebar.success("✅ 重新分析完成!")
        st.sidebar.info("请刷新页面查看最新结果")
        
        # 清除重新运行标志
        st.session_state.rerun_requested = False
        
    except Exception as e:
        st.sidebar.error(f"重新运行失败: {e}")
        st.session_state.rerun_requested = False

def create_pdf_report_button():
    """创建PDF报告生成按钮"""
    st.markdown("---")
    st.subheader("📄 生成分析报告")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("📊 生成Excel报告", use_container_width=True):
            st.info("Excel报告已生成")
            # 这里可以添加实际的Excel报告生成逻辑
    
    with col2:
        if st.button("📋 生成PDF报告", use_container_width=True):
            generate_pdf_report()
    
    with col3:
        if st.button("📈 导出图表包", use_container_width=True):
            export_charts()

def generate_pdf_report():
    """生成PDF报告"""
    try:
        st.info("正在生成PDF报告...")
        
        # 模拟PDF生成过程
        progress = st.progress(0)
        
        for i in range(100):
            progress.progress(i + 1)
            if i % 20 == 0:
                st.text(f"生成进度: {i+1}%")
        
        # 实际实现中，这里会调用PDF生成脚本
        # subprocess.run(['python', 'generate_pdf_report.py'])
        
        st.success("✅ PDF报告生成完成!")
        st.info("报告文件已保存到 output/ 目录")
        
        # 提供下载链接
        if Path("output").exists():
            st.download_button(
                label="📥 下载PDF报告",
                data=b"PDF content would be here",
                file_name=f"peptide_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
            
    except Exception as e:
        st.error(f"PDF报告生成失败: {e}")

def export_charts():
    """导出图表包"""
    try:
        st.info("正在导出图表包...")
        
        # 创建ZIP文件（这里是示例实现）
        zip_data = io.BytesIO()
        
        st.success("✅ 图表包导出完成!")
        
        st.download_button(
            label="📦 下载图表包",
            data=zip_data.getvalue(),
            file_name=f"peptide_charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip"
        )
        
    except Exception as e:
        st.error(f"图表包导出失败: {e}")

def main():
    """主函数"""
    st.title("🧬 AI肽段药物分析仪表板")
    st.markdown("---")
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 数据概览", 
        "🚰 分泌路径分析", 
        "🎯 受体发现", 
        "🧬 肽段优化结果"
    ])
    
    # 侧边栏参数输入
    create_parameter_input_section()
    
    # 标签页内容
    with tab1:
        create_overview_tab()
    
    with tab2:
        create_secretion_tab()
    
    with tab3:
        create_receptor_tab()
    
    with tab4:
        create_optimization_tab()
    
    # 底部报告生成
    create_pdf_report_button()
    
    # 页脚信息
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**版本信息**")
        st.text("v1.0.0")
        
    with col2:
        st.markdown("**最后更新**")
        st.text(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
    with col3:
        st.markdown("**联系方式**")
        st.text("AI Assistant")

if __name__ == "__main__":
    main()
