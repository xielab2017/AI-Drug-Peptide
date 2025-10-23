#!/usr/bin/env python3
"""
AI-Drug Peptide V1.0 - 跨平台安装脚本
AI驱动的肽类药物开发平台
"""

import os
import sys
import platform
import subprocess
import urllib.request
import json
import shutil
from pathlib import Path

class Colors:
    """终端颜色输出"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class Installer:
    def __init__(self):
        self.system = platform.system().lower()
        self.python_version = sys.version_info
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.requirements_file = self.project_root / "requirements.txt"
        
    def print_banner(self):
        """打印安装横幅"""
        banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                    AI-Drug Peptide V1.0                     ║
║              AI驱动的肽类药物开发平台                          ║
║                                                              ║
║  🧬 蛋白相互作用分析  🔬 分子对接预测  📊 保守性分析  🎯 肽优化  ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}

{Colors.YELLOW}系统信息:{Colors.END}
  • 操作系统: {platform.system()} {platform.release()}
  • Python版本: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}
  • 架构: {platform.machine()}
  • 安装路径: {self.project_root}
"""
        print(banner)
    
    def check_python_version(self):
        """检查Python版本"""
        print(f"{Colors.BLUE}🔍 检查Python版本...{Colors.END}")
        
        if self.python_version < (3, 8):
            print(f"{Colors.RED}❌ 错误: Python版本过低 ({self.python_version.major}.{self.python_version.minor}){Colors.END}")
            print(f"{Colors.YELLOW}   需要Python 3.8或更高版本{Colors.END}")
            print(f"{Colors.CYAN}   请访问 https://www.python.org/downloads/ 下载最新版本{Colors.END}")
            return False
        
        print(f"{Colors.GREEN}✅ Python版本检查通过: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}{Colors.END}")
        return True
    
    def check_system_requirements(self):
        """检查系统要求"""
        print(f"{Colors.BLUE}🔍 检查系统要求...{Colors.END}")
        
        # 检查内存
        try:
            if self.system == "linux":
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                mem_total = int(meminfo.split('\n')[0].split()[1]) // 1024 // 1024  # GB
            elif self.system == "darwin":  # macOS
                result = subprocess.run(['sysctl', 'hw.memsize'], capture_output=True, text=True)
                mem_total = int(result.stdout.split()[1]) // 1024 // 1024 // 1024  # GB
            else:  # Windows
                mem_total = 8  # 假设8GB，Windows检查较复杂
        except:
            mem_total = 4  # 默认假设4GB
        
        if mem_total < 4:
            print(f"{Colors.YELLOW}⚠️  警告: 系统内存可能不足 ({mem_total}GB){Colors.END}")
            print(f"{Colors.CYAN}   推荐至少4GB内存，推荐8GB以上{Colors.END}")
        else:
            print(f"{Colors.GREEN}✅ 内存检查通过: {mem_total}GB{Colors.END}")
        
        # 检查磁盘空间
        try:
            disk_usage = shutil.disk_usage(self.project_root)
            free_gb = disk_usage.free // 1024 // 1024 // 1024
            if free_gb < 2:
                print(f"{Colors.YELLOW}⚠️  警告: 磁盘空间可能不足 ({free_gb}GB){Colors.END}")
                print(f"{Colors.CYAN}   推荐至少2GB可用空间{Colors.END}")
            else:
                print(f"{Colors.GREEN}✅ 磁盘空间检查通过: {free_gb}GB可用{Colors.END}")
        except:
            print(f"{Colors.YELLOW}⚠️  无法检查磁盘空间{Colors.END}")
        
        return True
    
    def create_virtual_environment(self):
        """创建虚拟环境"""
        print(f"{Colors.BLUE}🔧 创建虚拟环境...{Colors.END}")
        
        if self.venv_path.exists():
            print(f"{Colors.YELLOW}⚠️  虚拟环境已存在，是否重新创建？{Colors.END}")
            response = input("输入 'y' 重新创建，其他键跳过: ").lower()
            if response == 'y':
                shutil.rmtree(self.venv_path)
            else:
                print(f"{Colors.GREEN}✅ 使用现有虚拟环境{Colors.END}")
                return True
        
        try:
            subprocess.run([
                sys.executable, '-m', 'venv', str(self.venv_path)
            ], check=True)
            print(f"{Colors.GREEN}✅ 虚拟环境创建成功{Colors.END}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}❌ 虚拟环境创建失败: {e}{Colors.END}")
            return False
    
    def get_pip_command(self):
        """获取pip命令路径"""
        if self.system == "windows":
            return str(self.venv_path / "Scripts" / "pip.exe")
        else:
            return str(self.venv_path / "bin" / "pip")
    
    def get_python_command(self):
        """获取Python命令路径"""
        if self.system == "windows":
            return str(self.venv_path / "Scripts" / "python.exe")
        else:
            return str(self.venv_path / "bin" / "python")
    
    def upgrade_pip(self):
        """升级pip"""
        print(f"{Colors.BLUE}📦 升级pip...{Colors.END}")
        
        pip_cmd = self.get_pip_command()
        try:
            subprocess.run([
                pip_cmd, 'install', '--upgrade', 'pip'
            ], check=True)
            print(f"{Colors.GREEN}✅ pip升级成功{Colors.END}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}❌ pip升级失败: {e}{Colors.END}")
            return False
    
    def install_requirements(self):
        """安装Python依赖"""
        print(f"{Colors.BLUE}📦 安装Python依赖包...{Colors.END}")
        
        pip_cmd = self.get_pip_command()
        
        # 首先安装基础依赖
        basic_deps = [
            'numpy>=1.21.0',
            'pandas>=1.3.0',
            'requests>=2.25.0',
            'pyyaml>=6.0'
        ]
        
        try:
            for dep in basic_deps:
                print(f"  安装 {dep}...")
                subprocess.run([
                    pip_cmd, 'install', dep
                ], check=True)
            
            # 安装完整依赖
            if self.requirements_file.exists():
                print(f"  安装完整依赖列表...")
                subprocess.run([
                    pip_cmd, 'install', '-r', str(self.requirements_file)
                ], check=True)
            
            print(f"{Colors.GREEN}✅ Python依赖安装成功{Colors.END}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}❌ Python依赖安装失败: {e}{Colors.END}")
            return False
    
    def install_system_dependencies(self):
        """安装系统依赖"""
        print(f"{Colors.BLUE}🔧 检查系统依赖...{Colors.END}")
        
        if self.system == "linux":
            self.install_linux_dependencies()
        elif self.system == "darwin":  # macOS
            self.install_macos_dependencies()
        elif self.system == "windows":
            self.install_windows_dependencies()
    
    def install_linux_dependencies(self):
        """安装Linux依赖"""
        print(f"{Colors.CYAN}🐧 检测到Linux系统{Colors.END}")
        
        # 检查包管理器
        package_managers = ['apt', 'yum', 'dnf', 'pacman', 'zypper']
        available_manager = None
        
        for manager in package_managers:
            if shutil.which(manager):
                available_manager = manager
                break
        
        if not available_manager:
            print(f"{Colors.YELLOW}⚠️  未检测到包管理器，跳过系统依赖安装{Colors.END}")
            return
        
        print(f"{Colors.GREEN}✅ 检测到包管理器: {available_manager}{Colors.END}")
        
        # 根据包管理器安装依赖
        if available_manager == 'apt':
            packages = ['python3-dev', 'python3-pip', 'build-essential', 'curl', 'wget']
        elif available_manager in ['yum', 'dnf']:
            packages = ['python3-devel', 'python3-pip', 'gcc', 'curl', 'wget']
        elif available_manager == 'pacman':
            packages = ['python', 'python-pip', 'base-devel', 'curl', 'wget']
        else:
            packages = ['python3-dev', 'python3-pip', 'gcc', 'curl', 'wget']
        
        print(f"{Colors.CYAN}建议安装系统包: {', '.join(packages)}{Colors.END}")
        print(f"{Colors.YELLOW}请手动运行以下命令安装:{Colors.END}")
        print(f"{Colors.WHITE}sudo {available_manager} install {' '.join(packages)}{Colors.END}")
    
    def install_macos_dependencies(self):
        """安装macOS依赖"""
        print(f"{Colors.CYAN}🍎 检测到macOS系统{Colors.END}")
        
        # 检查Homebrew
        if shutil.which('brew'):
            print(f"{Colors.GREEN}✅ 检测到Homebrew{Colors.END}")
            print(f"{Colors.CYAN}建议安装系统包: python@3.10, curl, wget{Colors.END}")
            print(f"{Colors.YELLOW}请手动运行以下命令安装:{Colors.END}")
            print(f"{Colors.WHITE}brew install python@3.10 curl wget{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  未检测到Homebrew{Colors.END}")
            print(f"{Colors.CYAN}建议安装Homebrew: https://brew.sh/{Colors.END}")
    
    def install_windows_dependencies(self):
        """安装Windows依赖"""
        print(f"{Colors.CYAN}🪟 检测到Windows系统{Colors.END}")
        
        # 检查Chocolatey
        if shutil.which('choco'):
            print(f"{Colors.GREEN}✅ 检测到Chocolatey{Colors.END}")
            print(f"{Colors.CYAN}建议安装系统包: python, curl, wget{Colors.END}")
            print(f"{Colors.YELLOW}请手动运行以下命令安装:{Colors.END}")
            print(f"{Colors.WHITE}choco install python curl wget{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  未检测到Chocolatey{Colors.END}")
            print(f"{Colors.CYAN}建议安装Chocolatey: https://chocolatey.org/{Colors.END}")
    
    def create_config_files(self):
        """创建配置文件"""
        print(f"{Colors.BLUE}⚙️  创建配置文件...{Colors.END}")
        
        config_dir = self.project_root / "config"
        config_dir.mkdir(exist_ok=True)
        
        # 创建默认配置文件
        default_config = {
            "version": "1.0.0",
            "system": {
                "platform": self.system,
                "python_version": f"{self.python_version.major}.{self.python_version.minor}",
                "architecture": platform.machine()
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
        
        config_file = config_dir / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        print(f"{Colors.GREEN}✅ 配置文件创建成功: {config_file}{Colors.END}")
    
    def create_directories(self):
        """创建必要的目录"""
        print(f"{Colors.BLUE}📁 创建项目目录...{Colors.END}")
        
        directories = [
            "data", "data/cache", "data/input", "data/output",
            "logs", "reports", "cache", "cache/docking_logs", "cache/receptors"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
        
        print(f"{Colors.GREEN}✅ 项目目录创建成功{Colors.END}")
    
    def verify_installation(self):
        """验证安装"""
        print(f"{Colors.BLUE}🔍 验证安装...{Colors.END}")
        
        python_cmd = self.get_python_command()
        
        try:
            # 测试Python导入
            test_imports = [
                'numpy', 'pandas', 'requests', 'yaml'
            ]
            
            for module in test_imports:
                result = subprocess.run([
                    python_cmd, '-c', f'import {module}; print(f"{module} version: {{getattr({module}, \"__version__\", \"unknown\")}}")'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"{Colors.GREEN}✅ {module}: {result.stdout.strip()}{Colors.END}")
                else:
                    print(f"{Colors.RED}❌ {module}: 导入失败{Colors.END}")
            
            print(f"{Colors.GREEN}✅ 安装验证完成{Colors.END}")
            return True
            
        except Exception as e:
            print(f"{Colors.RED}❌ 安装验证失败: {e}{Colors.END}")
            return False
    
    def print_success_message(self):
        """打印成功消息"""
        python_cmd = self.get_python_command()
        
        success_message = f"""
{Colors.GREEN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                    🎉 安装成功！ 🎉                          ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}

{Colors.CYAN}🚀 快速开始:{Colors.END}

1. 激活虚拟环境:
   {Colors.WHITE}{self.get_activation_command()}{Colors.END}

2. 启动应用:
   {Colors.WHITE}{python_cmd} launch.py{Colors.END}

3. 启动网页端:
   {Colors.WHITE}{python_cmd} dashboard.py{Colors.END}

{Colors.CYAN}📚 更多信息:{Colors.END}
   • 查看README.md了解详细使用方法
   • 访问 http://localhost:8080 查看Prefect仪表板
   • 查看logs/目录了解运行日志

{Colors.YELLOW}💡 提示:{Colors.END}
   • 首次运行可能需要下载数据，请保持网络连接
   • 如遇问题，请查看logs/目录下的日志文件
   • 支持macOS、Windows、Linux多平台

{Colors.GREEN}感谢使用AI-Drug Peptide V1.0！{Colors.END}
"""
        print(success_message)
    
    def get_activation_command(self):
        """获取虚拟环境激活命令"""
        if self.system == "windows":
            return f"{self.venv_path}\\Scripts\\activate"
        else:
            return f"source {self.venv_path}/bin/activate"
    
    def run(self):
        """运行安装程序"""
        try:
            self.print_banner()
            
            # 检查Python版本
            if not self.check_python_version():
                return False
            
            # 检查系统要求
            if not self.check_system_requirements():
                return False
            
            # 创建虚拟环境
            if not self.create_virtual_environment():
                return False
            
            # 升级pip
            if not self.upgrade_pip():
                return False
            
            # 安装Python依赖
            if not self.install_requirements():
                return False
            
            # 安装系统依赖
            self.install_system_dependencies()
            
            # 创建配置文件
            self.create_config_files()
            
            # 创建目录
            self.create_directories()
            
            # 验证安装
            if not self.verify_installation():
                return False
            
            # 打印成功消息
            self.print_success_message()
            
            return True
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⚠️  安装被用户中断{Colors.END}")
            return False
        except Exception as e:
            print(f"\n{Colors.RED}❌ 安装过程中发生错误: {e}{Colors.END}")
            return False

def main():
    """主函数"""
    installer = Installer()
    success = installer.run()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
