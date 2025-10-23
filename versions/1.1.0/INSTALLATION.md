# AI-Drug Peptide V1.0 - Installation Guide

This guide provides detailed installation instructions for AI-Drug Peptide on different operating systems.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher (recommended 3.9+)
- **RAM**: 4GB minimum (8GB+ recommended)
- **Storage**: 2GB available space
- **Network**: Internet connection for dependency download

### Supported Operating Systems
- **macOS**: 10.14 (Mojave) or later
- **Windows**: Windows 10 or later
- **Linux**: Ubuntu 18.04+, CentOS 7+, Fedora 30+

## 🚀 Quick Installation

### One-Line Installation (Recommended)

#### macOS/Linux
```bash
curl -fsSL https://raw.githubusercontent.com/your-username/AI-Drug-Peptide/main/install.sh | bash
```

#### Windows (PowerShell)
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/your-username/AI-Drug-Peptide/main/install.ps1" -OutFile "install.ps1"
.\install.ps1
```

## 🔧 Manual Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/AI-Drug-Peptide.git
cd AI-Drug-Peptide
```

### Step 2: Run Installation Script
```bash
python install.py
```

### Step 3: Verify Installation
```bash
python launch.py --help
```

## 🖥️ Platform-Specific Instructions

### macOS Installation

#### Prerequisites
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install system dependencies
brew install python@3.10 curl wget git
```

#### Installation Steps
```bash
# Clone repository
git clone https://github.com/your-username/AI-Drug-Peptide.git
cd AI-Drug-Peptide

# Run installation
python install.py

# Activate virtual environment
source venv/bin/activate

# Start application
python launch.py
```

### Windows Installation

#### Prerequisites
1. **Install Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Ensure "Add Python to PATH" is checked during installation

2. **Install Git**
   - Download from [git-scm.com](https://git-scm.com/download/win)

3. **Install Chocolatey (Optional)**
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

#### Installation Steps
```powershell
# Clone repository
git clone https://github.com/your-username/AI-Drug-Peptide.git
cd AI-Drug-Peptide

# Run installation
python install.py

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start application
python launch.py
```

### Linux Installation

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install system dependencies
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential curl wget git

# Clone repository
git clone https://github.com/your-username/AI-Drug-Peptide.git
cd AI-Drug-Peptide

# Run installation
python3 install.py

# Activate virtual environment
source venv/bin/activate

# Start application
python launch.py
```

#### CentOS/RHEL
```bash
# Install system dependencies
sudo yum install -y python3 python3-pip python3-devel gcc curl wget git

# Clone repository
git clone https://github.com/your-username/AI-Drug-Peptide.git
cd AI-Drug-Peptide

# Run installation
python3 install.py

# Activate virtual environment
source venv/bin/activate

# Start application
python launch.py
```

#### Fedora
```bash
# Install system dependencies
sudo dnf install -y python3 python3-pip python3-devel gcc curl wget git

# Clone repository
git clone https://github.com/your-username/AI-Drug-Peptide.git
cd AI-Drug-Peptide

# Run installation
python3 install.py

# Activate virtual environment
source venv/bin/activate

# Start application
python launch.py
```

#### Arch Linux
```bash
# Install system dependencies
sudo pacman -S --noconfirm python python-pip base-devel curl wget git

# Clone repository
git clone https://github.com/your-username/AI-Drug-Peptide.git
cd AI-Drug-Peptide

# Run installation
python install.py

# Activate virtual environment
source venv/bin/activate

# Start application
python launch.py
```

## 🐳 Docker Installation

### Prerequisites
- Docker installed and running
- Docker Compose (optional)

### Installation Steps
```bash
# Clone repository
git clone https://github.com/your-username/AI-Drug-Peptide.git
cd AI-Drug-Peptide

# Build Docker image
docker build -t ai-drug-peptide .

# Run container
docker run -it --rm -p 8080:8080 ai-drug-peptide
```

### Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🔍 Verification

### Check Installation
```bash
# Check Python version
python --version

# Check virtual environment
which python

# Test imports
python -c "import numpy, pandas, requests, yaml; print('All modules imported successfully')"

# Run help command
python launch.py --help
```

### Test Basic Functionality
```bash
# Start interactive mode
python launch.py

# Check environment
python launch.py --skip-env-check

# Start dashboard
python dashboard.py
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Python Version Issues
```bash
# Check Python version
python --version

# If version is too old, install newer version
# macOS
brew install python@3.10

# Ubuntu/Debian
sudo apt install python3.10

# Windows: Download from python.org
```

#### 2. Permission Issues
```bash
# macOS/Linux: Fix permissions
chmod +x install.sh
chmod +x installers/install.sh

# Windows: Run PowerShell as Administrator
```

#### 3. Network Issues
```bash
# Check internet connection
ping pypi.org

# Use alternative PyPI mirror
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt
```

#### 4. Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### 5. Dependency Conflicts
```bash
# Check for conflicts
pip check

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Getting Help

1. **Check Logs**
   ```bash
   # View installation logs
   cat logs/install.log
   
   # View application logs
   tail -f logs/app.log
   ```

2. **Report Issues**
   - Create GitHub issue with system information
   - Include error messages and logs
   - Provide steps to reproduce

3. **Community Support**
   - GitHub Discussions
   - Stack Overflow (tag: ai-drug-peptide)

## 🔄 Updating

### Update from Git
```bash
# Pull latest changes
git pull origin main

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Restart application
python launch.py
```

### Update from PyPI
```bash
# Upgrade package
pip install --upgrade ai-drug-peptide

# Restart application
python launch.py
```

## 🗑️ Uninstallation

### Remove Installation
```bash
# Remove project directory
rm -rf AI-Drug-Peptide

# Remove virtual environment (if created separately)
rm -rf venv
```

### Clean System Dependencies
```bash
# macOS
brew uninstall python@3.10

# Ubuntu/Debian
sudo apt remove python3 python3-pip

# Windows: Uninstall from Control Panel
```

## 📚 Next Steps

After successful installation:

1. **Read Documentation**
   - [Quick Start Guide](QUICK_START.md)
   - [Configuration Guide](CONFIGURATION.md)
   - [API Documentation](API.md)

2. **Run Examples**
   ```bash
   # Run example analysis
   python launch.py --workflow --protein-id THBS4
   
   # Start web dashboard
   python dashboard.py
   ```

3. **Configure Environment**
   - Set up database connections
   - Configure analysis parameters
   - Customize output formats

---

For additional help, please refer to the [Troubleshooting Guide](TROUBLESHOOTING.md) or create an issue on GitHub.
