# 🔬 ResearchHub 使用指南

> 学术文献研究与AI蛋白/肽设计工具

---

## 🎯 这是什么？

ResearchHub 是一个 **一站式学术研究AI平台**，可以帮你：

| 功能 | 说明 |
|------|------|
| 🔍 **论文搜索** | 从arXiv、OpenAlex搜索学术论文 |
| 📝 **智能摘要** | 用AI总结论文要点 |
| 🎙️ **语音播客** | 把论文变成音频随时听 |
| 📓 **文献管理** | 创建笔记本保存论文 |
| 🧪 **AI蛋白设计** | 用AI设计新型蛋白/肽序列 |

---

## 🚀 三种使用方式

### 方式一：网页界面（推荐）

**无需安装，浏览器直接使用！**

```bash
# 安装依赖
pip install flask requests beautifulsoup4

# 启动服务
python -m research_hub.web.app

# 然后打开浏览器访问
http://localhost:5000
```

| 模式 | 命令 | 访问地址 |
|------|------|----------|
| 本地 | `python web/app.py --local` | http://localhost:5000 |
| 开放 | `python web/app.py --port 8080` | http://你的IP:8080 |

---

### 方式二：Python代码

```python
import sys
sys.path.insert(0, '/path/to/research-hub')

# ===== 1. 搜索论文 =====
from agents.search_agent import SearchAgent

search = SearchAgent()
papers = search.search_arxiv("machine learning", max_results=5)

for p in papers:
    print(f"📄 {p['title'][:60]}...")

# ===== 2. 设计抗菌肽 =====
from design.generator import ProteinGenerator
from design.evaluator import SequenceEvaluator

gen = ProteinGenerator()
amps = gen.generate_antimicrobial_peptide(
    length_range=(15, 25),  # 长度范围
    num_sequences=5          # 生成数量
)

eval = SequenceEvaluator()
for amp in amps:
    result = eval.evaluate_antimicrobial_potential(amp['sequence'])
    print(f"{amp['sequence']} → 评分: {result['amp_score']:.2f}")
```

---

### 方式三：命令行

```bash
# 搜索论文
python -m research_hub search "protein design"

# 生成抗菌肽
python -m research_hub generate --type amp --num 10
```

---

## 🧪 核心功能详解

### 1. AI蛋白/肽设计

```python
# 抗菌肽设计
amps = gen.generate_antimicrobial_peptide(
    length_range=(15, 30),
    num_sequences=10
)

# 随机蛋白
seq = gen.generate_random(length=100, weighted=True)

# 多样化集合
seqs = gen.generate_diverse_set(length=50, num_sequences=20)
```

### 2. 序列评估

```python
evaluator = SequenceEvaluator()

# 全面评估
result = evaluator.evaluate("AKLFVMGPELKAL")
print(f"稳定性: {result['stability_score']:.2f}")
print(f"溶解度: {result['solubility_score']:.2f}")

# 抗菌肽潜力
amp_result = evaluator.evaluate_antimicrobial_potential("KALKKKLLKALKKK")
print(f"AMP评分: {amp_result['amp_score']:.2f}")
```

### 3. 数据库对接

```python
from databases.protein_db import UniProtClient, PDBClient

# UniProt搜索
uniprot = UniProtClient()
proteins = uniprot.search("kinase human", size=5)

# PDB搜索
pdb = PDBClient()
structures = pdb.search("hemoglobin", size=3)
```

### 4. 文献管理

```python
from storage.database import Database

db = Database()

# 创建笔记本
nb_id = db.create_notebook("我的研究")

# 添加论文
db.add_paper(nb_id, {
    "title": "论文标题",
    "authors": ["作者"],
    "summary": "摘要"
})

# 搜索
results = db.search("关键词")
```

---

## 📊 网页功能一览

| 功能 | 说明 |
|------|------|
| 🧪 蛋白设计 | 选择类型、长度、数量，一键生成 |
| 🔍 论文搜索 | 输入关键词，搜索arXiv/OpenAlex |
| 📓 笔记本 | 创建和管理研究笔记本 |

---

## 💡 创新亮点

1. **一站式研究** - 搜论文→读摘要→做笔记→生成播客
2. **AI蛋白设计** - 智能生成+评估筛选
3. **双模式** - 本地/网页两种使用方式
4. **零门槛** - 不需要生物信息学背景

---

## 📦 安装

```bash
# 基础依赖
pip install flask requests beautifulsoup4 openpyxl

# （可选）AI模型
pip install fair-esm transformers torch
```

---

## 📁 数据存储

- 笔记本数据：`~/.openclaw/data/research-hub/`
- 导出的设计：`~/.openclaw/data/research-hub/designs/`

---

## ❓ 常见问题

**Q: 需要编程基础吗？**
A: 网页界面完全不需要，会用浏览器即可

**Q: 可以设计什么样的蛋白？**
A: 目前支持：抗菌肽、随机蛋白、模板变体

**Q: 数据来源可靠吗？**
A: 来自UniProt、PDB等官方数据库

---

## 🆘 支持

有问题请联系开发团队

---

*让科研更简单*
