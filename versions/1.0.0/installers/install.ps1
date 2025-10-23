# AI-Drug Peptide V1.0 - Windows PowerShell 一键安装脚本

# 设置错误处理
$ErrorActionPreference = "Stop"

# 颜色定义
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    Cyan = "Cyan"
    White = "White"
}

# 打印横幅
function Print-Banner {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    AI-Drug Peptide V1.0                     ║" -ForegroundColor Cyan
    Write-Host "║              AI驱动的肽类药物开发平台                          ║" -ForegroundColor Cyan
    Write-Host "║                                                              ║" -ForegroundColor Cyan
    Write-Host "║  🧬 蛋白相互作用分析  🔬 分子对接预测  📊 保守性分析  🎯 肽优化  ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "系统信息:" -ForegroundColor Yellow
    Write-Host "  • 操作系统: $([System.Environment]::OSVersion.VersionString)" -ForegroundColor White
    Write-Host "  • 架构: $([System.Environment]::GetEnvironmentVariable('PROCESSOR_ARCHITECTURE'))" -ForegroundColor White
    Write-Host "  • 用户: $([System.Environment]::UserName)" -ForegroundColor White
    Write-Host "  • 安装路径: $(Get-Location)" -ForegroundColor White
    Write-Host ""
}

# 检查系统要求
function Test-Requirements {
    Write-Host "🔍 检查系统要求..." -ForegroundColor Blue
    
    # 检查Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python版本: $pythonVersion" -ForegroundColor Green
            
            # 检查Python版本
            $version = python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))" 2>&1
            $majorMinor = [version]::new($version.Split('.')[0], $version.Split('.')[1])
            $requiredVersion = [version]::new(3, 8)
            
            if ($majorMinor -ge $requiredVersion) {
                Write-Host "✅ Python版本检查通过" -ForegroundColor Green
            } else {
                Write-Host "❌ Python版本过低，需要3.8或更高版本" -ForegroundColor Red
                Write-Host "请访问 https://www.python.org/downloads/ 下载最新版本" -ForegroundColor Cyan
                exit 1
            }
        } else {
            throw "Python not found"
        }
    } catch {
        Write-Host "❌ 未找到Python" -ForegroundColor Red
        Write-Host "请先安装Python: https://www.python.org/downloads/" -ForegroundColor Cyan
        exit 1
    }
    
    # 检查pip
    try {
        $pipVersion = pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ pip已安装: $pipVersion" -ForegroundColor Green
        } else {
            throw "pip not found"
        }
    } catch {
        Write-Host "❌ 未找到pip" -ForegroundColor Red
        Write-Host "请重新安装Python并确保包含pip" -ForegroundColor Cyan
        exit 1
    }
    
    # 检查网络连接
    try {
        $response = Test-NetConnection -ComputerName "pypi.org" -Port 443 -InformationLevel Quiet
        if ($response) {
            Write-Host "✅ 网络连接正常" -ForegroundColor Green
        } else {
            Write-Host "⚠️  网络连接可能有问题，安装过程可能较慢" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️  无法测试网络连接" -ForegroundColor Yellow
    }
    
    # 检查磁盘空间
    $drive = Get-Location | Get-Volume
    $freeSpaceGB = [math]::Round($drive.SizeRemaining / 1GB, 2)
    if ($freeSpaceGB -lt 2) {
        Write-Host "⚠️  磁盘空间可能不足 (${freeSpaceGB}GB可用)" -ForegroundColor Yellow
        Write-Host "推荐至少2GB可用空间" -ForegroundColor Cyan
    } else {
        Write-Host "✅ 磁盘空间检查通过 (${freeSpaceGB}GB可用)" -ForegroundColor Green
    }
}

# 安装系统依赖
function Install-SystemDependencies {
    Write-Host "🔧 检查系统依赖..." -ForegroundColor Blue
    
    # 检查Chocolatey
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Host "✅ 检测到Chocolatey" -ForegroundColor Green
        Write-Host "建议安装系统包: python, curl, git" -ForegroundColor Cyan
        Write-Host "请手动运行以下命令安装:" -ForegroundColor Yellow
        Write-Host "choco install python curl git" -ForegroundColor White
    } else {
        Write-Host "⚠️  未检测到Chocolatey" -ForegroundColor Yellow
        Write-Host "建议安装Chocolatey: https://chocolatey.org/" -ForegroundColor Cyan
    }
    
    # 检查Git
    if (Get-Command git -ErrorAction SilentlyContinue) {
        Write-Host "✅ Git已安装" -ForegroundColor Green
    } else {
        Write-Host "⚠️  未检测到Git" -ForegroundColor Yellow
        Write-Host "建议安装Git: https://git-scm.com/download/win" -ForegroundColor Cyan
    }
}

# 创建虚拟环境
function New-VirtualEnvironment {
    Write-Host "🔧 创建虚拟环境..." -ForegroundColor Blue
    
    if (Test-Path "venv") {
        Write-Host "⚠️  虚拟环境已存在" -ForegroundColor Yellow
        $response = Read-Host "是否重新创建？(y/N)"
        if ($response -eq "y" -or $response -eq "Y") {
            Remove-Item -Recurse -Force "venv"
        } else {
            Write-Host "✅ 使用现有虚拟环境" -ForegroundColor Green
            return
        }
    }
    
    python -m venv venv
    Write-Host "✅ 虚拟环境创建成功" -ForegroundColor Green
}

# 安装Python依赖
function Install-PythonDependencies {
    Write-Host "📦 安装Python依赖包..." -ForegroundColor Blue
    
    # 激活虚拟环境
    $activateScript = ".\venv\Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        & $activateScript
    } else {
        Write-Host "❌ 虚拟环境激活脚本未找到" -ForegroundColor Red
        exit 1
    }
    
    # 升级pip
    Write-Host "升级pip..." -ForegroundColor Cyan
    python -m pip install --upgrade pip
    
    # 安装基础依赖
    Write-Host "安装基础依赖..." -ForegroundColor Cyan
    pip install "numpy>=1.21.0" "pandas>=1.3.0" "requests>=2.25.0" "pyyaml>=6.0"
    
    # 安装完整依赖
    if (Test-Path "requirements.txt") {
        Write-Host "安装完整依赖列表..." -ForegroundColor Cyan
        pip install -r requirements.txt
    } else {
        Write-Host "⚠️  未找到requirements.txt文件" -ForegroundColor Yellow
    }
    
    Write-Host "✅ Python依赖安装成功" -ForegroundColor Green
}

# 创建项目结构
function New-ProjectStructure {
    Write-Host "📁 创建项目结构..." -ForegroundColor Blue
    
    # 创建目录
    $directories = @(
        "data", "data\cache", "data\input", "data\output",
        "logs", "reports", "cache", "cache\docking_logs", "cache\receptors",
        "config"
    )
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    # 创建配置文件
    $configContent = @"
{
  "version": "1.0.0",
  "system": {
    "platform": "windows",
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
"@
    
    $configContent | Out-File -FilePath "config\config.json" -Encoding UTF8
    
    Write-Host "✅ 项目结构创建成功" -ForegroundColor Green
}

# 验证安装
function Test-Installation {
    Write-Host "🔍 验证安装..." -ForegroundColor Blue
    
    # 激活虚拟环境
    $activateScript = ".\venv\Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        & $activateScript
    }
    
    # 测试Python导入
    Write-Host "测试Python模块导入..." -ForegroundColor Cyan
    
    $testScript = @"
import sys
modules = ['numpy', 'pandas', 'requests', 'yaml']
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}: 导入成功')
    except ImportError as e:
        print(f'❌ {module}: 导入失败 - {e}')
        sys.exit(1)
"@
    
    python -c $testScript
    
    Write-Host "✅ 安装验证完成" -ForegroundColor Green
}

# 打印成功消息
function Show-SuccessMessage {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                    🎉 安装成功！ 🎉                          ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "🚀 快速开始:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. 激活虚拟环境:" -ForegroundColor White
    Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "2. 启动应用:" -ForegroundColor White
    Write-Host "   python launch.py" -ForegroundColor White
    Write-Host ""
    Write-Host "3. 启动网页端:" -ForegroundColor White
    Write-Host "   python dashboard.py" -ForegroundColor White
    Write-Host ""
    Write-Host "📚 更多信息:" -ForegroundColor Cyan
    Write-Host "   • 查看README.md了解详细使用方法"
    Write-Host "   • 访问 http://localhost:8080 查看Prefect仪表板"
    Write-Host "   • 查看logs/目录了解运行日志"
    Write-Host ""
    Write-Host "💡 提示:" -ForegroundColor Yellow
    Write-Host "   • 首次运行可能需要下载数据，请保持网络连接"
    Write-Host "   • 如遇问题，请查看logs/目录下的日志文件"
    Write-Host "   • 支持macOS、Windows、Linux多平台"
    Write-Host ""
    Write-Host "感谢使用AI-Drug Peptide V1.0！" -ForegroundColor Green
}

# 主函数
function Main {
    try {
        Print-Banner
        Test-Requirements
        Install-SystemDependencies
        New-VirtualEnvironment
        Install-PythonDependencies
        New-ProjectStructure
        Test-Installation
        Show-SuccessMessage
    } catch {
        Write-Host ""
        Write-Host "❌ 安装过程中发生错误: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "请检查错误信息并重试" -ForegroundColor Yellow
        exit 1
    }
}

# 运行主函数
Main
