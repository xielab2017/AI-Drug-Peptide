# AI-Drug Peptide - 版本管理

本目录包含AI-Drug Peptide项目的不同版本。每个版本都是完整、独立的代码副本。

---

## 📁 版本目录结构

```
versions/
├── README.md          # 本文件
├── 1.0.0/             # v1.0.0 初始版本（已知问题）
│   ├── VERSION.md     # 版本说明
│   ├── bin/           # 核心脚本
│   ├── config/        # 配置文件
│   └── ...
└── 1.1.0/             # v1.1.0 Bug修复版本（推荐）
    ├── VERSION.md     # 版本说明
    ├── PEPTIDE_SCREENING_FIXES.md  # 详细修复报告
    ├── .env.example   # 环境变量模板
    ├── bin/           # 核心脚本（已修复）
    ├── config/        # 配置文件
    └── test_peptide_screening_fixes.py  # 测试套件
```

---

## 🔖 版本对比

| 特性 | v1.0.0 | v1.1.0 |
|------|--------|--------|
| **发布日期** | 2025-10-05 | 2025-10-23 |
| **状态** | ⚠️ 已知问题 | ✅ 推荐使用 |
| **Git Commit** | 1f5ea9e | 31060ea |
| | | |
| **核心功能** | | |
| STRING分析 | ✅ | ✅ |
| 分子对接 | ✅ | ✅ |
| 保守性分析 | ✅ | ✅ |
| 肽段优化 | ❌ 有Bug | ✅ 完整实现 |
| | | |
| **关键Bug** | | |
| 无限递归Bug | ❌ 存在 | ✅ 已修复 |
| PDB生成错误 | ❌ 存在 | ✅ 已修复 |
| Pipeline未实现 | ❌ 存在 | ✅ 已实现 |
| Neo4j硬依赖 | ❌ 存在 | ✅ 已修复 |
| 硬编码凭据 | ❌ 存在 | ✅ 已修复 |
| | | |
| **新增功能** | | |
| 环境变量配置 | ❌ | ✅ |
| Neo4j可选依赖 | ❌ | ✅ |
| 综合测试套件 | ❌ | ✅ |
| 详细修复文档 | ❌ | ✅ |
| | | |
| **测试通过率** | 未测试 | 100% (7/7) |

---

## 🚀 快速开始

### 使用v1.0.0（学习目的）

```bash
cd versions/1.0.0
python install.py
python launch.py

# ⚠️ 注意：避免使用肽段优化功能（有Bug）
```

### 使用v1.1.0（推荐）

```bash
cd versions/1.1.0

# 安装依赖
pip install pandas numpy openpyxl pyyaml biopython

# 配置环境（可选）
cp .env.example .env
nano .env

# 运行测试
python test_peptide_screening_fixes.py

# 使用肽段优化
python launch.py --optimization
```

---

## 📊 版本详情

### v1.0.0 - 初始版本

**发布日期**: 2025-10-05

**主要功能**:
- ✅ 完整的安装系统
- ✅ STRING相互作用分析
- ✅ 分子对接预测
- ✅ 保守性分析
- ⚠️ 肽段优化（有严重Bug）

**已知问题**:
1. `_load_config()` 无限递归Bug
2. PDB生成逻辑错误
3. 优化Pipeline未实现
4. Neo4j硬依赖
5. 数据库凭据硬编码

**使用建议**:
- ✅ 学习项目结构
- ✅ 使用STRING分析
- ✅ 使用对接功能
- ❌ **不要使用肽段优化**

**详细说明**: 查看 `1.0.0/VERSION.md`

---

### v1.1.0 - Bug修复版本（推荐）

**发布日期**: 2025-10-23

**主要更新**:
- ✅ 修复所有v1.0.0的关键Bug
- ✅ 完整实现3轮肽段优化流程
- ✅ Neo4j优雅降级机制
- ✅ 环境变量配置支持
- ✅ 综合测试套件（100%通过）

**新增文件**:
- `PEPTIDE_SCREENING_FIXES.md` - 详细修复报告
- `.env.example` - 环境变量模板
- `test_peptide_screening_fixes.py` - 测试套件

**性能指标**:
- 执行时间: ~0.25s (10个肽段)
- 内存使用: ~200 MB峰值
- 测试通过率: 100% (7/7)

**使用建议**:
- ✅ **生产环境推荐**
- ✅ 所有功能可用
- ✅ 完整测试覆盖

**详细说明**: 查看 `1.1.0/VERSION.md` 和 `1.1.0/PEPTIDE_SCREENING_FIXES.md`

---

## 🔄 版本迁移

### 从v1.0.0迁移到v1.1.0

**步骤1**: 切换版本目录
```bash
cd versions/1.1.0
```

**步骤2**: 安装新依赖（如需要）
```bash
pip install pandas numpy openpyxl pyyaml
```

**步骤3**: 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，设置数据库连接等
```

**步骤4**: 验证安装
```bash
python test_peptide_screening_fixes.py
```

**注意**: v1.1.0完全向后兼容v1.0.0，无需修改代码。

---

## 📝 版本命名规则

我们遵循 [语义化版本](https://semver.org/) 规范：

```
主版本号.次版本号.修订号

例如: 1.1.0
  │  │  │
  │  │  └─ 修订号：Bug修复
  │  └──── 次版本号：新增功能（向后兼容）
  └─────── 主版本号：重大变更（可能不兼容）
```

### v1.0.0 → v1.1.0
- **次版本号升级**: 新增完整的肽段优化功能
- **向后兼容**: 所有v1.0.0功能正常工作
- **建议升级**: 修复了严重Bug

---

## 🧪 测试说明

### v1.0.0测试
```bash
cd versions/1.0.0
# 仅测试基础功能，避免测试肽段优化
python -c "from bin.input_init import ProteinInputInitializer; print('OK')"
```

### v1.1.0测试
```bash
cd versions/1.1.0
# 运行完整测试套件
python test_peptide_screening_fixes.py

# 预期输出:
# 总计: 7/7 测试通过 (100%)
# 🎉 所有测试通过！peptide screening修复成功。
```

---

## 📦 打包说明

### 打包v1.0.0
```bash
cd versions
tar -czf AI-Drug-Peptide-v1.0.0.tar.gz 1.0.0/
```

### 打包v1.1.0
```bash
cd versions
tar -czf AI-Drug-Peptide-v1.1.0.tar.gz 1.1.0/
```

---

## 🔐 安全说明

### v1.0.0
- ⚠️ 数据库凭据硬编码在源代码中
- ⚠️ 不建议在生产环境使用

### v1.1.0
- ✅ 支持环境变量配置
- ✅ 提供 `.env.example` 模板
- ✅ 无硬编码凭据

---

## 📚 文档索引

### v1.0.0文档
- `1.0.0/VERSION.md` - 版本说明
- `1.0.0/README.md` - 项目README
- `1.0.0/QUICK_START.md` - 快速开始
- `1.0.0/USAGE.md` - 使用指南

### v1.1.0文档
- `1.1.0/VERSION.md` - 版本说明
- `1.1.0/PEPTIDE_SCREENING_FIXES.md` - 详细修复报告 ⭐
- `1.1.0/README.md` - 项目README
- `1.1.0/QUICK_START.md` - 快速开始
- `1.1.0/USAGE.md` - 使用指南
- `1.1.0/.env.example` - 环境配置模板

---

## ❓ FAQ

### Q: 应该使用哪个版本？
**A**: 强烈推荐使用 **v1.1.0**，它修复了所有已知Bug并通过了完整测试。

### Q: v1.0.0还有存在的价值吗？
**A**: 有，作为项目历史记录和学习参考。可以对比两个版本来理解Bug修复过程。

### Q: 如何查看版本差异？
**A**:
```bash
# 查看文件差异
diff -r versions/1.0.0/bin/peptide_optim.py versions/1.1.0/bin/peptide_optim.py

# 或使用git
git diff 1f5ea9e 31060ea -- bin/peptide_optim.py
```

### Q: v1.1.0需要额外的依赖吗？
**A**: 必需依赖相同（pandas, numpy, openpyxl, pyyaml），但Biopython和py2neo变为可选。

### Q: 数据兼容性如何？
**A**: v1.1.0完全兼容v1.0.0的数据格式。

---

## 🛣️ 版本路线图

### 已发布
- ✅ v1.0.0 (2025-10-05) - 初始版本
- ✅ v1.1.0 (2025-10-23) - Bug修复版本

### 计划中
- 📋 v1.2.0 - 真实工具集成
  - ProGen3 API
  - RoPE工具
  - GROMACS
  - AutoDock Vina

- 📋 v1.3.0 - 性能和可视化
  - 数据库持久化
  - 交互式可视化
  - 并行优化
  - GPU加速

---

## 📞 支持

如有问题，请：
1. 查看相应版本的 `VERSION.md`
2. 查看 `PEPTIDE_SCREENING_FIXES.md` (v1.1.0)
3. 提交 [GitHub Issue](https://github.com/xielab2017/AI-Drug-Peptide/issues)

---

## 📄 许可证

所有版本均采用 MIT License - 详见各版本的 LICENSE 文件

---

**推荐**: 使用 **v1.1.0** 获得最佳体验和完整功能！

**更新时间**: 2025-10-23
