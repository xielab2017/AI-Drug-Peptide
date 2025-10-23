# 版本结构说明

## 📂 目录结构

```
AI-Drug-Peptide/
│
├── versions/                    # 版本管理目录
│   ├── README.md                # 版本对比和使用指南
│   │
│   ├── 1.0.0/                   # v1.0.0 初始版本
│   │   ├── VERSION.md           # 版本说明（已知问题列表）
│   │   ├── bin/                 # 原始代码（有Bug）
│   │   │   ├── peptide_optim.py # ❌ 包含无限递归Bug
│   │   │   └── workflow.py      # ❌ 硬编码数据库凭据
│   │   ├── config/              # 配置文件
│   │   ├── src/                 # 源代码
│   │   └── ...                  # 其他文件（73个文件总计）
│   │
│   └── 1.1.0/                   # v1.1.0 修复版本（推荐）
│       ├── VERSION.md           # 版本说明（改进列表）
│       ├── PEPTIDE_SCREENING_FIXES.md  # 详细修复报告
│       ├── .env.example         # 环境变量模板
│       ├── bin/                 # 修复后的代码
│       │   ├── peptide_optim.py # ✅ 已修复所有Bug
│       │   └── workflow.py      # ✅ 支持环境变量
│       ├── config/              # 配置文件
│       ├── src/                 # 源代码
│       ├── output/              # 示例输出
│       │   └── optimized_peptide_library_*.xlsx
│       ├── test_peptide_screening_fixes.py  # 测试套件
│       └── ...                  # 其他文件（77个文件总计）
│
├── bin/                         # 当前工作目录（v1.1.0）
├── config/                      # 当前配置
├── README.md                    # 主README（已更新版本信息）
├── PEPTIDE_SCREENING_FIXES.md   # 修复报告
├── .env.example                 # 环境变量模板
└── test_peptide_screening_fixes.py  # 测试套件
```

---

## 🔄 版本关系

```
┌─────────────────────────────────────────────────────────┐
│                   Git 历史                               │
└─────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         │                                   │
         v                                   v
   ┌─────────────┐                    ┌─────────────┐
   │   1f5ea9e   │                    │   31060ea   │
   │  v1.0.0     │                    │  v1.1.0     │
   │  初始版本    │  ────修复Bug────>  │  修复版本    │
   │  已知问题    │                    │  推荐使用    │
   └─────────────┘                    └─────────────┘
         │                                   │
         v                                   v
   versions/1.0.0/                    versions/1.1.0/
   - 73 files                         - 77 files
   - ❌ 10个已知Bug                   - ✅ 全部修复
   - ⚠️ 仅供参考                      - ⭐ 生产就绪
```

---

## 📊 版本对比

### 功能对比

| 功能模块 | v1.0.0 | v1.1.0 | 说明 |
|---------|--------|--------|------|
| **基础功能** | | | |
| STRING分析 | ✅ | ✅ | 无变化 |
| 分子对接 | ✅ | ✅ | 无变化 |
| 保守性分析 | ✅ | ✅ | 无变化 |
| 结果合并 | ✅ | ✅ | 无变化 |
| **肽段优化** | | | |
| Round 1 生成 | ❌ | ✅ | 完整实现 |
| Round 2 稳定性 | ❌ | ✅ | 完整实现 |
| Round 3 验证 | ❌ | ✅ | 完整实现 |
| Excel报告 | ❌ | ✅ | 新增功能 |
| **配置管理** | | | |
| YAML配置 | ✅ | ✅ | 无变化 |
| 环境变量 | ❌ | ✅ | 新增支持 |
| .env模板 | ❌ | ✅ | 新增文件 |
| **依赖管理** | | | |
| Neo4j | 必需 | 可选 | 优雅降级 |
| Biopython | 必需 | 可选 | Fallback |
| **测试** | | | |
| 测试套件 | ❌ | ✅ | 7个测试 |
| 测试通过率 | - | 100% | 全部通过 |

### Bug修复对比

| Bug编号 | 问题描述 | v1.0.0 | v1.1.0 |
|---------|---------|--------|--------|
| #1 | 无限递归Bug | ❌ 存在 | ✅ 已修复 |
| #2 | PDB生成逻辑错误 | ❌ 存在 | ✅ 已修复 |
| #3 | Pipeline未实现 | ❌ 存在 | ✅ 已实现 |
| #4 | Neo4j硬依赖 | ❌ 存在 | ✅ 已修复 |
| #5 | 硬编码凭据 | ❌ 存在 | ✅ 已修复 |
| #6 | Placeholder返回错误 | ❌ 存在 | ✅ 已修复 |
| #7 | 约束检查过严 | ❌ 存在 | ✅ 已优化 |
| #8 | 肽段太长 | ❌ 存在 | ✅ 已优化 |
| #9 | 日志目录问题 | ❌ 存在 | ✅ 已修复 |
| #10 | Excel报告Bug | ❌ 存在 | ✅ 已修复 |

---

## 🎯 使用建议

### 场景1：学习和研究

**推荐**: v1.0.0

```bash
cd versions/1.0.0
# 学习项目结构
# 理解Bug产生原因
# 对比修复前后
```

### 场景2：生产环境

**推荐**: v1.1.0

```bash
cd versions/1.1.0
# 安装依赖
pip install -r requirements.txt
# 配置环境
cp .env.example .env
# 运行测试
python test_peptide_screening_fixes.py
```

### 场景3：开发和贡献

**推荐**: 主目录（= v1.1.0）

```bash
# 直接在主目录工作
cd AI-Drug-Peptide
# 开发新功能
# 提交PR
```

---

## 📁 文件差异

### v1.0.0 特有文件（0个）
- 无特有文件

### v1.1.0 新增文件（4个）
1. `.env.example` - 环境变量配置模板
2. `PEPTIDE_SCREENING_FIXES.md` - 详细修复报告
3. `test_peptide_screening_fixes.py` - 综合测试套件
4. `output/optimized_peptide_library_*.xlsx` - 示例输出

### 共同文件修改（主要）
1. `bin/peptide_optim.py` - 修复10个Bug
2. `bin/workflow.py` - 环境变量支持
3. `README.md` - 版本信息更新

---

## 🚀 快速切换

### 切换到v1.0.0
```bash
cd /home/user/AI-Drug-Peptide/versions/1.0.0
python install.py
python launch.py
```

### 切换到v1.1.0
```bash
cd /home/user/AI-Drug-Peptide/versions/1.1.0
pip install pandas numpy openpyxl pyyaml
python test_peptide_screening_fixes.py
python launch.py --optimization
```

### 使用主目录（推荐）
```bash
cd /home/user/AI-Drug-Peptide
# 主目录始终是最新版本（当前为v1.1.0）
```

---

## 📚 文档索引

### v1.0.0 文档
- `versions/1.0.0/VERSION.md` - 版本说明和已知问题
- `versions/1.0.0/README.md` - 项目README
- `versions/1.0.0/QUICK_START.md` - 快速开始指南
- `versions/1.0.0/USAGE.md` - 使用说明

### v1.1.0 文档
- `versions/1.1.0/VERSION.md` - 版本说明和改进列表
- `versions/1.1.0/PEPTIDE_SCREENING_FIXES.md` - **详细修复报告** ⭐
- `versions/1.1.0/README.md` - 项目README
- `versions/1.1.0/QUICK_START.md` - 快速开始指南
- `versions/1.1.0/.env.example` - 环境配置模板

### 版本管理文档
- `versions/README.md` - **版本对比总览** ⭐
- `VERSION_STRUCTURE.md` - 本文件（结构说明）

---

## 🔍 Git操作

### 查看版本差异
```bash
# 对比两个版本
git diff 1f5ea9e 31060ea

# 对比特定文件
git diff 1f5ea9e 31060ea -- bin/peptide_optim.py

# 查看修复提交
git show 31060ea
```

### 提取特定版本
```bash
# 提取v1.0.0
git archive 1f5ea9e | tar -x -C /tmp/v1.0.0

# 提取v1.1.0
git archive 31060ea | tar -x -C /tmp/v1.1.0
```

---

## 💡 最佳实践

### 1. 使用正确的版本
- 生产环境 → **v1.1.0**
- 学习研究 → v1.0.0
- 新功能开发 → 主目录

### 2. 测试验证
```bash
# v1.1.0 必须运行测试
cd versions/1.1.0
python test_peptide_screening_fixes.py

# 预期: 7/7 测试通过 (100%)
```

### 3. 配置管理
```bash
# 使用环境变量（v1.1.0）
cp .env.example .env
nano .env  # 编辑配置

# 避免硬编码（v1.0.0的问题）
```

---

## ⚠️ 注意事项

### v1.0.0 限制
- ❌ 不要使用肽段优化功能
- ❌ 不要在生产环境部署
- ✅ 可用于STRING分析等基础功能
- ✅ 适合学习项目结构

### v1.1.0 优势
- ✅ 所有功能可用
- ✅ 生产环境就绪
- ✅ 完整测试覆盖
- ✅ 详细文档支持

---

## 📞 获取帮助

### 查看文档
1. `versions/README.md` - 版本总览
2. `versions/1.1.0/PEPTIDE_SCREENING_FIXES.md` - 修复详情
3. `versions/1.1.0/VERSION.md` - 版本说明

### 提交问题
- GitHub Issues: https://github.com/xielab2017/AI-Drug-Peptide/issues
- 标明使用的版本号

---

**创建日期**: 2025-10-23
**当前推荐版本**: v1.1.0
**主目录对应版本**: v1.1.0
