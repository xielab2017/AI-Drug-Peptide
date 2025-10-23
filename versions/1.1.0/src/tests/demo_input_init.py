#!/usr/bin/env python3
"""
input_init.py 功能演示脚本
展示如何使用输入初始化系统
"""

import subprocess
import sys
import json
from pathlib import Path

def demo_interactive_input():
    """演示交互式输入"""
    print("🎬 input_init.py 功能演示")
    print("=" * 60)
    print()
    print("这个脚本将演示以下功能:")
    print("1. ✅ 蛋白质名称输入验证")
    print("2. ✅ 物种ID格式解析和NCBI API验证")
    print("3. ✅ 分析目标多选功能")
    print("4. ✅ 自动生成配置文件 (config.json)")
    print("5. ✅ 输出详细的流程启动清单")
    print()
    
    # 运行input_init.py
    try:
        result = subprocess.run([sys.executable, "input_init.py"], 
                              capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ 演示完成! 检查生成的文件:")
            config_files = list(Path.home().glob(".peptide_env/*_config.json"))
            workflow_files = list(Path.home().glob(".peptide_env/*_workflow.json"))
            
            for file in config_files + workflow_files:
                print(f"   📄 {file}")
                
        else:
            print(f"\n❌ 演示过程中出现问题 (退出码: {result.returncode})")
            
    except Exception as e:
        print(f"\n❌ 运行演示时发生错误: {e}")

def show_example_config():
    """显示示例配置文件"""
    print("\n📄 示例配置文件格式:")
    print("=" * 60)
    
    example_config = {
        "project_info": {
            "protein_name": "THBS4",
            "created_time": "2025-10-04T14:30:00.000Z",
            "version": "1.0"
        },
        "species_data": [
            {
                "species": "人",
                "protein_id": "NP_003253.1",
                "original_entry": "人NP_003253.1",
                "validation": {
                    "valid": True,
                    "ncbi_id": "123456789",
                    "title": "thrombospondin 4 isoform a [Homo sapiens]",
                    "organism": "Homo sapiens",
                    "length": 1075
                }
            },
            {
                "species": "小鼠",
                "protein_id": "NP_035712.1))


                "original_entry": "小鼠NP_035712.1",
                "validation": {
                    "valid": True,
                    "ncbi_id": "987654321",
                    "title": "thrombospondin 4 isoform a [Mus musculus]",
                    "organism": "Mus musculus",
                    "length": 1069
                }
            }
        },
        "analysis_targets": [
            "分泌路径解析",
            "受体发现",
            "活性评估"
        ],
        "database_paths": {
            "uniprot": "/data/uniprot/",
            "pdb": "/data/pdb/",
            "string": "/data/string/"
        },
        "equipment_apis": {
            "peptide_synthesizer": "http://localhost:8080/api/synthesizer",
            "mass_spectrometer": "http://localhost:8081/api/ms"
        }
    }
    
    print(json.dumps(example_config, ensure_ascii=False, indent=2))

def show_example_workflow():
    """显示示例流程"""
    print("\n📋 示例分析流程清单:")
    print("=" * 60)
    
    example_workflow = [
        {
            "step": 1,
            "task": "数据收集和验证",
            "description": "收集 THBS4 的多物种序列数据",
            "dependencies": [],
            "estimated_time": "2-5分钟",
            "status": "待开始"
        },
        {
            "step": 2,
            "task": "序列比对和保守性分析",
            "description": "分析 THBS4 在多个物种间的保守性",
            "dependencies": [1],
            "estimated_time": "5-10分钟",
            "status": "待开始"
        },
        {
            "step": 3,
            "task": "分泌路径预测",
            "description": "使用SignalP-6分析 THBS4 的信号肽和分泌特性",
            "dependencies": [1, 2],
            "estimated_time": "3-5分钟",
            "status": "待开始",
            "tools": ["SignalP-6", "PSORTb", "SecretP"]
        },
        {
            "step": 4,
            "task": "受体相互作用预测",
            "description": "预测 THBS4 可能结合的受体和相互作用位点",
            "dependencies": [1, 2],
            "estimated_time": "10-15分钟",
            "status": "待开始",
            "tools": ["STRING", "HINTdb", "Interactome3D"]
        },
        {
            "step": 5,
            "task": "结果整合与报告生成",
            "description": "整合所有分析结果，生成 THBS4 的综合分析报告",
            "dependencies": [1, 2, 3, 4],
            "estimated_time": "5-10分钟",
            "status": "待开始",
            "tools": ["ReportLab", "Matplotlib", "Streamlit"]
        }
    ]
    
    print(json.dumps(example_workflow, ensure_ascii=False, indent=2))

def main():
    """主演示函数"""
    print("🧬 肽段输入初始化系统演示")
    print("=" * 60)
    
    print("\n🎯 即将演示的功能:")
    print("1. 用户输入验证 (蛋白质名、物种ID)")
    print("2. NCBI API调用和物种ID验证")
    print("3. 分析目标选择和配置")
    print("4. 自动生成config.json配置文件")
    print("5. 生成分析流程启动清单")
    print()
    
    choice = input("选择演示方式:\n  1. 交互式演示 (推荐)\n  2. 显示示例配置\n  选择 (1/2): ").strip()
    
    if choice == "1":
        demo_interactive_input()
    elif choice == "2":
        show_example_config()
        show_example_workflow()
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()
