#!/usr/bin/env python3
"""
测试step2_docking_prediction.py的基本功能
"""

import json
import os
import sys
import pandas as pd
from pathlib import Path

def test_config_loading():
    """测试配置文件加载"""
    print("测试配置文件加载...")
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        print("✓ 配置文件加载成功")
        
        # 检查必需字段
        required_fields = ['target_protein', 'docking', 'autodock_tools', 'paths']
        for field in required_fields:
            if field in config:
                print(f"  ✓ {field} 字段存在")
            else:
                print(f"  ✗ 缺少 {field} 字段")
                
        return True
    except Exception as e:
        print(f"✗ 配置文件加载失败: {e}")
        return False

def test_receptor_file():
    """测试受体文件加载"""
    print("\n测试受体文件加载...")
    
    try:
        df = pd.read_csv('cache/string_receptors.csv')
        print(f"✓ 受体文件加载成功，共 {len(df)} 个受体")
        
        # 检查必需列
        required_columns = ['receptor_id', 'pdb_id', 'gene_name']
        for col in required_columns:
            if col in df.columns:
                print(f"  ✓ {col} 列存在")
            else:
                print(f"  ✗ 缺少 {col} 列")
                
        # 打印前几个受体
        print("  前3个受体:")
        for i, row in df.head(3).iterrows():
            print(f"    {row['receptor_id']}: {row['gene_name']} ({row['pdb_id']})")
            
        return True
    except Exception as e:
        print(f"✗ 受体文件加载失败: {e}")
        return False

def test_directory_structure():
    """测试目录结构"""
    print("\n测试目录结构...")
    
    required_dirs = [
        'cache',
        'cache/docking_logs',
        'cache/receptors',
        'structures'
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"  ✓ {dir_path} 目录存在")
        else:
            print(f"  ✗ 缺少 {dir_path} 目录")
            
def test_structure_file():
    """测试目标蛋白结构文件"""
    print("\n测试目标蛋白结构文件...")
    
    structure_path = 'structures/thbs4.pdb'
    if os.path.exists(structure_path):
        with open(structure_path, 'r') as f:
            content = f.read()
            
        atom_count = content.count('ATOM')
        print(f"  ✓ THBS4结构文件存在，包含 {atom_count} 个原子记录")
        
        # 检查是否有TSP结构域信息
        if 'THROMBOSPONDIN' in content:
            print("  ✓ 包含THBS4标识信息")
        else:
            print("  ⚠ 结构文件可能不是THBS4")
            
    else:
        print(f"  ✗ 结构文件不存在: {structure_path}")

def test_dependencies():
    """测试外部依赖"""
    print("\n测试外部依赖...")
    
    import shutil
    
    # 检查Vina
    if shutil.which('vina'):
        print("  ✓ AutoDock Vina 已安装")
    else:
        print("  ⚠ AutoDock Vina 未找到 (可能需要安装)")
        
    # 检查Python包
    required_packages = ['pandas', 'numpy', 'requests', 'biopython']
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package} 包已安装")
        except ImportError:
            print(f"  ✗ {package} 包未安装")

def main():
    """主测试函数"""
    print("=== Step2 Docking Prediction 测试 ===\n")
    
    # 运行所有测试
    tests = [
        test_config_loading,
        test_receptor_file,
        test_directory_structure,
        test_structure_file,
        test_dependencies
    ]
    
    passed = 0
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ 测试异常: {e}")
    
    print(f"\n=== 测试结果: {passed}/{len(tests)} 通过 ===")
    
    if passed == len(tests):
        print("✓ 所有测试通过，可以运行step2_docking_prediction.py")
    else:
        print("⚠ 部分测试未通过，请检查相关配置和依赖")

if __name__ == "__main__":
    main()
