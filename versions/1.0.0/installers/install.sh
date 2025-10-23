#!/bin/bash
# AI-Drug Peptide V1.0 - Linux/macOS 一键安装脚本

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# 打印横幅
print_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    AI-Drug Peptide V1.0                     ║"
    echo "║              AI驱动的肽类药物开发平台                          ║"
    echo "║                                                              ║"
    echo "║  🧬 蛋白相互作用分析  🔬 分子对接预测  📊 保守性分析  🎯 肽优化  ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${YELLOW}系统信息:${NC}"
    echo "  • 操作系统: $(uname -s) $(uname -r)"
    echo "  • 架构: $(uname -m)"
    echo "  • 用户: $(whoami)"
    echo "  • 安装路径: $(pwd)"
    echo ""
}

# 检查系统要求
check_requirements() {
    echo -e "${BLUE}🔍 检查系统要求...${NC}"
    
    # 检查Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        echo -e "${GREEN}✅ Python版本: $PYTHON_VERSION${NC}"
        
        # 检查Python版本是否满足要求
        if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
            echo -e "${GREEN}✅ Python版本检查通过${NC}"
        else
            echo -e "${RED}❌ Python版本过低，需要3.8或更高版本${NC}"
            echo -e "${CYAN}请访问 https://www.python.org/downloads/ 下载最新版本${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ 未找到Python3${NC}"
        echo -e "${CYAN}请先安装Python3: https://www.python.org/downloads/${NC}"
        exit 1
    fi
    
    # 检查pip
    if command -v pip3 &> /dev/null; then
        echo -e "${GREEN}✅ pip3已安装${NC}"
    else
        echo -e "${YELLOW}⚠️  未找到pip3，尝试安装...${NC}"
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y python3-pip
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-pip
        elif command -v brew &> /dev/null; then
            brew install python3-pip
        else
            echo -e "${RED}❌ 无法自动安装pip3，请手动安装${NC}"
            exit 1
        fi
    fi
    
    # 检查网络连接
    if ping -c 1 pypi.org &> /dev/null; then
        echo -e "${GREEN}✅ 网络连接正常${NC}"
    else
        echo -e "${YELLOW}⚠️  网络连接可能有问题，安装过程可能较慢${NC}"
    fi
    
    # 检查磁盘空间
    AVAILABLE_SPACE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$AVAILABLE_SPACE" -lt 2 ]; then
        echo -e "${YELLOW}⚠️  磁盘空间可能不足 (${AVAILABLE_SPACE}GB可用)${NC}"
        echo -e "${CYAN}推荐至少2GB可用空间${NC}"
    else
        echo -e "${GREEN}✅ 磁盘空间检查通过 (${AVAILABLE_SPACE}GB可用)${NC}"
    fi
}

# 安装系统依赖
install_system_deps() {
    echo -e "${BLUE}🔧 安装系统依赖...${NC}"
    
    # 检测操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            echo -e "${CYAN}🐧 检测到Ubuntu/Debian系统${NC}"
            sudo apt-get update
            sudo apt-get install -y python3-dev python3-pip build-essential curl wget git
        elif command -v yum &> /dev/null; then
            echo -e "${CYAN}🐧 检测到CentOS/RHEL系统${NC}"
            sudo yum install -y python3-devel python3-pip gcc curl wget git
        elif command -v dnf &> /dev/null; then
            echo -e "${CYAN}🐧 检测到Fedora系统${NC}"
            sudo dnf install -y python3-devel python3-pip gcc curl wget git
        elif command -v pacman &> /dev/null; then
            echo -e "${CYAN}🐧 检测到Arch Linux系统${NC}"
            sudo pacman -S --noconfirm python python-pip base-devel curl wget git
        else
            echo -e "${YELLOW}⚠️  未识别的Linux发行版，跳过系统依赖安装${NC}"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        echo -e "${CYAN}🍎 检测到macOS系统${NC}"
        if command -v brew &> /dev/null; then
            echo -e "${GREEN}✅ 检测到Homebrew${NC}"
            brew install python@3.10 curl wget git
        else
            echo -e "${YELLOW}⚠️  未检测到Homebrew${NC}"
            echo -e "${CYAN}建议安装Homebrew: https://brew.sh/${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  未识别的操作系统${NC}"
    fi
}

# 创建虚拟环境
create_venv() {
    echo -e "${BLUE}🔧 创建虚拟环境...${NC}"
    
    if [ -d "venv" ]; then
        echo -e "${YELLOW}⚠️  虚拟环境已存在${NC}"
        read -p "是否重新创建？(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
        else
            echo -e "${GREEN}✅ 使用现有虚拟环境${NC}"
            return
        fi
    fi
    
    python3 -m venv venv
    echo -e "${GREEN}✅ 虚拟环境创建成功${NC}"
}

# 激活虚拟环境并安装依赖
install_python_deps() {
    echo -e "${BLUE}📦 安装Python依赖包...${NC}"
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级pip
    echo -e "${CYAN}升级pip...${NC}"
    pip install --upgrade pip
    
    # 安装基础依赖
    echo -e "${CYAN}安装基础依赖...${NC}"
    pip install numpy>=1.21.0 pandas>=1.3.0 requests>=2.25.0 pyyaml>=6.0
    
    # 安装完整依赖
    if [ -f "requirements.txt" ]; then
        echo -e "${CYAN}安装完整依赖列表...${NC}"
        pip install -r requirements.txt
    else
        echo -e "${YELLOW}⚠️  未找到requirements.txt文件${NC}"
    fi
    
    echo -e "${GREEN}✅ Python依赖安装成功${NC}"
}

# 创建项目结构
create_project_structure() {
    echo -e "${BLUE}📁 创建项目结构...${NC}"
    
    # 创建目录
    mkdir -p data/{cache,input,output}
    mkdir -p logs reports cache/{docking_logs,receptors}
    mkdir -p config
    
    # 创建配置文件
    cat > config/config.json << 'EOF'
{
  "version": "1.0.0",
  "system": {
    "platform": "linux",
    "python_version": "3.8+",
    "architecture": "x86_64"
  },
  "database": {
    "postgres": {
      "host": "localhost",
      "port": 5432,
      "database": "peptide_research",
      "user": "postgres",
      "password": "password"
    },
    "neo4j": {
      "uri": "bolt://localhost:7687",
      "user": "neo4j",
      "password": "password"
    }
  },
  "analysis": {
    "max_workers": 4,
    "memory_limit": "8GB",
    "timeout": 3600
  },
  "paths": {
    "data_dir": "./data",
    "cache_dir": "./cache",
    "logs_dir": "./logs",
    "reports_dir": "./reports"
  }
}
EOF
    
    echo -e "${GREEN}✅ 项目结构创建成功${NC}"
}

# 验证安装
verify_installation() {
    echo -e "${BLUE}🔍 验证安装...${NC}"
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 测试Python导入
    echo -e "${CYAN}测试Python模块导入...${NC}"
    
    python3 -c "
import sys
modules = ['numpy', 'pandas', 'requests', 'yaml']
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}: 导入成功')
    except ImportError as e:
        print(f'❌ {module}: 导入失败 - {e}')
        sys.exit(1)
"
    
    echo -e "${GREEN}✅ 安装验证完成${NC}"
}

# 打印成功消息
print_success() {
    echo -e "${GREEN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🎉 安装成功！ 🎉                          ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${CYAN}🚀 快速开始:${NC}"
    echo ""
    echo "1. 激活虚拟环境:"
    echo -e "   ${WHITE}source venv/bin/activate${NC}"
    echo ""
    echo "2. 启动应用:"
    echo -e "   ${WHITE}python launch.py${NC}"
    echo ""
    echo "3. 启动网页端:"
    echo -e "   ${WHITE}python dashboard.py${NC}"
    echo ""
    echo -e "${CYAN}📚 更多信息:${NC}"
    echo "   • 查看README.md了解详细使用方法"
    echo "   • 访问 http://localhost:8080 查看Prefect仪表板"
    echo "   • 查看logs/目录了解运行日志"
    echo ""
    echo -e "${YELLOW}💡 提示:${NC}"
    echo "   • 首次运行可能需要下载数据，请保持网络连接"
    echo "   • 如遇问题，请查看logs/目录下的日志文件"
    echo "   • 支持macOS、Windows、Linux多平台"
    echo ""
    echo -e "${GREEN}感谢使用AI-Drug Peptide V1.0！${NC}"
}

# 主函数
main() {
    print_banner
    check_requirements
    install_system_deps
    create_venv
    install_python_deps
    create_project_structure
    verify_installation
    print_success
}

# 错误处理
trap 'echo -e "\n${RED}❌ 安装过程中发生错误${NC}"; exit 1' ERR

# 运行主函数
main "$@"
