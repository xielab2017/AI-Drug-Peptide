#!/usr/bin/env python3
"""
AI-Drug-Peptide V2.0 本地安装版启动器
双击即可运行，无需命令行
"""

import sys
import os
import webbrowser
import threading
import time

# 获取当前目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)
    webbrowser.open("http://localhost:5000")

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║        🧬 AI-Drug-Peptide V2.0                        ║
║                                                          ║
║   本地网页版启动中...                                   ║
║   请在浏览器中打开: http://localhost:5000              ║
║                                                          ║
║   按 Ctrl+C 停止服务                                    ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # 切换到web目录
    web_dir = os.path.join(CURRENT_DIR, "research_hub", "web")
    if os.path.exists(web_dir):
        os.chdir(web_dir)
    
    # 启动浏览器
    threading.Thread(target=open_browser, daemon=True).start()
    
    # 启动Flask
    try:
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=False)
    except ImportError:
        print("❌ 请先安装依赖:")
        print("   pip install flask")
        print()
        input("按回车键退出...")
    except KeyboardInterrupt:
        print("\n\n👋 服务已停止")

if __name__ == "__main__":
    main()
