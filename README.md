# 🧬 AI-Drug-Peptide

> AI驱动的肽类药物开发平台

[![GitHub Stars](https://img.shields.io/github/stars/xielab2017/AI-Drug-Peptide)](https://github.com/xielab2017/AI-Drug-Peptide)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## ⚡ 选择版本

| 版本 | 说明 | 安装 |
|------|------|------|
| **[V2.0 (推荐)](https://github.com/xielab2017/AI-Drug-Peptide/tree/v2.0)** | AI增强版，零依赖，网页界面 | 简单 |
| [V1.0 (完整版)](https://github.com/xielab2017/AI-Drug-Peptide/tree/main) | 传统分析流程，STRING/对接 | 复杂 |

---

## 🚀 V2.0 快速开始（推荐）

### 方式一：网页版（无需安装）

```bash
# 克隆
git clone https://github.com/xielab2017/AI-Drug-Peptide.git
cd AI-Drug-Peptide

# 切换V2.0分支
git checkout v2.0

# 安装依赖
pip install flask requests beautifulsoup4

# 启动
python research_hub/web/app.py

# 浏览器访问 http://localhost:5000
```

### 方式二：命令行版

```bash
python research_hub/research_hub.py --help

# 生成抗菌肽
python research_hub/research_hub.py generate --type amp --length 15-25 --num 10

# 搜索论文
python research_hub/research_hub.py search "protein design"
```

---

## 📦 V2.0 核心功能

| 功能 | 说明 |
|------|------|
| 🧪 **AI蛋白设计** | 抗菌肽生成、随机蛋白、多样化集合 |
| 📊 **序列评估** | 稳定性、溶解度、等电点预测 |
| 📖 **文献搜索** | arXiv/OpenAlex 学术论文 |
| 🌐 **网页界面** | 交互式可视化 |
| 📓 **笔记本** | 文献管理 + 全文搜索 |
| 🔬 **数据库** | UniProt / PDB / AlphaFold |

---

## 💻 V1.0 完整版（需要安装额外软件）

V1.0 包含完整的生物信息学分析流程：

- STRING 蛋白互作分析
- 分子对接预测 (AutoDock Vina)
- 跨物种保守性分析
- 多格式报告生成

详细安装说明见 [INSTALLATION.md](INSTALLATION.md)

---

## 📖 文档

- [V2.0 使用指南](https://github.com/xielab2017/AI-Drug-Peptide/tree/v2.0/research_hub/RESEARCHHUB-USER-GUIDE.md)
- [V1.0 安装文档](INSTALLATION.md)
- [V1.0 使用文档](USAGE.md)

---

## 📮 联系

- GitHub: https://github.com/xielab2017/AI-Drug-Peptide
- 官网: http://ai-drug-peptide.xielab.net

---

*让药物研发更简单* 🧬
