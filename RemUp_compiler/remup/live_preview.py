#!/usr/bin/env python3
"""
RemUp实时预览服务器
"""

import os
import sys
import time
import http.server
import socketserver
import threading
import webbrowser
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 正确的导入语句
from remup.compiler import compile_remup
from remup.html_generator import HTMLGenerator

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, file_path, theme, port):
        self.file_path = file_path
        self.theme = theme
        self.port = port
        self.last_modified = time.time()

    def on_modified(self, event):
        if event.src_path == self.file_path:
            current_time = time.time()
            # 防抖：避免短时间内多次触发
            if current_time - self.last_modified < 1:
                return
            self.last_modified = current_time
            print(f"\n🔄 检测到文件变化: {event.src_path}")
            try:
                # 重新编译
                output_path = compile_remup(self.file_path, theme=self.theme)
                print(f"✅ 重新编译完成: {output_path}")
            except Exception as e:
                print(f"❌ 编译错误: {e}")

def get_available_themes():
    """获取可用主题列表 - 直接从HTMLGenerator获取"""
    generator = HTMLGenerator()
    return generator.get_available_themes()

def get_static_css_dir():
    """获取静态CSS目录 - 直接从HTMLGenerator获取"""
    generator = HTMLGenerator()
    return generator.static_css_dir

def get_project_root():
    """获取项目根目录 - 直接从HTMLGenerator获取"""
    generator = HTMLGenerator()
    return generator.project_root

def start_live_preview(file_path, port=8000, theme='RemStyle'):
    """启动实时预览服务器"""
    print(f"📁 项目根目录: {get_project_root()}")
    print(f"🎨 静态CSS目录: {get_static_css_dir()}")
    
    themes = get_available_themes()
    print(f"📋 发现 {len(themes)} 个可用主题: {', '.join(themes)}")
    print(f"🔧 编译器初始化完成")
    
    # 确保文件路径是绝对路径
    if not os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"❌ 错误：文件不存在: {file_path}")
        return
    
    # 获取文件所在目录
    watch_dir = os.path.dirname(file_path)
    
    # 确保目录存在
    if not os.path.exists(watch_dir):
        print(f"❌ 错误：目录不存在: {watch_dir}")
        return
    
    print(f"📁 监视目录: {watch_dir}")
    print(f"📄 监视文件: {os.path.basename(file_path)}")

    # 初始编译
    try:
        output_path = compile_remup(file_path, theme=theme)
        print(f"✅ 初始编译完成: {output_path}")
    except Exception as e:
        print(f"❌ 初始编译错误: {e}")
        return

    # 启动HTTP服务器
    output_dir = os.path.dirname(output_path)
    os.chdir(output_dir)  # 改变工作目录到输出目录
    
    # 使用ThreadingTCPServer避免阻塞
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.ThreadingTCPServer(("", port), Handler)
    
    # 启动服务器线程
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    print(f"🌐 启动实时预览服务器在 http://localhost:{port}")
    webbrowser.open(f"http://localhost:{port}/{os.path.basename(output_path)}")

    # 启动文件监视
    try:
        event_handler = FileChangeHandler(file_path, theme, port)
        observer = Observer()
        observer.schedule(event_handler, watch_dir, recursive=False)
        observer.start()
        
        print("🔄 实时预览已启动，文件变化将自动重新编译...")
        print("按 Ctrl+C 停止预览")
        
        # 主线程等待中断信号
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 停止实时预览")
    except Exception as e:
        print(f"❌ 文件监视器启动失败: {e}")
        print("💡 实时预览功能受限，但HTTP服务器仍在运行")
    finally:
        try:
            observer.stop()
            observer.join()
        except:
            pass
        httpd.shutdown()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("RemUp编译器 v1.0.0 已加载成功！支持文件格式: .ru, .remup")
        print("用法: python -m remup.live_preview <remup文件> [端口] [主题]")
        sys.exit(1)

    file_path = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    theme = sys.argv[3] if len(sys.argv) > 3 else 'RemStyle'

    start_live_preview(file_path, port, theme)