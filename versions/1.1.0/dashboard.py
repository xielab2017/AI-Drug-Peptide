#!/usr/bin/env python3
"""
AI-Drug Peptide V1.0 - Prefect仪表板启动脚本
AI驱动的肽类药物开发平台
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path
import argparse

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

class DashboardLauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.host = "localhost"
        self.port = 8080
        
    def print_banner(self):
        """打印启动横幅"""
        banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                AI-Drug Peptide Dashboard V1.0               ║
║              Prefect工作流管理仪表板                          ║
║                                                              ║
║  📊 实时监控  🔄 任务管理  📈 数据可视化  ⚙️ 工作流控制  ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}

{Colors.YELLOW}服务信息:{Colors.END}
  • 主机: {self.host}
  • 端口: {self.port}
  • 访问地址: http://{self.host}:{self.port}
  • 工作目录: {self.project_root}
"""
        print(banner)
    
    def check_prefect(self):
        """检查Prefect是否安装"""
        print(f"{Colors.BLUE}🔍 检查Prefect安装...{Colors.END}")
        
        try:
            import prefect
            print(f"{Colors.GREEN}✅ Prefect已安装: {prefect.__version__}{Colors.END}")
            return True
        except ImportError:
            print(f"{Colors.RED}❌ Prefect未安装{Colors.END}")
            print(f"{Colors.CYAN}正在安装Prefect...{Colors.END}")
            
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 'prefect>=2.0.0'
                ], check=True)
                print(f"{Colors.GREEN}✅ Prefect安装成功{Colors.END}")
                return True
            except subprocess.CalledProcessError as e:
                print(f"{Colors.RED}❌ Prefect安装失败: {e}{Colors.END}")
                return False
    
    def check_port(self):
        """检查端口是否可用"""
        print(f"{Colors.BLUE}🔍 检查端口可用性...{Colors.END}")
        
        import socket
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.host, self.port))
                print(f"{Colors.GREEN}✅ 端口 {self.port} 可用{Colors.END}")
                return True
        except OSError:
            print(f"{Colors.YELLOW}⚠️  端口 {self.port} 已被占用{Colors.END}")
            print(f"{Colors.CYAN}尝试使用其他端口...{Colors.END}")
            
            # 尝试其他端口
            for port in range(8081, 8090):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind((self.host, port))
                        self.port = port
                        print(f"{Colors.GREEN}✅ 使用端口 {port}{Colors.END}")
                        return True
                except OSError:
                    continue
            
            print(f"{Colors.RED}❌ 无法找到可用端口{Colors.END}")
            return False
    
    def start_prefect_server(self):
        """启动Prefect服务器"""
        print(f"{Colors.BLUE}🚀 启动Prefect服务器...{Colors.END}")
        
        try:
            # 启动Prefect服务器
            cmd = [
                sys.executable, '-m', 'prefect', 'server', 'start',
                '--host', self.host,
                '--port', str(self.port)
            ]
            
            print(f"{Colors.CYAN}执行命令: {' '.join(cmd)}{Colors.END}")
            
            # 在后台启动服务器
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务器启动
            print(f"{Colors.YELLOW}等待服务器启动...{Colors.END}")
            time.sleep(5)
            
            # 检查进程是否还在运行
            if process.poll() is None:
                print(f"{Colors.GREEN}✅ Prefect服务器启动成功{Colors.END}")
                print(f"{Colors.CYAN}进程ID: {process.pid}{Colors.END}")
                return process
            else:
                stdout, stderr = process.communicate()
                print(f"{Colors.RED}❌ Prefect服务器启动失败{Colors.END}")
                print(f"{Colors.RED}错误输出: {stderr}{Colors.END}")
                return None
                
        except Exception as e:
            print(f"{Colors.RED}❌ 启动Prefect服务器时发生错误: {e}{Colors.END}")
            return None
    
    def open_browser(self):
        """打开浏览器"""
        url = f"http://{self.host}:{self.port}"
        print(f"{Colors.BLUE}🌐 打开浏览器...{Colors.END}")
        
        try:
            webbrowser.open(url)
            print(f"{Colors.GREEN}✅ 浏览器已打开: {url}{Colors.END}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  无法自动打开浏览器: {e}{Colors.END}")
            print(f"{Colors.CYAN}请手动访问: {url}{Colors.END}")
    
    def show_dashboard_info(self):
        """显示仪表板信息"""
        info = f"""
{Colors.GREEN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                    🎉 仪表板启动成功！ 🎉                    ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}

{Colors.CYAN}📊 仪表板信息:{Colors.END}
  • 访问地址: http://{self.host}:{self.port}
  • 工作流管理: 创建、编辑、运行工作流
  • 任务监控: 实时查看任务执行状态
  • 数据可视化: 交互式图表和仪表板
  • 日志查看: 详细的执行日志

{Colors.CYAN}🔧 主要功能:{Colors.END}
  • 工作流设计器: 拖拽式工作流创建
  • 任务调度: 定时任务和事件触发
  • 监控面板: 实时性能监控
  • 错误处理: 自动重试和错误恢复
  • 数据管道: 数据处理和转换

{Colors.YELLOW}💡 使用提示:{Colors.END}
  • 首次使用请查看工作流模板
  • 可以导入现有的工作流配置
  • 支持多种数据源和输出格式
  • 提供详细的API文档

{Colors.CYAN}📚 更多资源:{Colors.END}
  • Prefect文档: https://docs.prefect.io/
  • 示例工作流: ./examples/
  • 配置文件: ./config/
  • 日志文件: ./logs/

{Colors.GREEN}按 Ctrl+C 停止服务器{Colors.END}
"""
        print(info)
    
    def run(self, args):
        """运行仪表板启动器"""
        self.print_banner()
        
        # 检查Prefect
        if not self.check_prefect():
            return False
        
        # 检查端口
        if not self.check_port():
            return False
        
        # 启动服务器
        process = self.start_prefect_server()
        if not process:
            return False
        
        # 打开浏览器
        if not args.no_browser:
            self.open_browser()
        
        # 显示信息
        self.show_dashboard_info()
        
        try:
            # 保持服务器运行
            process.wait()
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⚠️  正在停止服务器...{Colors.END}")
            process.terminate()
            process.wait()
            print(f"{Colors.GREEN}✅ 服务器已停止{Colors.END}")
        
        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AI-Drug Peptide Dashboard V1.0 - Prefect工作流管理仪表板",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dashboard.py                    # 启动仪表板并打开浏览器
  python dashboard.py --no-browser       # 启动仪表板但不打开浏览器
  python dashboard.py --port 9090         # 在指定端口启动
        """
    )
    
    parser.add_argument('--host', type=str, default='localhost',
                       help='服务器主机地址 (默认: localhost)')
    parser.add_argument('--port', type=int, default=8080,
                       help='服务器端口 (默认: 8080)')
    parser.add_argument('--no-browser', action='store_true',
                       help='不自动打开浏览器')
    
    args = parser.parse_args()
    
    # 创建启动器并运行
    launcher = DashboardLauncher()
    launcher.host = args.host
    launcher.port = args.port
    
    success = launcher.run(args)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
