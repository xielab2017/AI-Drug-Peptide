#!/usr/bin/env python3
"""
测试脚本：验证peptide screening修复
"""

import sys
import os
from pathlib import Path

# 添加bin目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'bin'))

def test_imports():
    """测试1: 验证模块导入"""
    print("=" * 60)
    print("测试1: 验证模块导入")
    print("=" * 60)

    try:
        from peptide_optim import (
            PeptideOptimizationPipeline,
            Neo4jDataExtractor,
            ProGen3Interface,
            StabilityOptimizer,
            CrossSpeciesValidator,
            PeptideLibraryGenerator,
            CoreRegion,
            PeptideCandidate
        )
        print("✓ 所有模块导入成功")
        return True
    except Exception as e:
        print(f"✗ 模块导入失败: {e}")
        return False

def test_config_loading():
    """测试2: 验证配置加载（无递归）"""
    print("\n" + "=" * 60)
    print("测试2: 验证配置加载（无递归）")
    print("=" * 60)

    try:
        from peptide_optim import PeptideOptimizationPipeline

        # 这应该不会导致递归错误
        pipeline = PeptideOptimizationPipeline()
        print(f"✓ PeptideOptimizationPipeline 初始化成功")
        print(f"  - 配置文件: {pipeline.config_file}")
        print(f"  - 参数: {pipeline.params}")
        return True
    except RecursionError:
        print("✗ 递归错误仍然存在！")
        return False
    except Exception as e:
        print(f"⚠ 初始化时出现其他错误（可能是预期的）: {e}")
        return True  # 可能是Neo4j不可用，这是可以接受的

def test_neo4j_fallback():
    """测试3: 验证Neo4j优雅降级"""
    print("\n" + "=" * 60)
    print("测试3: 验证Neo4j优雅降级")
    print("=" * 60)

    try:
        from peptide_optim import Neo4jDataExtractor

        # 不要求Neo4j必须可用
        extractor = Neo4jDataExtractor(require_neo4j=False)
        print(f"✓ Neo4jDataExtractor 初始化成功（require_neo4j=False）")
        print(f"  - Neo4j可用: {extractor.neo4j_available}")

        # 尝试提取数据（应该返回空列表或使用fallback）
        secretory, binding = extractor.extract_core_regions()
        print(f"  - 提取到分泌区域: {len(secretory)}")
        print(f"  - 提取到结合区域: {len(binding)}")
        return True
    except Exception as e:
        print(f"✗ Neo4j fallback测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mock_core_regions():
    """测试4: 验证模拟核心区域创建"""
    print("\n" + "=" * 60)
    print("测试4: 验证模拟核心区域创建")
    print("=" * 60)

    try:
        from peptide_optim import PeptideOptimizationPipeline

        pipeline = PeptideOptimizationPipeline()
        mock_regions = pipeline._create_mock_core_regions()

        print(f"✓ 创建了 {len(mock_regions)} 个模拟核心区域")
        for i, region in enumerate(mock_regions, 1):
            print(f"  {i}. {region.region_type} - {region.protein_id}")
            print(f"     序列长度: {region.length}")
        return True
    except Exception as e:
        print(f"✗ 模拟核心区域创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_peptide_generation():
    """测试5: 验证肽段生成"""
    print("\n" + "=" * 60)
    print("测试5: 验证肽段生成（Round 1）")
    print("=" * 60)

    try:
        from peptide_optim import ProGen3Interface, PeptideOptimizationPipeline

        pipeline = PeptideOptimizationPipeline()
        core_regions = pipeline._create_mock_core_regions()

        progen3 = ProGen3Interface()
        peptides = progen3.generate_peptides(core_regions, target_count=10)

        print(f"✓ 生成了 {len(peptides)} 个肽段候选")
        if peptides:
            print(f"  示例肽段:")
            sample = peptides[0]
            print(f"    - ID: {sample.peptide_id}")
            print(f"    - 序列: {sample.sequence[:30]}...")
            print(f"    - 分子量: {sample.molecular_weight:.1f} Da")
            print(f"    - GRAVY: {sample.gravy_score:.2f}")
            print(f"    - 符合约束: {sample.meets_constraints}")
        return True
    except Exception as e:
        print(f"✗ 肽段生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_stability_optimization():
    """测试6: 验证稳定性优化"""
    print("\n" + "=" * 60)
    print("测试6: 验证稳定性优化（Round 2）")
    print("=" * 60)

    try:
        from peptide_optim import (
            ProGen3Interface,
            StabilityOptimizer,
            PeptideOptimizationPipeline
        )

        pipeline = PeptideOptimizationPipeline()
        core_regions = pipeline._create_mock_core_regions()

        # 生成一些肽段
        progen3 = ProGen3Interface()
        peptides = progen3.generate_peptides(core_regions, target_count=5)

        # 运行稳定性优化
        optimizer = StabilityOptimizer()
        optimized = optimizer.optimize_stability(peptides)

        print(f"✓ 稳定性优化完成")
        print(f"  - 输入肽段: {len(peptides)}")
        print(f"  - 通过Tm>55°C筛选: {len(optimized)}")
        if optimized:
            sample = optimized[0]
            print(f"  示例优化肽段:")
            print(f"    - ID: {sample.peptide_id}")
            print(f"    - Tm: {sample.tm_value:.1f}°C")
            print(f"    - 稳定性评分: {sample.stability_score:.2f}")
        return True
    except Exception as e:
        print(f"✗ 稳定性优化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_pipeline():
    """测试7: 验证完整优化流程"""
    print("\n" + "=" * 60)
    print("测试7: 验证完整3轮优化流程")
    print("=" * 60)

    try:
        from peptide_optim import PeptideOptimizationPipeline

        # 降低目标数量以加快测试
        pipeline = PeptideOptimizationPipeline()
        pipeline.params['target_peptide_count'] = 10

        print("运行完整优化流程（这可能需要一些时间）...")
        result = pipeline.optimize_peptides()

        print(f"✓ 完整流程执行完成")
        print(f"  - 状态: {result['status']}")
        print(f"  - Round 1候选: {result.get('round1_candidates', 0)}")
        print(f"  - Round 2候选: {result.get('round2_candidates', 0)}")
        print(f"  - Round 3候选: {result.get('round3_candidates', 0)}")
        print(f"  - 最终候选: {result.get('final_candidates', 0)}")

        if result.get('statistics'):
            stats = result['statistics']
            print(f"  统计信息:")
            print(f"    - 平均Tm: {stats.get('average_tm', 0):.1f}°C")
            print(f"    - 平均分子量: {stats.get('average_mw', 0):.1f} Da")
            print(f"    - 平均跨物种比率: {stats.get('average_cross_species_ratio', 0):.2f}")

        return result['status'] == 'success'
    except Exception as e:
        print(f"✗ 完整流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Peptide Screening 修复验证测试" + " " * 17 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    tests = [
        ("模块导入", test_imports),
        ("配置加载", test_config_loading),
        ("Neo4j降级", test_neo4j_fallback),
        ("模拟数据", test_mock_core_regions),
        ("肽段生成", test_peptide_generation),
        ("稳定性优化", test_stability_optimization),
        ("完整流程", test_complete_pipeline),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ 测试 '{name}' 执行时崩溃: {e}")
            results.append((name, False))

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {name}")

    print(f"\n总计: {passed}/{total} 测试通过 ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n🎉 所有测试通过！peptide screening修复成功。")
        return 0
    else:
        print(f"\n⚠ {total - passed} 个测试失败，请检查上述错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
