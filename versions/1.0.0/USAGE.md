# AI-Drug Peptide 使用说明

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd AI-Drug-Peptide

# 安装依赖
pip install -r requirements.txt

# 创建默认配置
python src/main.py --create-config
```

### 2. 运行第一个分析

```bash
# 使用默认配置运行完整分析
python src/main.py --protein-id THBS4
```

### 3. 查看结果

分析完成后，结果将保存在以下位置：
- **报告文件**: `./data/output/analysis_report_THBS4_*.{json,excel,pdf,html}`
- **数据文件**: `./data/cache/` 目录下的各种CSV文件
- **日志文件**: `./logs/app.log`

## 🔧 详细配置

### 配置文件说明

主配置文件 `config.json` 包含以下主要部分：

```json
{
  "paths": {
    "cache_dir": "./data/cache",      # 缓存目录
    "output_dir": "./data/output",    # 输出目录
    "temp_dir": "./data/temp"         # 临时文件目录
  },
  "database": {
    "postgresql": {                   # PostgreSQL数据库配置
      "host": "localhost",
      "port": 5432,
      "database": "peptide_research",
      "user": "postgres",
      "password": "password"
    },
    "neo4j": {                        # Neo4j图数据库配置
      "uri": "bolt://localhost:7687",
      "user": "neo4j",
      "password": "password"
    }
  },
  "analysis": {
    "string": {                       # STRING分析参数
      "confidence_threshold": 0.9,
      "max_interactions": 100
    },
    "docking": {                      # 分子对接参数
      "energy_threshold": -7.0,
      "exhaustiveness": 8
    },
    "conservation": {                  # 保守性分析参数
      "conservation_threshold": 0.8,
      "min_species": 3
    }
  }
}
```

### 环境变量支持

可以使用环境变量来覆盖配置文件中的设置：

```bash
# 数据库配置
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=peptide_research
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=your_password

# Neo4j配置
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=your_password

# 运行分析
python src/main.py --protein-id THBS4
```

## 📊 分析步骤详解

### 1. STRING相互作用分析

**功能**: 分析蛋白质相互作用网络，识别潜在受体

**参数**:
- `confidence_threshold`: 置信度阈值 (0.0-1.0)
- `max_interactions`: 最大相互作用数量
- `species_id`: 物种ID (默认: 9606 人类)

**输出**:
- 相互作用网络图
- 置信度分布图
- 受体列表 (`string_receptors.csv`)

### 2. 分子对接预测

**功能**: 使用AutoDock Vina进行分子对接分析

**参数**:
- `energy_threshold`: 结合能阈值 (kcal/mol)
- `exhaustiveness`: 搜索强度 (1-32)
- `max_runs`: 最大运行次数

**输出**:
- 结合能分布图
- 受体排名
- 对接结果 (`docking_results.csv`)

### 3. 保守性分析

**功能**: 评估跨物种保守性

**参数**:
- `conservation_threshold`: 保守性阈值 (0.0-1.0)
- `min_species`: 最小物种数量
- `alignment_method`: 比对方法 (clustalw/biopython)

**输出**:
- 保守性热图
- 物种比较图
- 保守性结果 (`conservation_results.csv`)

### 4. 分泌分析

**功能**: 预测蛋白质分泌路径

**参数**:
- `signalp_threshold`: 信号肽阈值
- `tmhmm_threshold`: 跨膜区域阈值
- `hpa_enabled`: 是否启用HPA数据

**输出**:
- 分泌路径图
- 组织表达热图
- 信号肽预测结果

### 5. 肽优化

**功能**: 三轮优化流程

**参数**:
- `target_count`: 目标肽段数量
- `max_length`: 最大长度
- `tm_threshold`: Tm阈值
- `cross_species_ratio`: 跨物种比例

**输出**:
- 优化肽库
- 稳定性分析
- 活性验证结果

## 🛠️ 命令行选项

### 基本用法

```bash
python src/main.py [选项] --protein-id <蛋白质ID>
```

### 主要选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--config` | 配置文件路径 | `config.json` |
| `--protein-id` | 蛋白质ID | 必需 |
| `--steps` | 分析步骤 | `string,docking,conservation` |
| `--start-step` | 开始步骤 | 无 |
| `--log-level` | 日志级别 | `INFO` |
| `--log-file` | 日志文件 | 无 |

### 示例命令

```bash
# 使用默认配置运行完整分析
python src/main.py --protein-id THBS4

# 使用自定义配置文件
python src/main.py --config config.json --protein-id THBS4

# 从特定步骤开始运行
python src/main.py --protein-id THBS4 --start-step step3_docking

# 只运行特定分析步骤
python src/main.py --protein-id THBS4 --steps string docking

# 设置日志级别
python src/main.py --protein-id THBS4 --log-level DEBUG

# 保存日志到文件
python src/main.py --protein-id THBS4 --log-file analysis.log
```

## 🔍 结果解读

### 1. JSON报告

包含完整的分析结果，适合程序处理：

```json
{
  "protein_id": "THBS4",
  "analysis_results": {
    "string_analysis": {
      "total_interactions": 5,
      "confidence_scores": [0.95, 0.88, 0.82],
      "interacting_proteins": [...]
    },
    "docking_analysis": [...],
    "conservation_analysis": {...}
  },
  "metadata": {...}
}
```

### 2. Excel报告

多工作表详细报告：

- **Summary**: 分析概览
- **Detailed Results**: 详细结果
- **Charts**: 图表说明

### 3. PDF报告

静态报告，包含：
- 分析步骤完成情况
- STRING相互作用置信度分布
- 分子对接结合能分布
- 保守性分析结果

### 4. HTML报告

交互式报告，包含：
- 动态图表
- 网络图
- 交互式数据表格

## 🚨 故障排除

### 常见问题

1. **工具不可用**
   ```bash
   # 检查工具是否安装
   which blastp
   which vina
   
   # 检查PATH环境变量
   echo $PATH
   ```

2. **数据库连接失败**
   ```bash
   # 检查PostgreSQL服务
   systemctl status postgresql
   
   # 检查Neo4j服务
   systemctl status neo4j
   ```

3. **内存不足**
   ```bash
   # 调整批处理大小
   # 在config.json中修改
   "performance": {
     "memory_limit": "8GB",
     "batch_size": 50
   }
   ```

4. **网络超时**
   ```bash
   # 增加超时时间
   # 在config.json中修改
   "network": {
     "timeout": 60,
     "max_retries": 5
   }
   ```

### 日志分析

```bash
# 查看应用日志
tail -f logs/app.log

# 查看特定模块日志
grep "STRING" logs/app.log
grep "Docking" logs/app.log
grep "Conservation" logs/app.log

# 查看错误日志
grep "ERROR" logs/app.log
grep "CRITICAL" logs/app.log
```

### 性能优化

1. **并行处理**
   ```json
   "workflow": {
     "max_parallel_tasks": 8
   }
   ```

2. **缓存优化**
   ```json
   "cache": {
     "enabled": true,
     "expiration_hours": 48
   }
   ```

3. **批处理大小**
   ```json
   "performance": {
     "batch_size": 100
   }
   ```

## 📚 进阶使用

### 自定义分析模块

```python
from src.core.analysis.engine import AnalysisEngine

class CustomAnalyzer:
    def run(self, **kwargs):
        # 自定义分析逻辑
        return {"result": "custom_analysis"}

# 注册自定义模块
analysis_engine.register_module("custom_analysis", CustomAnalyzer())
```

### 工作流自定义

```python
from src.core.workflow.orchestrator import WorkflowOrchestrator

# 创建自定义工作流
orchestrator = WorkflowOrchestrator(config, analysis_engine)

# 添加自定义步骤
orchestrator.add_step("custom_step", "custom_analysis", dependencies=["step1"])

# 运行工作流
orchestrator.run_workflow()
```

### 报告自定义

```python
from src.core.reporting.generator import ReportGenerator

# 创建自定义报告生成器
generator = ReportGenerator(config)

# 生成自定义报告
report_files = await generator.generate_report(request, results)
```

## 🎯 最佳实践

### 1. 配置管理
- 使用环境变量管理敏感信息
- 为不同环境创建不同的配置文件
- 定期备份配置文件

### 2. 数据管理
- 定期清理缓存文件
- 备份重要的分析结果
- 使用版本控制管理数据

### 3. 性能优化
- 根据硬件资源调整并行任务数
- 使用SSD存储提高I/O性能
- 定期监控内存和CPU使用情况

### 4. 错误处理
- 启用详细日志记录
- 设置合理的超时时间
- 实现自动重试机制

## 📞 获取帮助

- **文档**: 查看 `ARCHITECTURE.md` 了解详细架构
- **问题报告**: 在GitHub Issues中报告问题
- **社区支持**: 加入我们的讨论群组

---

**注意**: 这是一个研究项目，仅供学术研究使用。在生产环境中使用前，请确保所有依赖工具已正确安装和配置。
