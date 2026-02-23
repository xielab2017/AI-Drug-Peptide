# 🧬 AI-Drug-Peptide V2.0

> AI驱动的肽类药物开发平台 - 整合版

[![GitHub Stars](https://img.shields.io/github/stars/xielab2017/AI-Drug-Peptide)](https://github.com/xielab2017/AI-Drug-Peptide)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0-blue)](https://github.com/xielab2017/AI-Drug-Peptide/tree/v2.0)

---

## 🎯 V2.0 新特性

### 整合升级

| 功能 | V1.0 | V2.0 |
|------|-------|-------|
| 蛋白分析 | ✅ 完整流程 | ✅ 保留 |
| AI设计 | ❌ 无 | ✅ ESM-2/ProtGPT2 |
| 文献搜索 | ❌ 无 | ✅ arXiv/OpenAlex |
| 网页界面 | Prefect复杂 | ✅ 轻量Flask |
| 依赖要求 | 高(需安装软件) | ✅ 零依赖可用 |

---

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/xielab2017/AI-Drug-Peptide.git
cd AI-Drug-Peptide

# 切换到V2.0分支
git checkout v2.0

# 安装依赖
pip install -r requirements.txt

# 安装ResearchHub依赖
pip install -r research_hub/requirements.txt
```

### 使用方式

#### 方式一：交互式菜单

```bash
python launch_v2.py
```

#### 方式二：命令行

```bash
# AI蛋白设计
python -c "
import sys
sys.path.insert(0, 'research_hub')
from research_hub.design.generator import ProteinGenerator
gen = ProteinGenerator()
amps = gen.generate_antimicrobial_peptide((15,25), 5)
for a in amps: print(a['sequence'])
"

# 文献搜索
python -c "
import sys
sys.path.insert(0, 'research_hub')
from research_hub.agents.search_agent import SearchAgent
s = SearchAgent()
for p in s.search_arxiv('protein design', 3): print(p['title'])
"
```

#### 方式三：网页界面

```bash
python research_hub/web/app.py
# 浏览器访问 http://localhost:5000
```

---

## 📦 核心功能

### V1.0 传统分析（保留）

- STRING蛋白互作分析
- 分子对接预测
- 跨物种保守性分析
- 多格式报告生成

### V2.0 新增功能

| 功能 | 说明 |
|------|------|
| 🧪 AI蛋白设计 | 生成抗菌肽、随机蛋白、多样化集合 |
| 📊 序列评估 | 稳定性、溶解度、等电点预测 |
| 📖 文献搜索 | arXiv/OpenAlex学术论文 |
| 🗣️ 语音播客 | 论文转语音 |
| 📓 笔记本 | 文献管理+全文搜索 |

---

## 📁 项目结构

```
AI-Drug-Peptide/
├── v1/                      # V1.0 完整版
│   ├── bin/                 # 分析脚本
│   ├── src/                 # 源代码
│   └── ...
├── research_hub/            # V2.0 新增
│   ├── agents/              # 文献代理
│   ├── design/              # AI设计模块
│   ├── databases/           # 数据库API
│   ├── models/             # AI模型
│   └── web/                 # 网页界面
├── launch_v2.py            # V2.0启动器
└── README.md
```

---

## 🔧 版本选择

| 需求 | 推荐版本 |
|------|----------|
| 完整分析流程(STRING/对接) | V1.0 (master分支) |
| AI蛋白设计/轻量使用 | V2.0 (v2.0分支) |
| 快速体验 | 网页界面 |

---

## 📋 环境要求

### V2.0 基础版

- Python 3.8+
- requests
- beautifulsoup4

### V2.0 完整版（可选）

- Flask (网页界面)
- fair-esm (AI模型)
- transformers (LLM)

---

## 📖 文档

- [V2.0 快速指南](docs/V2_QUICK_START.md)
- [V1.0 完整文档](docs/)
- [API参考](docs/API.md)

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

## 📄 License

MIT License

---

*让药物研发更简单* 🧬
