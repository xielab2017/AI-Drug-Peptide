#!/usr/bin/env python3
"""
ResearchHub CLI - 命令行版
使用方法: python research_hub.py [command] [options]
"""

import sys
import argparse
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.search_agent import SearchAgent
from design.generator import ProteinGenerator
from design.evaluator import SequenceEvaluator
from design.exporter import DesignExporter
from storage.database import Database


def cmd_search(args):
    """搜索论文"""
    print(f"🔍 搜索: {args.query}")
    print(f"   来源: {args.source}")
    print(f"   数量: {args.num}\n")
    
    agent = SearchAgent()
    papers = agent.search(args.query, args.source, args.num)
    
    for i, p in enumerate(papers, 1):
        print(f"{i}. {p['title'][:60]}...")
        print(f"   作者: {', '.join(p['authors'][:3])}")
        print(f"   时间: {p['published'][:10]}")
        print()
    
    return papers


def cmd_generate(args):
    """生成蛋白/肽序列"""
    print(f"🧪 生成序列")
    print(f"   类型: {args.type}")
    print(f"   长度: {args.length}")
    print(f"   数量: {args.num}\n")
    
    gen = ProteinGenerator()
    eval = SequenceEvaluator()
    
    results = []
    
    if args.type == "amp":
        length_range = tuple(map(int, args.length.split('-')))
        peptides = gen.generate_antimicrobial_peptide(length_range, args.num)
        
        for p in peptides:
            eval_result = eval.evaluate_antimicrobial_potential(p['sequence'])
            result = {
                'sequence': p['sequence'],
                'score': eval_result['amp_score'],
                'charge': p['charge'],
                'hydrophobicity': p['hydrophobicity']
            }
            results.append(result)
            
            score_str = f"{result['score']:.2f}"
            print(f"🔬 {p['sequence']}")
            print(f"   评分: {score_str} | 电荷: {result['charge']} | 疏水性: {result['hydrophobicity']:.2f}")
            print()
    
    elif args.type == "random":
        length = int(args.length)
        for i in range(args.num):
            seq = gen.generate_random(length, weighted=True)
            print(f"🔬 {seq}")
            print()
    
    # 导出结果
    if args.output and results:
        exporter = DesignExporter()
        path = exporter.export_json(results, args.output)
        print(f"💾 结果已保存: {path}")
    
    return results


def cmd_evaluate(args):
    """评估序列"""
    print(f"📊 评估序列: {args.sequence}\n")
    
    eval = SequenceEvaluator()
    result = eval.evaluate(args.sequence)
    
    print("评估结果:")
    print(f"  长度: {result['length']}")
    print(f"  疏水性: {result['hydrophobicity']:.3f}")
    print(f"  净电荷: {result['charge']:.1f}")
    print(f"  等电点: {result['isoelectric_point']:.1f}")
    print(f"  不稳定指数: {result['instability_index']:.1f}")
    print(f"  稳定性评分: {result['stability_score']:.2f}")
    print(f"  溶解度评分: {result['solubility_score']:.2f}")
    
    # 抗菌肽评估
    if args.amp:
        amp_result = eval.evaluate_antimicrobial_potential(args.sequence)
        print(f"\n抗菌肽潜力:")
        print(f"  AMP评分: {amp_result['amp_score']:.2f}")
        print(f"  建议: {amp_result['recommendation']}")


def cmd_notebook(args):
    """笔记本管理"""
    db = Database()
    
    if args.action == "list":
        notebooks = db.list_notebooks()
        print(f"📓 我的笔记本 ({len(notebooks)}个)\n")
        for nb in notebooks:
            print(f"  • {nb['title']}")
            print(f"    创建于: {nb['created_at'][:10]}")
            print()
    
    elif args.action == "create":
        nb_id = db.create_notebook(args.name)
        print(f"✅ 笔记本创建成功: {args.name} (ID: {nb_id})")
    
    elif args.action == "search":
        results = db.search(args.query)
        print(f"🔎 搜索结果: {args.query}\n")
        for r in results:
            print(f"  • {r['title'][:50]}")


def cmd_db(args):
    """数据库查询"""
    from databases.protein_db import UniProtClient, PDBClient
    
    if args.db == "uniprot":
        client = UniProtClient()
        results = client.search(args.query, size=args.num)
        print(f"🔬 UniProt 结果: {args.query}\n")
        for r in results:
            print(f"  • {r['accession']}: {r['protein_name'][:40]}")
            print(f"    生物: {r['organism']}")
            print()
    
    elif args.db == "pdb":
        client = PDBClient()
        results = client.search(args.query, size=args.num)
        print(f"🔬 PDB 结果: {args.query}\n")
        for r in results:
            print(f"  • {r['pdb_id']}: {r['title'][:40]}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description="ResearchHub - 学术研究与AI蛋白设计工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s search "machine learning" --num 5
  %(prog)s generate --type amp --length 15-25 --num 10
  %(prog)s evaluate "KALKKKLLKALKKK" --amp
  %(prog)s notebook create "我的研究"
  %(prog)s db uniprot "kinase" --num 5
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # search 命令
    search_parser = subparsers.add_parser("search", help="搜索论文")
    search_parser.add_argument("query", help="搜索关键词")
    search_parser.add_argument("--source", "-s", default="arxiv", choices=["arxiv", "openalex"], help="数据源")
    search_parser.add_argument("--num", "-n", type=int, default=5, help="返回数量")
    
    # generate 命令
    gen_parser = subparsers.add_parser("generate", help="生成蛋白/肽序列")
    gen_parser.add_argument("--type", "-t", default="amp", choices=["amp", "random", "diverse"], help="生成类型")
    gen_parser.add_argument("--length", "-l", default="15-25", help="长度范围 (如 15-25)")
    gen_parser.add_argument("--num", "-n", type=int, default=5, help="生成数量")
    gen_parser.add_argument("--output", "-o", help="输出文件")
    
    # evaluate 命令
    eval_parser = subparsers.add_parser("evaluate", help="评估序列")
    eval_parser.add_argument("sequence", help="蛋白序列")
    eval_parser.add_argument("--amp", action="store_true", help="评估抗菌肽潜力")
    
    # notebook 命令
    nb_parser = subparsers.add_parser("notebook", help="笔记本管理")
    nb_parser.add_argument("action", choices=["list", "create", "search"], help="操作")
    nb_parser.add_argument("--name", "-n", help="笔记本名称")
    nb_parser.add_argument("--query", "-q", help="搜索关键词")
    
    # db 命令
    db_parser = subparsers.add_parser("db", help="数据库查询")
    db_parser.add_argument("db", choices=["uniprot", "pdb"], help="数据库")
    db_parser.add_argument("query", help="查询关键词")
    db_parser.add_argument("--num", "-n", type=int, default=5, help="返回数量")
    
    args = parser.parse_args()
    
    if args.command == "search":
        cmd_search(args)
    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "notebook":
        cmd_notebook(args)
    elif args.command == "db":
        cmd_db(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
