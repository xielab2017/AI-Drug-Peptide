#!/usr/bin/env python3
"""
AI-Drug Peptide V2.0 - 启动脚本
整合版：传统分析 + AI蛋白设计 + 文献研究
"""

import sys
import os

# 添加research_hub路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'research_hub'))

from research_hub.design.generator import ProteinGenerator
from research_hub.design.evaluator import SequenceEvaluator
from research_hub.agents.search_agent import SearchAgent


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║        🧬 AI-Drug-Peptide V2.0                          ║
║                                                          ║
║   整合版：传统分析 + AI蛋白设计 + 文献研究              ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    print("可用功能:")
    print("  1. 🧪 AI蛋白设计")
    print("  2. 📖 文献搜索")
    print("  3. 📊 序列评估")
    print("  4. 🌐 网页界面")
    print("  0. 退出")
    print()
    
    choice = input("请选择功能 (0-4): ").strip()
    
    if choice == "1":
        print("\n🧪 AI蛋白设计...")
        gen = ProteinGenerator()
        amps = gen.generate_antimicrobial_peptide(length_range=(15, 25), num_sequences=5)
        
        eval = SequenceEvaluator()
        for i, amp in enumerate(amps, 1):
            result = eval.evaluate_antimicrobial_potential(amp['sequence'])
            print(f"  {i}. {amp['sequence']}")
            print(f"     评分: {result['amp_score']:.2f} | 电荷: {amp['charge']}")
    
    elif choice == "2":
        print("\n📖 文献搜索...")
        query = input("输入搜索关键词: ")
        agent = SearchAgent()
        papers = agent.search_arxiv(query, max_results=5)
        
        for i, p in enumerate(papers, 1):
            print(f"  {i}. {p['title'][:50]}...")
    
    elif choice == "3":
        print("\n📊 序列评估...")
        seq = input("输入蛋白序列: ").strip()
        eval = SequenceEvaluator()
        result = eval.evaluate(seq)
        print(f"  稳定性: {result['stability_score']:.2f}")
        print(f"  溶解度: {result['solubility_score']:.2f}")
    
    elif choice == "4":
        print("\n🌐 启动网页界面...")
        print("运行: python research_hub/web/app.py")
        print("然后访问: http://localhost:5000")
    
    else:
        print("退出")


if __name__ == "__main__":
    main()
