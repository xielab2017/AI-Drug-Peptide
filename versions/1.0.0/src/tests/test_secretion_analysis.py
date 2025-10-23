#!/usr/bin/env python3
"""
Test script for Secretion Analysis System
测试分泌分析系统的基本功能
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import_modules():
    """测试模块导入"""
    print("Testing module imports...")
    
    try:
        import pandas as pd
        print("✓ pandas imported successfully")
    except ImportError as e:
        print(f"✗ pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ numpy imported successfully")
    except ImportError as e:
        print(f"✗ numpy import failed: {e}")
        return False
    
    try:
        from Bio.Seq import Seq
        print("✓ Biopython imported successfully")
    except ImportError as e:
        print(f"✗ Biopython import failed: {e}")
        return False
    
    try:
        from sqlalchemy import create_engine
        print("✓ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"✗ SQLAlchemy import failed: {e}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        print("✓ matplotlib imported successfully")
    except ImportError as e:
        print(f"✗ matplotlib import failed: {e}")
        return False
    
    try:
        import plotly.graph_objects as go
        print("✓ plotly imported successfully")
    except ImportError as e:
        print(f"✗ plotly import failed: {e}")
        return False
    
    try:
        from neo4j import GraphDatabase
        print("✓ neo4j imported successfully")
    except ImportError as e:
        print(f"✗ neo4j import failed: {e}")
        return False
    
    return True

def test_data_classes():
    """测试数据类定义"""
    print("\nTesting data classes...")
    
    try:
        from secretion_analysis import SignalPeptideResult, TMHMMResult, HPATissueExpression
        
        # 测试SignalPeptideResult
        signal_result = SignalPeptideResult(
            protein_id="TEST001",
            signal_peptide_start=1,
            signal_peptide_end=25,
            cleavage_site=25,
            secretion_probability=0.95,
            signal_sequence="MKVLLVLGFLFLSSTLG",
            confidence="High"
        )
        print(f"✓ SignalPeptideResult created: {signal_result.protein_id}")
        
        # 测试TMHMMResult
        tm_result = TMHMMResult(
            protein_id="TEST001",
            tm_count=1,
            topology="Single-pass membrane protein",
            tm_regions=[(100, 120)],
            intracellular_start=121,
            intracellular_end=None,
            extracellular_start=None,
            extracellular_end=None
        )
        print(f"✓ TMHMMResult created: {tm_result.topology}")
        
        # 测试HPATissueExpression
        hpa_result = HPATissueExpression(
            protein_id="TEST001",
            tissue_name="Heart muscle",
            expression_level="High",
            cell_type="Cardiomyocytes",
            reliability="High",
            image_url="https://example.com/image.jpg"
        )
        print(f"✓ HPATissueExpression created: {hpa_result.tissue_name}")
        
        return True
        
    except Exception as e:
        print(f"✗ Data classes test failed: {e}")
        return False

def test_config_loading():
    """测试配置文件加载"""
    print("\nTesting configuration loading...")
    
    # 创建测试配置文件
    test_config = """
postgresql:
  host: "localhost"
  port: 5432
  database: "test_db"
  user: "test_user"
  password: "test_pass"

neo4j:
  uri: "bolt://localhost:7687"
  user: "neo4j"
  password: "password"
"""
    
    config_file = Path("test_config.yaml")
    config_file.write_text(test_config)
    
    try:
        from secretion_analysis import SecretionAnalyzer
        
        # 测试配置加载（不连接数据库）
        analyzer = SecretionAnalyzer.__new__(SecretionAnalyzer)
        analyzer.config = analyzer._load_config("test_config.yaml")
        
        assert analyzer.config['postgresql']['host'] == "localhost"
        assert analyzer.config['neo4j']['uri'] == "bolt://localhost:7687"
        print("✓ Configuration loaded successfully")
        
        # 清理测试文件
        config_file.unlink()
        return True
        
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        # 清理测试文件
        if config_file.exists():
            config_file.unlink()
        return False

def test_signalp_simulation():
    """测试SignalP模拟输出解析"""
    print("\nTesting SignalP output parsing...")
    
    try:
        from secretion_analysis import SecretionAnalyzer
        
        # 模拟SignalP输出
        mock_output = """
# SignalP-6.0 predicted signal peptides
# Name    Length  Max. cleavage site pos.  Cleavage site reliability (C-score)   Signal peptide reliability (S-score)
TEST001  250    25                       0.95                               0.98
TEST002  200    -                       0.12                               0.25
"""
        
        analyzer = SecretionAnalyzer.__new__(SecretionAnalyzer)
        result = analyzer._parse_signalp_output(mock_output, "TEST001")
        
        if result and result.secretion_probability > 0.8:
            print(f"✓ SignalP parsing successful: prob={result.secretion_probability}")
            return True
        else:
            print(f"✗ SignalP parsing failed: {result}")
            return False
            
    except Exception as e:
        print(f"✗ SignalP parsing test failed: {e}")
        return False

def test_tmhmm_simulation():
    """测试TMHMM模拟输出解析"""
    print("\nTesting TMHMM output parsing...")
    
    try:
        from secretion_analysis import SecretionAnalyzer
        
        # 模拟TMHMM输出
        mock_output = """
TMHMM2.0 prediction results
Accession number: Length: Number of predicted TMs: 0
EXPECTED NUMBER OF TRANSMEMBRANE HELICES: 0
In membrane helix: oooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
TMhelix: 100-120 119-139
"""
        
        analyzer = SecretionAnalyzer.__new__(SecretionAnalyzer)
        result = analyzer._parse_tmhmm_output(mock_output, "TEST001")
        
        if result and result.tm_count >= 0:
            print(f"✓ TMHMM parsing successful: tm_count={result.tm_count}")
            return True
        else:
            print(f"✗ TMHMM parsing failed: {result}")
            return False
            
    except Exception as e:
        print(f"✗ TMHMM parsing test failed: {e}")
        return False

def test_visualization():
    """测试可视化组件"""
    print("\nTesting visualization components...")
    
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        import tempfile
        from pathlib import Path
        
        # 创建简单的测试图表
        fig = make_subplots(rows=2, cols=1, subplot_titles=['Test Chart 1', 'Test Chart 2'])
        
        fig.add_trace(go.Bar(x=['A', 'B', 'C'], y=[1, 2, 3], name="Test Bar"), row=1, col=1)
        fig.add_trace(go.Scatter(x=['X', 'Y', 'Z'], y=[3, 2, 1], name="Test Line"), row=2, col=1)
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            fig.write_html(tmp.name)
            
        file_size = Path(tmp.name).stat().st_size
        print(f"✓ Visualization test successful: file size={file_size} bytes")
        
        # 清理临时文件
        Path(tmp.name).unlink()
        return True
        
    except Exception as e:
        print(f"✗ Visualization test failed: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("="*60)
    print("SECRETION ANALYSIS SYSTEM - TEST SUITE")
    print("="*60)
    
    tests = [
        test_import_modules,
        test_data_classes,
        test_config_loading,
        test_signalp_simulation,
        test_tmhmm_simulation,
        test_visualization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("="*60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("✓ All tests passed! System is ready for use.")
        return 0
    else:
        print(f"✗ {total - passed} tests failed. Please check the issues above.")
        return 1

def test_quick_run():
    """快速运行测试（不连接外部工具）"""
    print("\nTesting quick analysis run...")
    
    try:
        from secretion_analysis import SecretionAnalyzer
        
        # 创建测试数据
        test_proteins = [
            {
                'protein_id': 'INS_TEST',
                'protein_name': 'Test Insulin',
                'gene_name': 'Ins',
                'sequence': 'MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTRREAEDLQVGQVELGGGPGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN',
                'organism': 'Homo sapiens',
                'uniprot_id': 'P01308',
                'pdb_id': '1MSO'
            }
        ]
        
        # 创建临时配置文件
        config_content = """
postgresql:
  host: "localhost"
  port: 5432
  database: "test"
  user: "test"
  password: "test"

neo4j:
  uri: "bolt://localhost:7687"
  user: "neo4j"
  password: "password"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as config_file:
            config_file.write(config_content)
            config_file_path = config_file.name
        
        # 测试HPA数据获取
        analyzer = SecretionAnalyzer.__new__(SecretionAnalyzer)
        analyzer.config = analyzer._load_config(config_file_path)
        
        hpa_data = analyzer._simulate_hpa_data('INS_TEST')
        
        if len(hpa_data) > 0:
            print(f"✓ Quick run test successful: {len(hpa_data)} HPA records")
            
            # 清理临时文件
            Path(config_file_path).unlink()
            return True
        else:
            print("✗ Quick run test failed: no HPA data")
            return False
            
    except Exception as e:
        print(f"✗ Quick run test failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # 运行快速测试
        exit(run_all_tests() or test_quick_run())
    else:
        # 运行完整测试
        exit(run_all_tests())
