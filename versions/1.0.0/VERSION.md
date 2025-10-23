# AI-Drug Peptide v1.0.0

**发布日期**: 2025-10-05
**Git Commit**: 1f5ea9e
**状态**: 已知问题版本

---

## 版本概述

这是AI-Drug Peptide的初始发布版本，包含完整的生物信息学分析平台功能。

---

## 核心功能

### 1. 智能安装系统
- ✅ 跨平台支持 (macOS, Linux, Windows)
- ✅ 自动依赖管理
- ✅ 环境配置
- ✅ 验证机制

### 2. 统一启动接口
- ✅ 交互式模式
- ✅ 命令行模式
- ✅ 灵活配置
- ✅ 错误处理

### 3. 网页端数据分析操控
- ✅ Prefect集成
- ✅ 实时监控
- ✅ 数据可视化
- ✅ 任务管理

### 4. 分析流程
- ✅ STRING相互作用分析
- ✅ 分子对接预测
- ✅ 保守性分析
- ✅ 结果合并

### 5. 肽段优化模块
- ⚠️ 基础框架（存在已知问题）
- ⚠️ ProGen3接口（模拟实现）
- ⚠️ 稳定性优化（模拟实现）
- ⚠️ 跨物种验证（模拟实现）

---

## 已知问题

### ⚠️ 严重问题

#### 1. 无限递归Bug
- **位置**: `bin/peptide_optim.py:1338`
- **描述**: `_load_config()` 方法调用自身，导致程序崩溃
- **影响**: 肽段优化模块无法正常启动
- **状态**: ❌ 未修复

#### 2. PDB生成逻辑错误
- **位置**: `bin/peptide_optim.py:653`
- **描述**: 错误的布尔逻辑导致原子添加异常
- **影响**: PDB文件生成不正确
- **状态**: ❌ 未修复

#### 3. Pipeline未实现
- **位置**: `bin/peptide_optim.py:1376-1402`
- **描述**: `optimize_peptides()` 只返回空数据
- **影响**: 3轮优化流程无法执行
- **状态**: ❌ 未修复

#### 4. Neo4j硬依赖
- **位置**: `bin/peptide_optim.py:199`
- **描述**: Neo4j不可用时直接崩溃
- **影响**: 无法在没有Neo4j的环境运行
- **状态**: ❌ 未修复

#### 5. 硬编码数据库凭据
- **位置**: `bin/workflow.py:519, 734`
- **描述**: 数据库连接信息硬编码
- **影响**: 安全隐患，无法配置
- **状态**: ❌ 未修复

---

## 使用建议

### ⚠️ 重要提示
此版本的肽段优化模块存在严重Bug，**不建议在生产环境使用**。

### 推荐使用场景
- ✅ 学习和理解项目结构
- ✅ STRING分析功能
- ✅ 分子对接功能
- ✅ 保守性分析功能
- ❌ 肽段优化功能（有Bug）

---

## 安装说明

```bash
# 克隆仓库
git clone https://github.com/xielab2017/AI-Drug-Peptide.git
cd AI-Drug-Peptide

# 切换到1.0.0目录
cd versions/1.0.0

# 安装依赖
python install.py

# 启动（避免使用肽段优化功能）
python launch.py
```

---

## 升级到v1.1.0

如果需要使用肽段优化功能，请升级到v1.1.0：

```bash
# 使用1.1.0版本
cd versions/1.1.0
python install.py
python launch.py --optimization
```

详见：`../1.1.0/VERSION.md` 和 `../1.1.0/PEPTIDE_SCREENING_FIXES.md`

---

## 系统要求

### 最低要求
- Python: 3.8+
- OS: macOS 10.14+, Windows 10+, Ubuntu 18.04+
- RAM: 4GB
- 存储: 2GB

### 推荐配置
- Python: 3.10+
- RAM: 16GB
- 存储: 10GB SSD
- 网络: 稳定的互联网连接

---

## 依赖包

### 必需依赖
```
pandas>=1.5.0
numpy>=1.23.0
biopython>=1.81
requests>=2.28.0
openpyxl>=3.0.0
pyyaml>=6.0
```

### 可选依赖
```
py2neo>=2021.2.3  # Neo4j支持
prefect>=2.0.0     # 工作流支持
plotly>=5.0.0      # 可视化
```

---

## 许可证

MIT License - 详见 LICENSE 文件

---

## 技术支持

- **问题报告**: [GitHub Issues](https://github.com/xielab2017/AI-Drug-Peptide/issues)
- **升级建议**: 使用 v1.1.0 获取Bug修复
- **文档**: 参见项目根目录的README.md

---

## 版本历史

- **v1.0.0** (2025-10-05) - 初始发布版本 [当前]
- **v1.1.0** (2025-10-23) - Bug修复版本 [推荐]

---

**注意**: 此版本仅供参考和学习使用。强烈建议升级到v1.1.0以获取完整功能和Bug修复。
