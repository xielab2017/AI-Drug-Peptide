#!/usr/bin/env python3
"""
测试input_init.py的功能模块
"""

import sys
import json
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append('.')

def test_basic_functionality():
    """测试基本功能"""
    print("🧪 测试input_init.py基本功能")
    print("=" * 50)
    
    try:
        from input_init import ProteinInputInitializer
        
        # 创建初始器实例
        initializer = ProteinInputInitializer()
        
        # 测试蛋白质名称验证
        valid_names = ["THBS4", "TNF-α", "IL-6", "my_protein_1"]
        invalid_names = ["", "123", "protein with spaces"]
        
        print("\n✅ 测试蛋白质名称验证:")
        for name in valid_names:
            is_valid = initializer.validate_protein_name(name)
            status = "✅" if is_valid else "❌"
            print(f"  {status} '{name}': {'有效' if is_valid else '无效'}")
        
        for name in invalid_names:
            is_valid = initializer.validate_protein_name(name)
            status = "✅" if is_valid else "❌"
            print(f"  {status} '{name}': {'有效' if is_valid else '无效'}")
        
        # 测试物种条目解析
        print("\n✅ 测试物种条目解析:")
        test_entries = [
            "人NP_003253.1",
            "小鼠NP_035712.1", 
            "大肠杆菌YP_123456.1",
            "无效格式123",
            "物种名 没有ID"
        ]
        
        for entry in test_entries:
            parsed = initializer.parse_species_entry(entry)
            if parsed:
                print(f"  ✅ '{entry}' -> {parsed['species']} + {parsed['protein_id']}")
            else:
                print(f"  ❌ '{entry}' -> 解析失败")
        
        # 测试分析目标
        print("\n✅ 测试分析目标选择:")
        for key, value in initializer.analysis_options.items():
            print(f"  {key}. {value}")
        
        print("\n✅ 所有测试完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False

def show_config_structure():
    """显示配置文件结构"""
    print("\n📋 配置文件结构预览:")
    print("=" * 50)
    
    config_structure = {
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
            }
        ],
        "analysis_targets": [
            "分泌路径解析",
            "受体发现", 
            "肽段优化"
        ],
        "database_paths": {
            "uniprot": "/data/uniprot/",
            "pdb": "/data/pdb/",
            "string": "/data/string/"
        },
        "equipment_apis": {
            "peptide_synthesizer": "http://localhost:8080/api/synthesizer",
            "mass_spectrometer": "http://localhost:8081/api/ms"
        },
        "output_settings": {
            "default_path": "~/peptide_analysis_results",
            "formats": ["json", "pdf", "excel"]
        }
    }
    
    print(json.dumps(config_structure, ensure_ascii=False, indent=2))

def show_workflow_example():
    """显示工作流程示例"""
    print("\n📋 工作流程示例:")
    print("=" * 50)
    
    workflow_example = [
        {
            "step": 1,
            "task": "数据收集和验证",
            "description": "收集 THBS4 的多物种序列数据",
            "dependencies": [],
            "estimated_time": "2-5分钟",
            "tools": ["NCBI API"]
        },
        {
            "step": 2,
            "task": "序列比对和保守性分析", 
            "description": "分析 THBS4 在多个物种间的保守性",
            "dependencies": [1],
            "estimated_time": "5-10分钟",
            "tools": ["BLAST", "ClustalW"]
        },
        {
            "step": 3,
            "task": "分泌路径预测",
            "description": "使用SignalP-6分析 THBS4 的信号肽和分泌特性",
            "dependencies": [1, 2],
            "estimated_time": "3-5分钟",
            "tools": ["SignalP-6", "PSORTb"]
        }
    ]
    
    for step in workflow_example:
        print(f"\n{step['step']:2d}. {step['task']}")
        print(f"    📝 {step['description']}")
        if step['dependencies']:
            deps = ', '.join([f"步骤{d}" for d in step['dependencies']])
            print(f"    📌 依赖: {deps}")
        print(f"    ⏱️  时间: {step['estimated_time']}")
        print(f"    🛠️  工具: {', '.join(step['tools'])}")

def main():
    """主测试函数"""
    print("🧬 input_init.py 测试套件")
    print("=" * 60)
    
    # 运行功能测试
    basic_test_passed = test_basic_functionality()
    
    if basic_test_passed:
        print("\n🎉 基本功能测试通过！")
        
        # 显示配置和工作流程示例
        show_config_structure()
        show_workflow_example()
        
        print("\n🚀 要运行完整的交互式输入系统:")
        print("   python3 input_init.py")
        print("\n🎬 要运行演示:")
        print("   python3 demo_input_init.py")
        
    else:
        print("\n❌ 测试失败，请检查代码")
        sys.exit(1)

if __name__ == "__main__":
    main()
