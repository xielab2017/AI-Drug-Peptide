# 🧬 AI-Drug-Peptide V2.0

> AI驱动的肽类药物开发平台 - 增强版

[![GitHub Stars](https://img.shields.io/github/stars/xielab2017/AI-Drug-Peptide)](https://github.com/xielab2017/AI-Drug-Peptide)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0-blue)](https://github.com/xielab2017/AI-Drug-Peptide/tree/v2.0)

---

## 🎯 V2.0 简介

V2.0 是 AI-Drug-Peptide 的增强版本，在 V1.0 基础上整合了前沿的 AI 技术，提供更强大的蛋白/肽设计能力。

### V1.0 vs V2.0 对比

| 功能 | V1.0 | V2.0 |
|------|-------|-------|
| **分析流程** | ✅ 完整(STRING/对接/保守性) | ✅ 保留 |
| **AI蛋白设计** | ❌ 无 | ✅ ESM-2/ProtGPT2 |
| **文献搜索** | ❌ 无 | ✅ arXiv/OpenAlex |
| **网页界面** | Prefect复杂 | ✅ 轻量Flask |
| **依赖要求** | 高(需安装软件) | ✅ 零依赖可用 |

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
python research_hub/research_hub.py generate --type amp --length 15-25 --num 10

# 文献搜索
python research_hub/research_hub.py search "protein design"
```

#### 方式三：网页界面

```bash
python research_hub/web/app.py
# 浏览器访问 http://localhost:5000
```

---

## 📦 核心功能

### V1.0 传统分析（需额外安装）

- STRING 蛋白互作分析
- 分子对接预测 (AutoDock Vina)
- 跨物种保守性分析
- 多格式报告生成

### V2.0 新增功能

| 功能 | 说明 |
|------|------|
| 🧪 **AI蛋白设计** | 抗菌肽生成、随机蛋白、多样化集合 |
| 📊 **序列评估** | 稳定性、溶解度、等电点预测 |
| 📖 **文献搜索** | arXiv/OpenAlex 学术论文 |
| 🗣️ **语音播客** | 论文转语音 |
| 📓 **笔记本** | 文献管理 + 全文搜索 |
| 🔬 **数据库** | UniProt / PDB / AlphaFold 查询 |

---

## 📋 环境要求

### V2.0 基础版

- Python 3.8+
- requests
- beautifulsoup4

### V2.0 完整版

```bash
# 网页界面
pip install flask

# AI模型（可选）
pip install fair-esm transformers torch
```

---

## 📖 详细文档

- [V2.0 使用指南](research_hub/RESEARCHHUB-USER-GUIDE.md)
- [V1.0 完整文档](docs/)
- [原始论文](https://doi.org/...)

---

## 🔧 版本选择

| 需求 | 推荐 |
|------|------|
| 完整分析流程(STRING/对接) | V1.0 (master分支) |
| AI蛋白设计/轻量使用 | **V2.0 (v2.0分支)** |
| 快速体验 | 网页界面 |

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 License

MIT License

---

## 📮 联系

- GitHub: https://github.com/xielab2017/AI-Drug-Peptide
- 官网: http://ai-drug-peptide.xielab.net

---

*让药物研发更简单* 🧬
