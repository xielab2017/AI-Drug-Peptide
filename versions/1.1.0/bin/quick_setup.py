#!/usr/bin/env python3
"""
Quick Peptide Environment Setup - Python Version
A simplified Python-only version of the environment setup

This script provides the same functionality as the shell script
but written entirely in Python for cross-platform compatibility.
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

class PeptideQuickSetup:
    """Quick setup class for peptide environment"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.python_exe = sys.executable
        self.home = Path.home()
        self.config_dir = self.home / '.peptide_env'
        
        # Colors for output
        self.colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'bold': '\033[1m',
            'end': '\033[0m'
        }
        
    def log(self, message, color='blue'):
        """Print colored log message"""
        color_code = self.colors.get(color, '')
        print(f"{color_code}[{message}]{self.colors['end']}")
        
    def success(self, message):
        """Print success message"""
        print(f"{self.colors['green']}✓ {message}{self.colors['end']}")
        
    def error(self, message):
        """Print error message"""
        print(f"{self.colors['red']}✗ {message}{self.colors['end']}")
        
    def warning(self, message):
        """Print warning message"""
        print(f"{self.colors['yellow']}⚠ {message}{self.colors['end']}")
        
    def run_command(self, cmd, check=True, capture_output=True):
        """Run command and return result"""
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                check=check, 
                capture_output=capture_output, 
                text=True
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, "", str(e)
            
    def check_package_manager(self):
        """Detect available package manager"""
        package_managers = {
            'linux': {
                'apt': 'apt-get',
                'yum': 'yum',
                'dnf': 'dnf',
                'portage': 'emerge',  # Gentoo
            },
            'darwin': {'brew': 'brew'},  # macOS
            'windows': {'choco': 'choco'},  # Windows Chocolatey
        }
        
        managers = package_managers.get(self.system, {})
        
        for name, cmd in managers.items():
            success, _, _ = self.run_command(f"which {cmd}", check=False)
            if success:
                self.success(f"Found package manager: {name}")
                return name, cmd
                
        self.warning("No compatible package manager found")
        return None, None
        
    def install_basic_tools(self):
        """Install basic system tools"""
        self.log("Installing basic tools...")
        
        pm_name, pm_cmd = self.check_package_manager()
        
        if not pm_name:
            self.warning("Skipping basic tool installation - no package manager")
            return
            
        install_packages = {
            'linux': {
                'apt': ['curl', 'wget', 'unzip', 'build-essential'],
                'yum': ['curl', 'wget', 'unzip', 'gcc', 'gcc-c++', 'make'],
                'dnf': ['curl', 'wget', 'unzip', 'gcc', 'gcc-c++', 'make'],
            },
            'darwin': {'brew': ['curl', 'wget']},
            'windows': {'choco': ['curl', 'wget', '7zip']},
        }
        
        packages = install_packages.get(self.system, {}).get(pm_name, [])
        
        if packages:
            install_cmd = f"{pm_cmd} install -y " + " ".join(packages)
            if self.system == 'linux':
                install_cmd = f"sudo {install_cmd}"
                
            success, stdout, stderr = self.run_command(install_cmd)
            if success:
                self.success("Basic tools installed successfully")
            else:
                self.error(f"Failed to install basic tools: {stderr}")
                
    def check_tool(self, tool_name, check_command=None):
        """Check if tool is installed"""
        cmd = check_command or f"{tool_name} --version"
        success, stdout, stderr = self.run_command(cmd, check=False)
        
        if success:
            version_line = stdout.split('\n')[0] if stdout else "Unknown version"
            self.success(f"{tool_name}: {version_line}")
            return True
        else:
            self.error(f"{tool_name}: Not installed")
            return False
            
    def install_git(self):
        """Install Git if not present"""
        if self.check_tool("Git"):
            return
            
        self.log("Installing Git...")
        pm_name, pm_cmd = self.check_package_manager()
        
        install_commands = {
            'linux': 'apt install -y git' if pm_name == 'apt' else 'yum install -y git',
            'darwin': 'brew install git',
            'windows': 'choco install -y git',
        }
        
        cmd = install_commands.get(self.system, "")
        if cmd and pm_name:
            if self.system == 'linux':
                cmd = f"sudo {cmd}"
                
            success, _, stderr = self.run_command(cmd)
            if success:
                self.success("Git installed successfully")
            else:
                self.error(f"Failed to install Git: {stderr}")
                
    def check_conda(self):
        """Check conda installation"""
        if self.check_tool("Conda", "conda --version"):
            # Check if we can create environments
            success, _, _ = self.run_command("conda env list", check=False)
            if success:
                return True
                
        return False
        
    def install_conda(self):
        """Install conda/anaconda"""
        if self.check_conda():
            return
            
        self.log("Installing Anaconda...")
        
        # Determine installer URL based on system
        installer_urls = {
            'linux': "https://repo.anaconda.com/archive/Anaconda3-2023.09-Linux-x86_64.sh",
            'darwin': "https://repo.anaconda.com/archive/Anaconda3-2023.09-MacOSX-arm64.sh" 
                      if platform.machine() == 'arm64' else 
                      "https://repo.anaconda.com/archive/Anaconda3-2023.09-MacOSX-x86_64.sh",
        }
        
        if self.system == 'windows':
            self.log("For Windows, please download Anaconda from anaconda.com")
            return
            
        url = installer_urls.get(self.system)
        if not url:
            self.error("Unsupported system for automatic conda installation")
            return
            
        installer_file = Path.home() / f'anaconda-installer_{platform.machine()}.sh'
        
        # Download installer
        success, _, stderr = self.run_command(f"curl -L -o {installer_file} {url}")
        if success:
            self.success("Downloaded Anaconda installer")
        else:
            self.error(f"Failed to download installer: {stderr}")
            return
            
        # Install conda
        install_cmd = f"bash {installer_file} -b -p {self.home}/anaconda3"
        success, _, stderr = self.run_command(install_cmd)
        
        if success:
            self.success("Anaconda installed successfully")
            
            # Add to PATH
            bashrc = self.home / '.bashrc'
            if bashrc.exists():
                with open(bashrc, 'a') as f:
                    f.write('\nexport PATH="$HOME/anaconda3/bin:$PATH"\n')
                    
            # Update current PATH
            os.environ['PATH'] = f"{self.home}/anaconda3/bin:{os.environ['PATH']}"
            
        else:
            self.error(f"Failed to install conda: {stderr}")
            
        # Clean up installer
        installer_file.unlink(missing_ok=True)
        
    def setup_conda_environment(self):
        """Setup conda environment with bioinformatics packages"""
        self.log("Setting up conda environment...")
        
        # Ensure conda is available
        if not self.check_conda():
            self.error("Conda not available, skipping environment setup")
            return
            
        # Create environment
        env_cmd = "conda create -n peptide_dev python=3.9 -y"
        success, _, stderr = self.run_command(env_cmd)
        
        if not success:
            self.error(f"Failed to create environment: {stderr}")
            return
            
        self.success("Created conda environment 'peptide_dev'")
        
        # Install packages
        packages = [
            "numpy", "pandas", "scikit-learn", "matplotlib", 
            "seaborn", "jupyter", "ipython", "biopython",
            "streamlit", "transformers", "torch", "psycopg2",
            "reportlab", "py2neo"
        ]
        
        for package in packages:
            self.log(f"Installing {package}...")
            cmd = f"conda run -n peptide_dev pip install {package}"
            success, _, stderr = self.run_command(cmd)
            
            if success:
                self.success(f"Installed {package}")
            else:
                self.error(f"Failed to install {package}: {stderr}")
                
    def setup_directories(self):
        """Create necessary directories"""
        self.log("Setting up directories...")
        
        dirs_to_create = [
            self.config_dir,
            self.home / 'peptide_models',  # User-accessible models directory
            self.config_dir / 'scripts',
            self.config_dir / 'configs',
        ]
        
        for directory in dirs_to_create:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                self.success(f"Created directory: {directory}")
            except PermissionError:
                self.warning(f"Permission denied for: {directory}")
                self.warning("You may need to create this directory manually with sudo")
                
    def create_config_files(self):
        """Create configuration files"""
        self.log("Creating configuration files...")
        
        # Environment configuration
        config = {
            'environment_name': 'peptide_dev',
            'python_version': '3.9',
            'system': self.system,
            'packages': [
                'biopython', 'numpy', 'pandas', 'sklearn',
                'matplotlib', 'seaborn', 'streamlit',
                'transformers', 'torch', 'reportlab'
            ],
            'directories': {
                'config': str(self.config_dir),
                'models': str(self.home / 'peptide_models'),
                'data': str(self.home / 'peptide_data')
            }
        }
        
        config_file = self.config_dir / 'environment_config.json'
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        self.success(f"Configuration saved to {config_file}")
        
        # Create activation script
        activation_script = self.config_dir / 'activate_env.sh'
        script_content = '''#!/bin/bash
# Peptide Environment Activation Script

echo "Activating peptide environment..."
conda activate peptide_dev

if [ $? -eq 0 ]; then
    echo "✓ Environment activated successfully"
    echo "✓ Current environment: peptide_dev"
    echo "✓ Python version: $(python --version)"
    echo ""
    echo "Available tools:"
    echo "  - Biopython: $(python -c 'import Bio; print(Bio.__version__)' 2>/dev/null || echo 'Not available')"
    echo "  - PyTorch: $(python -c 'import torch; print(torch.__version__)' 2>/dev/null || echo 'Not available')"
    echo "  - Streamlit: $(python -c 'import streamlit; print(streamlit.__version__)' 2>/dev/null || echo 'Not available')"
    echo ""
    echo "To test the environment:"
    echo "  python environment_manager.py --test"
    echo ""
else
    echo "✗ Failed to activate environment"
    exit 1
fi
'''
        
        with open(activation_script, 'w') as f:
            f.write(script_content)
            
        os.chmod(activation_script, 0o755)
        self.success(f"Activation script created: {activation_script}")
        
    def generate_report(self):
        """Generate installation report"""
        self.log("Generating installation report...")
        
        report_lines = [
            "="*60,
            "PEPTIDE ENVIRONMENT SETUP REPORT",
            "="*60,
            "",
            f"System: {platform.platform()}",
            f"Python: {sys.version}",
            f"Setup completed: {platform.node()}",
            "",
            "INSTALLATION STATUS:",
            "-"*30,
        ]
        
        # Check tools
        tools_to_check = [
            ("Git", "git --version"),
            ("Conda", "conda --version"),
            ("Python packages", "conda run -n peptide_dev python -c 'import sys; print(f\"Python {sys.version}\")'")
        ]
        
        for tool_name, cmd in tools_to_check:
            success, output, _ = self.run_command(cmd, check=False)
            status = "✓ OK" if success else "✗ FAILED"
            report_lines.append(f"{tool_name:20} | {status}")
            
        report_lines.extend([
            "",
            "DIRECTORIES CREATED:",
            "-"*30,
            f"Config Directory: {self.config_dir}",
            f"Models Directory: /data/models",
            f"Activation Script: {self.config_dir / 'activate_env.sh'}",
            "",
            "NEXT STEPS:",
            "-"*30,
            "1. Run: source ~/.peptide_env/activate_env.sh",
            "2. Test: python environment_manager.py --test",
            "3. Install additional bioinformatics tools manually",
            "",
            "MANUAL INSTALLATIONS REQUIRED:",
            "-"*30,
            "- SignalP 6.0: Download from DTU website",
            "- ProGen2 weights: Run download script when ready",
            "- Docker: Install from docker.com if needed",
            "",
            "="*60,
        ])
        
        report_content = "\n".join(report_lines)
        
        # Print report
        print("\n" + report_content)
        
        # Save report
        report_file = self.config_dir / 'install_report.txt'
        with open(report_file, 'w') as f:
            f.write(report_content)
            
        self.success(f"Report saved to {report_file}")
        
    def run_setup(self):
        """Run complete setup"""
        self.log("Starting Peptide Environment Quick Setup")
        self.log("This will install the basic environment dependencies")
        
        print(f"""
System detected: {platform.system()} {platform.release()}
Python executable: {self.python_exe}
Target directory: {self.config_dir}

Proceeding with installation...
        """)
        
        # Run setup steps
        self.setup_directories()
        self.install_basic_tools()
        self.install_git()
        self.install_conda()
        
        if self.check_conda():
            self.setup_conda_environment()
            
        self.create_config_files()
        self.generate_report()
        
        self.log("Setup completed!")
        print(f"""
✓ Environment setup finished
✓ Configuration saved to {self.config_dir}
✓ Report generated with installation status

Next steps:
  1. Activate environment: source {self.config_dir / 'activate_env.sh'}
  2. Test installation: python environment_manager.py --test
  3. Continue with manual tool installations as needed
        """)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Quick Peptide Environment Setup')
    parser.add_argument('--skip-conda', action='store_true',
                       help='Skip conda installation')
    parser.add_argument('--skip-tools', action='store_true', 
                       help='Skip basic tool installation')
    parser.add_argument('--config-only', action='store_true',
                       help='Only create configuration files')
    
    args = parser.parse_args()
    
    setup = PeptideQuickSetup()
    
    if args.config_only:
        setup.setup_directories()
        setup.create_config_files()
        return
        
    setup.run_setup()


if __name__ == "__main__":
    main()
