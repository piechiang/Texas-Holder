#!/usr/bin/env python3
"""
Quick start script for Texas Hold'em Web Calculator
德州扑克网页计算器快速启动脚本
"""

import os
import sys
import webbrowser
import time
from threading import Timer

def check_dependencies():
    """Check if Flask is installed"""
    try:
        import flask
        print("✅ Flask found / Flask已找到")
        return True
    except ImportError:
        print("❌ Flask not found. Installing... / Flask未找到，正在安装...")
        os.system("pip install -r requirements.txt")
        try:
            import flask
            print("✅ Flask installed successfully / Flask安装成功")
            return True
        except ImportError:
            print("❌ Failed to install Flask / Flask安装失败")
            return False

def open_browser():
    """Open browser after server starts"""
    time.sleep(2)
    print("🌐 Opening browser... / 正在打开浏览器...")
    webbrowser.open('http://localhost:5000')

def main():
    print("🎰 Texas Hold'em Web Calculator Launcher")
    print("德州扑克网页计算器启动器")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("Please install Flask manually: pip install Flask")
        print("请手动安装Flask: pip install Flask")
        return
    
    # Check if web_app.py exists
    if not os.path.exists('web_app.py'):
        print("❌ web_app.py not found in current directory")
        print("❌ 当前目录未找到web_app.py")
        return
    
    print("\n🚀 Starting web server... / 正在启动网页服务器...")
    print("📱 The interface works on mobile devices / 界面支持移动设备")
    print("🔄 Press Ctrl+C to stop the server / 按Ctrl+C停止服务器")
    print("\n" + "=" * 50)
    
    # Schedule browser opening
    Timer(2.0, open_browser).start()
    
    # Import and start the Flask app
    try:
        from web_app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye! / 服务器已停止。再见！")
    except Exception as e:
        print(f"\n❌ Error starting server / 启动服务器错误: {e}")

if __name__ == "__main__":
    main()