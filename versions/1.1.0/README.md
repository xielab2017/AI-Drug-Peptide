# AI-Drug Peptide V1.0

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)](https://github.com/xielab2017/AI-Drug-Peptide)

AI驱动的肽类药物开发平台 - 通过多步骤生物信息学分析管道，从蛋白相互作用网络识别潜在受体，进行分子对接预测，评估跨物种保守性，最终生成优化的肽段候选药物。

## 🚀 快速安装

### 一键安装（推荐）

```bash
# macOS/Linux
curl -fsSL https://raw.githubusercontent.com/xielab2017/AI-Drug-Peptide/main/install.sh | bash

# Windows (PowerShell)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/xielab2017/AI-Drug-Peptide/main/install.ps1" -OutFile "install.ps1"
.\install.ps1
```

### 手动安装

#### 1. 克隆仓库
```bash
git clone https://github.com/xielab2017/AI-Drug-Peptide.git
cd AI-Drug-Peptide
```

#### 2. 运行安装脚本
```bash
# macOS/Linux
python install.py

# Windows
python install.py
```

#### 3. 启动应用
```bash
python launch.py
```

## 📦 系统要求

### 最低要求
- **Python**: 3.8+ (推荐 3.9+)
- **操作系统**: macOS 10.14+, Windows 10+, Ubuntu 18.04+
- **内存**: 4GB RAM (推荐 8GB+)
- **存储**: 2GB 可用空间

### 推荐配置
- **Python**: 3.10+
- **内存**: 16GB RAM
- **存储**: 10GB SSD
- **网络**: 稳定的互联网连接

## 🔧 核心功能

### 1. 智能安装系统
- ✅ **跨平台支持**: 自动检测 macOS、Linux、Windows 系统
- ✅ **依赖管理**: 自动安装 Python 包、生物信息学工具
- ✅ **环境配置**: 自动创建虚拟环境和配置文件
- ✅ **验证机制**: 安装后自动验证环境正确性

### 2. 统一启动接口
- ✅ **交互式模式**: 友好的菜单界面
- ✅ **命令行模式**: 支持脚本化和批处理
- ✅ **灵活配置**: 支持多种运行模式和参数
- ✅ **错误处理**: 完善的错误检查和恢复机制

### 3. 网页端数据分析操控
- ✅ **Prefect集成**: 基于Prefect的工作流管理
- ✅ **实时监控**: 分析进度实时显示
- ✅ **数据可视化**: 交互式图表和仪表板
- ✅ **任务管理**: 任务调度、暂停、恢复、重试

## 🛠️ 使用方法

### 交互式模式
```bash
python launch.py
```

### 命令行模式
```bash
# 运行完整工作流
python launch.py --workflow --protein-id THBS4

# 运行特定步骤
python launch.py --steps step1,step2 --protein-id THBS4

# 分泌分析
python launch.py --secretion --protein-id THBS4

# 肽优化
python launch.py --optimization --protein-id THBS4
```

### 网页端操控
```bash
python dashboard.py
```
访问 `http://localhost:8080` 查看Prefect仪表板

## 📊 分析流程

1. **STRING相互作用分析** - 从STRING数据库获取蛋白相互作用网络
2. **分子对接预测** - 使用AutoDock Vina进行分子对接
3. **保守性分析** - 跨物种序列比对和保守性评估
4. **结果合并** - 整合所有分析结果，生成综合评分

## 📁 项目结构

```
AI-Drug-Peptide/
├── 🚀 install.py           # 智能安装脚本
├── 🎯 launch.py            # 主启动脚本
├── 📊 dashboard.py         # Prefect网页端数据分析操控
├── 📖 README.md            # 项目说明
├── 📄 LICENSE              # MIT许可证
├── 🔧 setup.py             # Python包安装配置
├── 📦 requirements.txt     # Python依赖
│
├── 📁 bin/                 # 🔬 核心分析脚本
├── 📁 src/                 # 💻 源代码模块
├── 📁 config/              # ⚙️ 配置文件
├── 📁 data/                # 💾 数据目录
├── 📁 logs/                # 📝 日志文件
├── 📁 reports/             # 📊 生成的报告
├── 📁 scripts/             # 🔧 辅助脚本
├── 📁 docs/                # 📚 详细文档
└── 📁 installers/          # 📦 各平台安装脚本
```

## 🔍 输出结果

### 报告文件
- **JSON格式**: `./reports/analysis_report_THBS4_*.json`
- **Excel格式**: `./reports/analysis_report_THBS4_*.xlsx`
- **PDF格式**: `./reports/analysis_report_THBS4_*.pdf`
- **HTML格式**: `./reports/analysis_report_THBS4_*.html`

### 关键指标
- **结合能**: 负值越小表示结合越强
- **保守性**: 0-1之间，值越高表示越保守
- **置信度**: STRING数据库的置信度评分
- **综合评分**: 综合考虑各项指标的最终评分

## ⚙️ 配置说明

### 环境变量
```bash
# 数据库配置
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=peptide_research
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=password

# Neo4j配置
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=password
```

## 🚀 高级功能

### 1. 分泌分析
- 预测蛋白分泌信号
- 分析跨膜结构
- 评估组织特异性

### 2. 肽优化
- 基于AI的肽段设计
- 稳定性预测
- 毒性评估

### 3. 报告生成
- 多格式输出（JSON、Excel、PDF、HTML）
- 交互式图表
- 自动报告模板

## 🔧 故障排除

### 常见问题

1. **安装失败**
   ```bash
   # 检查Python版本
   python --version
   
   # 检查网络连接
   ping pypi.org
   
   # 重新安装
   python install.py --force
   ```

2. **依赖缺失**
   ```bash
   # 检查依赖
   python install.py --check-deps
   
   # 手动安装
   pip install -r requirements.txt
   ```

3. **数据库连接问题**
   ```bash
   # 检查Docker状态
   docker ps
   
   # 重启Neo4j
   docker restart neo4j
   ```

### 日志查看
```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log
```

## 📚 文档

- [快速开始指南](docs/QUICK_START.md)
- [配置说明](docs/CONFIGURATION.md)
- [API文档](docs/API.md)
- [故障排除](docs/TROUBLESHOOTING.md)

## 🤝 贡献

我们欢迎各种形式的贡献！

### 开发环境设置
```bash
# 克隆项目
git clone https://github.com/xielab2017/AI-Drug-Peptide.git
cd AI-Drug-Peptide

# 安装开发依赖
python install.py --dev

# 运行测试
python -m pytest tests/
```

### 代码规范
- 使用Black进行代码格式化
- 使用flake8进行代码检查
- 遵循PEP 8编码规范

## 📄 许可证

本项目采用 [MIT许可证](LICENSE) - 详见LICENSE文件。

## 📞 支持

- **问题报告**: [GitHub Issues](https://github.com/your-username/AI-Drug-Peptide/issues)
- **功能请求**: [GitHub Discussions](https://github.com/your-username/AI-Drug-Peptide/discussions)
- **文档改进**: 提交Pull Request

## 🙏 致谢

感谢所有贡献者和开源社区的支持！

---

**注意**: 这是一个研究项目，仅供学术研究使用。在生产环境中使用前，请确保所有依赖工具已正确安装和配置。
