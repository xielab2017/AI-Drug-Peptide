# ResearchHub - 蛋白组学与蛋白设计技能

> 基于西湖大学Cell顶刊41种器官蛋白组图谱研究
> 整合 GitHub 项目与前沿AI蛋白设计

---

## 功能概览

### 🔬 蛋白组学分析 (原有)
- 🔍 论文搜索 (arXiv/OpenAlex)
- 📝 智能摘要
- 🎙️ 音频播客
- 📓 Notebook 管理

### 🧬 蛋白/肽设计 (新增扩展)
- 🧪 蛋白序列生成
- 📊 序列评估 (稳定性/溶解度)
- 🔬 数据库对接 (UniProt/PDB/AlphaFold)
- 🤖 AI模型支持 (ESM-2/ProtGPT2)

---

## 快速开始

### 1. 蛋白序列生成

```python
import sys
sys.path.insert(0, '/Users/liweixie/.openclaw/skills/research-hub')

from design.generator import ProteinGenerator

gen = ProteinGenerator()

# 随机生成
seq = gen.generate_random(50, weighted=True)

# 生成抗菌肽
amps = gen.generate_antimicrobial_peptide(
    length_range=(15, 25),
    num_sequences=10
)

for amp in amps:
    print(f"序列: {amp['sequence']}")
    print(f"电荷: {amp['charge']}, 疏水性: {amp['hydrophobicity']:.2f}")
```

### 2. 序列评估

```python
from design.evaluator import SequenceEvaluator

evaluator = SequenceEvaluator()

# 全面评估
result = evaluator.evaluate("AKLFVMGPELKAL")

print(f"稳定性: {result['stability_score']:.2f}")
print(f"溶解度: {result['solubility_score']:.2f}")

# 抗菌肽潜力
amp_eval = evaluator.evaluate_antimicrobial_potential("KALKKKLLKALKKK")
print(f"AMP评分: {amp_eval['amp_score']:.2f}")
```

### 3. 数据库查询

```python
from databases.protein_db import UniProtClient, PDBClient

# UniProt 搜索
uniprot = UniProtClient()
proteins = uniprot.search("kinase human", size=5)

# PDB 搜索
pdb = PDBClient()
structures = pdb.search("hemoglobin", size=3)
```

### 4. 导出结果

```python
from design.exporter import DesignExporter

exporter = DesignExporter()

# 导出多格式
paths = exporter.export_all(designs, prefix="my_design")
print(paths)
```

---

## 模块结构

```
research-hub/
├── agents/              # 原有模块
│   ├── search_agent.py
│   ├── summary_agent.py
│   └── ...
├── design/              # 新增: 设计模块
│   ├── generator.py     # 序列生成
│   ├── evaluator.py     # 序列评估
│   └── exporter.py     # 结果导出
├── databases/          # 新增: 数据库
│   └── protein_db.py   # UniProt/PDB/AlphaFold
├── models/             # 新增: AI模型
│   └── protein_lm.py   # ESM-2/ProtGPT2
└── storage/            # 原有: 存储
```

---

## 功能矩阵

| 功能 | 状态 | 依赖 |
|------|------|------|
| 论文搜索/摘要 | ✅ | 已有 |
| 蛋白序列生成 | ✅ | 随机/模板 |
| 抗菌肽设计 | ✅ | 随机+约束 |
| 序列评估 | ✅ | 理化性质计算 |
| UniProt查询 | ✅ | requests |
| PDB查询 | ✅ | requests |
| AlphaFold预测 | ✅ | API |
| ESM-2嵌入 | 🔜 | fair-esm |
| ProtGPT2生成 | 🔜 | transformers |

---

## 依赖安装

```bash
# 基础依赖
pip install requests beautifulsoup4

# 设计模块依赖
pip install openpyxl

# AI模型依赖 (可选)
pip install fair-esm transformers torch
```

---

## 数据存储

- 设计结果: `~/.openclaw/data/research-hub/designs/`
- 数据库: `~/.openclaw/data/research-hub/research_hub.db`

---

*版本: v2.0 | 2026-02-23*
