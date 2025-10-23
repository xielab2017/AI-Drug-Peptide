# AI-Drug Peptide V1.0

AI-driven peptide drug development platform with multi-step bioinformatics analysis pipeline.

## 🚀 Quick Install

### One-line Installation

```bash
# macOS/Linux
curl -fsSL https://raw.githubusercontent.com/your-username/AI-Drug-Peptide/main/install.sh | bash

# Windows (PowerShell)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/your-username/AI-Drug-Peptide/main/install.ps1" -OutFile "install.ps1"
.\install.ps1
```

### Manual Installation

```bash
# Clone repository
git clone https://github.com/your-username/AI-Drug-Peptide.git
cd AI-Drug-Peptide

# Run installation script
python install.py

# Start application
python launch.py
```

## 📦 System Requirements

- **Python**: 3.8+ (recommended 3.9+)
- **OS**: macOS 10.14+, Windows 10+, Ubuntu 18.04+
- **RAM**: 4GB (recommended 8GB+)
- **Storage**: 2GB available space

## 🔧 Core Features

- ✅ **Cross-platform support**: macOS, Linux, Windows
- ✅ **Automated installation**: Dependencies and environment setup
- ✅ **Interactive interface**: User-friendly menu system
- ✅ **Web dashboard**: Prefect-based workflow management
- ✅ **Multi-step analysis**: STRING interaction → Docking → Conservation → Optimization

## 🛠️ Usage

### Interactive Mode
```bash
python launch.py
```

### Command Line Mode
```bash
# Run complete workflow
python launch.py --workflow --protein-id THBS4

# Run specific steps
python launch.py --steps step1,step2 --protein-id THBS4

# Secretion analysis
python launch.py --secretion --protein-id THBS4
```

### Web Dashboard
```bash
python dashboard.py
```
Visit `http://localhost:8080` for Prefect dashboard

## 📊 Analysis Pipeline

1. **STRING Interaction Analysis** - Protein interaction network from STRING database
2. **Molecular Docking Prediction** - AutoDock Vina molecular docking
3. **Conservation Analysis** - Cross-species sequence alignment and conservation assessment
4. **Result Integration** - Comprehensive scoring and candidate ranking

## 📁 Project Structure

```
AI-Drug-Peptide/
├── 🚀 install.py           # Smart installation script
├── 🎯 launch.py            # Main launcher
├── 📊 dashboard.py         # Prefect web dashboard
├── 📖 README.md            # Project documentation
├── 📄 LICENSE              # MIT License
├── 🔧 setup.py             # Python package setup
├── 📦 requirements.txt     # Python dependencies
│
├── 📁 bin/                 # 🔬 Core analysis scripts
├── 📁 src/                 # 💻 Source code modules
├── 📁 config/              # ⚙️ Configuration files
├── 📁 data/                # 💾 Data directory
├── 📁 logs/                # 📝 Log files
├── 📁 reports/             # 📊 Generated reports
├── 📁 scripts/             # 🔧 Utility scripts
├── 📁 docs/                # 📚 Documentation
└── 📁 installers/           # 📦 Platform installers
```

## 🔍 Output Results

### Report Files
- **JSON**: `./reports/analysis_report_THBS4_*.json`
- **Excel**: `./reports/analysis_report_THBS4_*.xlsx`
- **PDF**: `./reports/analysis_report_THBS4_*.pdf`
- **HTML**: `./reports/analysis_report_THBS4_*.html`

### Key Metrics
- **Binding Energy**: Lower negative values indicate stronger binding
- **Conservation**: 0-1 scale, higher values indicate more conserved regions
- **Confidence**: STRING database confidence scores
- **Composite Score**: Integrated scoring across all metrics

## ⚙️ Configuration

### Environment Variables
```bash
# Database configuration
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=peptide_research
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=password

# Neo4j configuration
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=password
```

## 🚀 Advanced Features

### 1. Secretion Analysis
- Protein secretion signal prediction
- Transmembrane structure analysis
- Tissue specificity assessment

### 2. Peptide Optimization
- AI-based peptide design
- Stability prediction
- Toxicity assessment

### 3. Report Generation
- Multi-format output (JSON, Excel, PDF, HTML)
- Interactive charts
- Automated report templates

## 🔧 Troubleshooting

### Common Issues

1. **Installation Failed**
   ```bash
   # Check Python version
   python --version
   
   # Check network connection
   ping pypi.org
   
   # Reinstall
   python install.py --force
   ```

2. **Missing Dependencies**
   ```bash
   # Check dependencies
   python install.py --check-deps
   
   # Manual installation
   pip install -r requirements.txt
   ```

3. **Database Connection Issues**
   ```bash
   # Check Docker status
   docker ps
   
   # Restart Neo4j
   docker restart neo4j
   ```

### Log Files
```bash
# View application logs
tail -f logs/app.log

# View error logs
grep ERROR logs/app.log
```

## 📚 Documentation

- [Quick Start Guide](docs/QUICK_START.md)
- [Configuration](docs/CONFIGURATION.md)
- [API Documentation](docs/API.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### Development Setup
```bash
# Clone repository
git clone https://github.com/your-username/AI-Drug-Peptide.git
cd AI-Drug-Peptide

# Install development dependencies
python install.py --dev

# Run tests
python -m pytest tests/
```

### Code Standards
- Use Black for code formatting
- Use flake8 for code linting
- Follow PEP 8 coding standards

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 📞 Support

- **Bug Reports**: [GitHub Issues](https://github.com/your-username/AI-Drug-Peptide/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/your-username/AI-Drug-Peptide/discussions)
- **Documentation**: [GitHub Wiki](https://github.com/your-username/AI-Drug-Peptide/wiki)

## 🙏 Acknowledgments

Thanks to all contributors and the open-source community!

---

**Note**: This is a research project for academic use only. Ensure all dependency tools are properly installed and configured before production use.
