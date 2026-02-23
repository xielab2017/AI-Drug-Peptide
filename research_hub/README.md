# 🧬 ResearchHub v3.0

> 学术文献研究与AI蛋白/肽设计平台

[![GitHub Stars](https://img.shields.io/github/stars/xielab2017/research-hub?style=social)](https://github.com/xielab2017/research-hub)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 🎯 简介

ResearchHub 是一个 **一站式学术研究AI平台**，提供两种使用方式：

| 模式 | 特点 | 适合 |
|------|------|------|
| 🌐 网页版 | 无需安装，浏览器直接用 | 快速体验、日常使用 |
| ⌨️ 命令行版 | 功能完整，可定制 | 开发者、高级用户 |

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 🔍 论文搜索 | arXiv、OpenAlex 学术论文 |
| 📝 智能摘要 | AI 生成论文摘要 |
| 🎙️ 语音播客 | 文本转语音 |
| 📓 文献管理 | 笔记本 + 全文搜索 |
| 🧪 AI 蛋白设计 | 抗菌肽 + 序列评估 |
| 🔬 数据库对接 | UniProt、PDB、AlphaFold |

---

## 🚀 快速开始

### 方式一：网页版（推荐）

```bash
# 1. 安装依赖
pip install flask requests beautifulsoup4 openpyxl

# 2. 克隆项目
git clone https://github.com/xielab2017/research-hub.git
cd research-hub

# 3. 启动服务
python web/app.py

# 4. 打开浏览器
# 本地访问: http://localhost:5000
# 局域网访问: http://你的IP:5000
```

### 方式二：命令行版

```bash
# 1. 安装依赖
pip install requests beautifulsoup4 openpyxl

# 2. 克隆项目
git clone https://github.com/xielab2017/research-hub.git
cd research-hub

# 3. 使用命令
python -m research_hub --help
```

---

## 📖 详细使用

### 网页版功能

打开 http://localhost:5000 即可看到：

```
┌─────────────────────────────────────────┐
│           🧬 ResearchHub               │
├─────────────────────────────────────────┤
│  [🧪 蛋白设计] [🔍 论文搜索] [📓 笔记本] │
└─────────────────────────────────────────┘

🧪 蛋白设计
├── 抗菌肽设计 → 输入长度、数量 → 生成
├── 序列评估 → 稳定性、溶解度预测
└── 结果导出 → JSON/CSV/FASTA

🔍 论文搜索
├── arXiv 搜索 → 输入关键词
├── OpenAlex 搜索 → 多学科
└── 结果展示 → 标题、作者、摘要

📓 笔记本
├── 创建笔记本
├── 添加论文
└── 全文搜索
```

### 命令行版使用

```bash
# 搜索论文
python -m research_hub search "machine learning" --source arxiv --num 5

# 生成抗菌肽
python -m research_hub generate --type amp --length 15-25 --num 10

# 创建笔记本
python -m research_hub notebook create "我的研究"

# 评估序列
python -m research_hub evaluate "KALKKKLLKALKKK"
```

### Python API

```python
import sys
sys.path.insert(0, 'research-hub')

# 1. 搜索论文
from agents.search_agent import SearchAgent
search = SearchAgent()
papers = search.search_arxiv("protein design", max_results=5)

# 2. 设计抗菌肽
from design.generator import ProteinGenerator
from design.evaluator import SequenceEvaluator

gen = ProteinGenerator()
amps = gen.generate_antimicrobial_peptide(length_range=(15, 25), num_sequences=10)

eval = SequenceEvaluator()
for amp in amps:
    result = eval.evaluate_antimicrobial_potential(amp['sequence'])
    print(f"{amp['sequence']}: 评分={result['amp_score']:.2f}")

# 3. 数据库查询
from databases.protein_db import UniProtClient
uniprot = UniProtClient()
proteins = uniprot.search("kinase", size=5)
```

---

## 📦 安装

### 基础依赖

```bash
pip install -r requirements.txt
```

### 可选依赖

```bash
# AI 模型（高级功能）
pip install fair-esm transformers torch

# 网页界面
pip install flask
```

---

## 🏗️ 项目结构

```
research-hub/
├── agents/              # 论文搜索代理
│   ├── search_agent.py
│   ├── summary_agent.py
│   └── ...
├── design/              # 蛋白设计模块
│   ├── generator.py     # 序列生成
│   ├── evaluator.py     # 序列评估
│   └── exporter.py      # 结果导出
├── databases/           # 数据库API
│   └── protein_db.py   # UniProt/PDB
├── models/              # AI模型
│   └── protein_lm.py   # ESM-2/ProtGPT2
├── web/                 # 网页界面
│   └── app.py
├── storage/             # 本地存储
│   └── database.py
└── research_hub.py      # 命令行入口
```

---

## 💡 创新亮点

1. **双模式** - 网页/命令行，满足不同场景
2. **AI 蛋白设计** - 智能生成 + 评估筛选
3. **一站式研究** - 搜论文→读摘要→做笔记
4. **零门槛** - 不需要生物信息学背景
5. **开源免费** - 社区共建

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

```bash
# 1. Fork 项目
# 2. 创建分支
git checkout -b feature/your-feature
# 3. 提交
git commit -m "Add your feature"
# 4. 推送
git push origin feature/your-feature
```

---

## 📄 License

MIT License - 自由使用、修改和分发

---

## 🙏 致谢

- 基于 [Roshk01/Research_summary_AI](https://github.com/Roshk01/Research_summary_AI)
- 基于 [sivasaikakarla/Research-Paper-Summarization](https://github.com/sivasaikakarla/Research-Paper-Summarization)
- ESM-2: [facebookresearch/esm](https://github.com/facebookresearch/esm)

---

## 📮 联系我

- GitHub: https://github.com/xielab2017/research-hub
- 邮箱: xielw@gdim.cn

---

*让科研更简单* 🧬
