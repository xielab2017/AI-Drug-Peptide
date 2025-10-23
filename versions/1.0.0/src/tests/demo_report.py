#!/usr/bin/env python3
"""
肽药物开发报告生成器演示脚本
Demonstration script for Peptide Drug Development Report Generator

This script shows how to use the report_generator.py for generating
comprehensive PDF reports with mock data.
"""

import os
import sys
import json
from report_generator import ReportGenerator

def create_demo_config():
    """创建演示用的配置文件"""
    demo_config = {
        "postgres": {
            "host": "localhost",
            "port": 5432,
            "database": "peptide_analysis_demo",
            "user": "demo_user",
            "password": "demo_password"
        },
        "neo4j": {
            "uri": "bolt://localhost:7687",
            "user": "neo4j",
            "password": "demo_password"
        },
        "smtp": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "demo@example.com",
            "sender_password": "demo_app_password"
        },
        "reports": {
            "default_language": "zh_CN",
            "include_charts": True,
            "chart_quality": "high",
            "logo_path": "logo.png"
        }
    }
    
    # 保存演示配置文件
    with open('demo_config.json', 'w', encoding='utf-8') as f:
        json.dump(demo_config, f, indent=2, ensure_ascii=False)
    
    print("✓ 演示配置文件已创建: demo_config.json")

def demo_basic_usage():
    """演示基本使用方法"""
    print("\n=== 基本使用演示 ===")
    
    try:
        # 初始化报告生成器
        generator = ReportGenerator('demo_config.json')
        
        # 生成THBS4分析报告
        print("生成THBS4肽药物开发分析报告...")
        output_path = generator.generate_report(
            protein_name="THBS4",
            species_list=["人类", "小鼠", "大鼠", "牛"],
            report_title="THBS4肽药物开发多物种分析报告"
        )
        
        print(f"报告生成完成: {output_path}")
        
    except Exception as e:
        print(f"✗ 报告生成失败: {e}")

def demo_custom_title():
    """演示自定义标题"""
    print("\n=== 自定义标题演示 ===")
    
    try:
        generator = ReportGenerator('demo_config.json')
        
        # 生成带有自定义标题的报告
        custom_title = "IL-6信号通路肽药物优化研究专项报告"
        output_path = generator.generate_report(
            protein_name="IL6",
            species_list=["人类", "小鼠"],
            report_title=custom_title
        )
        
        print(f"自定义标题报告生成完成: {output_path}")
        
    except Exception as e:
        print(f"✗ 自定义标题报告失败: {e}")

def demo_multiple_reports():
    """演示批量生成多个报告"""
    print("\n=== 批量报告生成演示 ===")
    
    proteins = [
        ("TNF", "肿瘤坏死因子肽药物开发分析"),
        ("VEGFA", "血管内皮生长因子药物研究"),
        ("IGF1", "胰岛素样生长因子1肽段优化")
    ]
    
    try:
        generator = ReportGenerator('demo_config.json')
        
        generated_reports = []
        
        for protein_name, report_title in proteins:
            print(f"正在生成 {protein_name} 报告...")
            
            output_path = generator.generate_report(
                protein_name=protein_name,
                species_list=["人类", "小鼠", "大鼠"],
                report_title=report_title
            )
            
            generated_reports.append({
                "protein": protein_name,
                "report_title": report_title,
                "output_path": output_path
            })
        
        print("\n✓ 批量报告生成完成:")
        for report in generated_reports:
            print(f"  - {report['protein']}: {report['output_path']}")
            
    except Exception as e:
        print(f"✗ 批量报告生成失败: {e}")

def demo_advanced_features():
    """演示高级功能"""
    print("\n=== 高级功能演示 ===")
    
    try:
        generator = ReportGenerator('demo_config.json')
        
        # 生成详细报告并尝试邮件发送示例
        output_path = generator.generate_report(
            protein_name="BDNF",
            species_list=["人类", "小鼠", "大鼠", "猕猴"],
            report_title="脑源性神经营养因子肽药物开发详细分析",
            output_path="output/demo_advanced_report.pdf"
        )
        
        print(f"✓ 高级功能报告生成完成: {output_path}")
        
        # 尝试发送邮件（需要正确配置SMTP）
        # recipients = ["researcher@lab.org", "pi@lab.org"]
        # generator.send_email_report(output_path, recipients, "肽药物分析报告")
        # print("✓ 邮件发送尝试完成")
        
    except Exception as e:
        print(f"✗ 高级功能演示失败: {e}")

def main():
    """主演示函数"""
    print("=== 肽药物开发报告生成器演示 ===")
    print("=== Peptide Drug Development Report Generator Demo ===")
    
    # 检查必要文件
    if not os.path.exists('report_generator.py'):
        print("✗ 找不到 report_generator.py，请确保在正确的目录中运行此脚本")
        return
    
    # 创建演示配置文件
    create_demo_config()
    
    # 创建输出目录
    os.makedirs('output', exist_ok=True)
    
    # 运行演示
    print("\n开始演示...")
    
    # 基本使用演示
    demo_basic_usage()
    
    # 自定义标题演示
    demo_custom_title()
    
    # 批量报告演示
    demo_multiple_reports()
    
    # 高级功能演示
    demo_advanced_features()
    
    print("\n=== 演示完成 ===")
    print("\n生成的报告文件:")
    
    # 列出生成的文件
    output_files = []
    for root, dirs, files in os.walk('output'):
        for file in files:
            if file.endswith('.pdf'):
                output_files.append(os.path.join(root, file))
    
    if output_files:
        for file in output_files:
            print(f"  - {file}")
    else:
        print("  (没有找到生成的报告文件)")
    
    print("\n查看使用说明: python report_generator.py --help")
    print("查看详细文档: REPORT_GENERATOR_README.md")

if __name__ == '__main__':
    main()
