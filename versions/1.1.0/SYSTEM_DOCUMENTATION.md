# AI-Drug Peptide V1.0 - 系统说明文档

## 📋 项目概述

**AI-Drug Peptide V1.0** 是一个AI驱动的肽类药物开发平台，通过多步骤生物信息学分析管道，从蛋白相互作用网络识别潜在受体，进行分子对接预测，评估跨物种保守性，最终生成优化的肽段候选药物。

## 🏗️ 系统架构

### 核心组件

#### 1. **四步分析流程**
- **Step 1**: STRING相互作用分析 (`bin/step1_string_interaction.py`)
- **Step 2**: 分子对接预测 (`bin/step2_docking_prediction.py`)
- **Step 3**: 保守性分析 (`bin/step3_conservation_check.py`)
- **Step 4**: 结果合并 (`bin/step4_merge_results.py`)

#### 2. **专业分析模块**
- **分泌分析**: `bin/secretion_analysis.py`
- **肽优化**: `bin/peptide_optim.py`
- **工作流管理**: `bin/workflow.py`

#### 3. **用户界面**
- **命令行界面**: `launch.py`
- **Web仪表板**: `dashboard.py`
- **安装脚本**: `install.py`

#### 4. **数据管理**
- **数据获取**: `bin/data_fetch_robust.py`
- **报告生成**: `bin/report_generator.py`
- **可视化**: `bin/visual_dashboard.py`

## 🔧 技术栈

### 后端技术
- **Python 3.8+**: 主要编程语言
- **Prefect**: 工作流管理框架
- **Pandas/NumPy**: 数据处理
- **BioPython**: 生物信息学工具
- **SQLAlchemy**: 数据库ORM
- **Neo4j**: 图数据库

### 前端技术
- **Prefect UI**: Web仪表板
- **Plotly**: 数据可视化
- **HTML/CSS/JavaScript**: 报告生成

### 部署技术
- **Docker**: 容器化部署
- **GitHub Actions**: CI/CD流程
- **PyPI**: Python包分发

## 📊 数据流程

### 输入数据
1. **目标蛋白ID**: 用户指定的蛋白质标识符
2. **配置参数**: 分析参数和阈值设置
3. **数据库连接**: STRING、NCBI、PDB等数据库

### 处理流程
1. **数据获取**: 从多个生物数据库获取相关数据
2. **相互作用分析**: 识别蛋白-蛋白相互作用网络
3. **分子对接**: 预测结合亲和力和结合位点
4. **保守性分析**: 评估跨物种保守性
5. **结果整合**: 综合评分和排序

### 输出结果
1. **分析报告**: JSON、Excel、PDF、HTML格式
2. **可视化图表**: 相互作用网络、保守性热图
3. **优化肽段**: 候选药物分子列表
4. **日志文件**: 详细的执行记录

## 🚀 安装和部署

### 系统要求
- **操作系统**: macOS 10.14+, Windows 10+, Ubuntu 18.04+
- **Python**: 3.8或更高版本
- **内存**: 4GB RAM (推荐8GB+)
- **存储**: 2GB可用空间
- **网络**: 稳定的互联网连接

### 安装方式

#### 1. 一键安装
```bash
# macOS/Linux
curl -fsSL https://raw.githubusercontent.com/xielab2017/AI-Drug-Peptide/main/install.sh | bash

# Windows (PowerShell)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/xielab2017/AI-Drug-Peptide/main/install.ps1" -OutFile "install.ps1"
.\install.ps1
```

#### 2. 手动安装
```bash
git clone https://github.com/xielab2017/AI-Drug-Peptide.git
cd AI-Drug-Peptide
python install.py
```

#### 3. Docker部署
```bash
docker-compose up -d
```

## 🔍 使用指南

### 快速开始
```bash
# 启动应用
python launch.py

# 运行完整工作流
python launch.py --workflow --protein-id THBS4

# 启动Web仪表板
python dashboard.py
```

### 命令行参数
- `--workflow`: 运行完整工作流
- `--steps`: 运行指定步骤
- `--protein-id`: 目标蛋白ID
- `--dashboard`: 启动Web仪表板

### 配置文件
- `config/config.json`: 主配置文件
- `config/config.yaml`: YAML格式配置
- `config/report_config.json`: 报告配置

## 📈 性能优化

### 并行处理
- 多线程数据获取
- 并行分子对接计算
- 分布式工作流执行

### 缓存机制
- 数据库查询缓存
- 计算结果缓存
- 中间文件缓存

### 内存管理
- 大数据集分块处理
- 内存使用监控
- 垃圾回收优化

## 🔒 安全考虑

### 数据安全
- 本地数据处理
- 敏感信息加密
- 访问权限控制

### 网络安全
- HTTPS连接
- API密钥管理
- 防火墙配置

## 🐛 故障排除

### 常见问题
1. **安装失败**: 检查Python版本和网络连接
2. **依赖缺失**: 运行`python install.py --check-deps`
3. **数据库连接**: 检查数据库服务状态
4. **内存不足**: 调整配置文件中的内存限制

### 日志查看
```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log
```

## 📚 开发指南

### 代码结构
```
AI-Drug-Peptide/
├── bin/                 # 核心分析脚本
├── src/                 # 源代码模块
├── config/              # 配置文件
├── data/                # 数据目录
├── logs/                # 日志文件
├── reports/             # 生成的报告
└── tests/               # 测试文件
```

### 开发环境设置
```bash
# 安装开发依赖
python install.py --dev

# 运行测试
python -m pytest tests/

# 代码格式化
black src/
```

### 贡献指南
- 遵循PEP 8编码规范
- 编写单元测试
- 更新文档
- 提交Pull Request

## 📞 技术支持

### 联系方式
- **GitHub Issues**: https://github.com/xielab2017/AI-Drug-Peptide/issues
- **GitHub Discussions**: https://github.com/xielab2017/AI-Drug-Peptide/discussions
- **邮箱**: xielw@gdim.cn

### 文档资源
- **项目文档**: https://github.com/xielab2017/AI-Drug-Peptide
- **API文档**: 查看`docs/`目录
- **示例代码**: 查看`examples/`目录

## 📄 许可证

本项目采用MIT许可证，详见[LICENSE](LICENSE)文件。

## 🙏 致谢

感谢所有贡献者和开源社区的支持！

---

**版本**: V1.0.0  
**最后更新**: 2024年10月5日  
**维护者**: AI-Drug Peptide Team
