# AI-Drug-Peptide

AI驱动的蛋白质/肽段设计平台

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

```python
from protein_design import ProteinDesigner
from peptide_design import PeptideDesigner

# 蛋白质设计
designer = ProteinDesigner()
sequences = designer.generate(length=100, num_sequences=10)

# 肽段设计
peptide_designer = PeptideDesigner(target='antimicrobial')
peptides = peptide_designer.design(length_range=(10, 30))
```

## 模块

- protein_design/ - 蛋白质设计
- peptide_design/ - 肽段设计
- structure/ - 结构预测
- literature/ - 文献检索
- web/ - 网页界面
