#!/usr/bin/env python3
"""
WebSocket实时预览服务器 - 修复属性缺失和事件循环问题
"""

import os
import sys
import time
import json
import asyncio
import websockets
import threading
import http.server
import socketserver
import webbrowser
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Set, Dict, Any, Optional

# 导入编译器模块
from remup.compiler import compile_remup
from remup.html_generator import HTMLGenerator

class WebSocketPreviewServer:
    """WebSocket实时预览服务器 - 修复版本"""
    
    def __init__(self, file_path: str, http_port: int = 8000, ws_port: int = 8001, theme: str = 'RemStyle'):
        self.file_path = Path(file_path).absolute()
        self.http_port = http_port
        self.ws_port = ws_port
        self.theme = theme
        self.output_path: Optional[str] = None
        
        # WebSocket连接管理
        self.connections: Set[websockets.WebSocketServerProtocol] = set()
        
        # 服务器状态 - 修复：确保所有属性都有初始值
        self.is_running = False
        self.compile_in_progress = False  # 修复：添加缺失的属性
        self.last_compile_time = 0
        
        # 事件循环引用
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        
        print(f"🚀 WebSocket实时预览服务器初始化")
        print(f"📁 监视文件: {self.file_path}")
        print(f"🌐 HTTP端口: {http_port}")
        print(f"🔌 WebSocket端口: {ws_port}")
        print(f"🎨 主题: {theme}")
    
    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        """设置事件循环引用 - 用于跨线程通信"""
        self.loop = loop
    
    async def handle_websocket(self, websocket):
        """处理WebSocket连接 - 修复属性访问"""
        # 获取连接路径信息
        path = websocket.path if hasattr(websocket, 'path') else '/'
        print(f"🔌 新的WebSocket连接: {websocket.remote_address}, 路径: {path}")
        
        # 注册连接
        self.connections.add(websocket)
        print(f"当前连接数: {len(self.connections)}")
        
        try:
            # 发送初始状态
            await self.send_status(websocket, "connected", "连接成功")
            
            # 保持连接
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(websocket, data)
                except json.JSONDecodeError as e:
                    print(f"❌ 无法解析JSON消息: {message}, 错误: {e}")
                except Exception as e:
                    print(f"❌ 处理消息时出错: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            print(f"🔌 WebSocket连接关闭: {websocket.remote_address}")
        except Exception as e:
            print(f"❌ WebSocket处理错误: {e}")
        finally:
            # 移除连接
            if websocket in self.connections:
                self.connections.remove(websocket)
            print(f"🔌 连接断开，剩余连接数: {len(self.connections)}")
    
    async def handle_message(self, websocket, data: Dict[str, Any]):
        """处理客户端消息 - 修复属性访问"""
        try:
            message_type = data.get('type')
            
            if message_type == 'ping':
                # 心跳检测
                await self.send_message(websocket, {'type': 'pong', 'timestamp': time.time()})
                
            elif message_type == 'compile_request':
                # 客户端请求重新编译
                await self.compile_and_notify()
                
            elif message_type == 'get_status':
                # 客户端请求状态信息
                status = await self.get_system_status()
                await self.send_message(websocket, {'type': 'status', 'data': status})
        except Exception as e:
            print(f"❌ 处理消息时出错: {e}")
    
    async def send_message(self, websocket, message: Dict[str, Any]):
        """发送消息到单个客户端"""
        try:
            await websocket.send(json.dumps(message))
        except (websockets.exceptions.ConnectionClosed, AttributeError) as e:
            print(f"❌ 发送消息失败: {e}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """广播消息到所有客户端"""
        if not self.connections:
            return
            
        disconnected = set()
        for websocket in self.connections:
            try:
                await websocket.send(json.dumps(message))
            except (websockets.exceptions.ConnectionClosed, AttributeError):
                disconnected.add(websocket)
        
        # 清理断开的连接
        for websocket in disconnected:
            self.connections.remove(websocket)
    
    async def send_status(self, websocket, status: str, message: str, data: Dict[str, Any] = None):
        """发送状态消息"""
        message_data = {
            'type': 'status',
            'status': status,
            'message': message,
            'timestamp': time.time()
        }
        if data:
            message_data['data'] = data
        
        await self.send_message(websocket, message_data)
    
    async def compile_and_notify(self):
        """编译文件并通知所有客户端 - 修复属性访问"""
        # 修复：确保属性存在
        if not hasattr(self, 'compile_in_progress'):
            self.compile_in_progress = False
            
        if self.compile_in_progress:
            return
            
        self.compile_in_progress = True
        try:
            # 发送编译开始通知
            await self.broadcast({
                'type': 'compile_start',
                'timestamp': time.time(),
                'file': str(self.file_path)
            })
            
            print(f"🔨 开始编译: {self.file_path}")
            
            # 执行编译
            try:
                self.output_path = compile_remup(
                    str(self.file_path), 
                    theme=self.theme
                )
                self.last_compile_time = time.time()
                
                # 重新注入WebSocket客户端脚本
                inject_websocket_client(str(self.output_path), self.ws_port)
                
                # 发送编译成功通知
                await self.broadcast({
                    'type': 'compile_success',
                    'timestamp': self.last_compile_time,
                    'output_path': str(self.output_path),
                    'message': '编译成功'
                })
                
                print(f"✅ 编译完成: {self.output_path}")
                
            except Exception as e:
                # 发送编译错误通知
                error_msg = f"编译错误: {str(e)}"
                await self.broadcast({
                    'type': 'compile_error',
                    'timestamp': time.time(),
                    'error': error_msg,
                    'message': '编译失败'
                })
                
                print(f"❌ {error_msg}")
                
        except Exception as e:
            print(f"❌ 编译通知过程中出错: {e}")
        finally:
            self.compile_in_progress = False
    
    async def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态信息 - 修复属性访问"""
        # 修复：确保所有属性都存在
        status_data = {
            'file_path': str(self.file_path),
            'output_path': str(self.output_path) if self.output_path else None,
            'last_compile_time': getattr(self, 'last_compile_time', 0),
            'theme': self.theme,
            'connections_count': len(self.connections),
            'is_compiling': getattr(self, 'compile_in_progress', False)
        }
        return status_data


class FileChangeHandler(FileSystemEventHandler):
    """文件变化处理器 - 修复事件循环问题"""
    
    def __init__(self, preview_server: WebSocketPreviewServer):
        self.preview_server = preview_server
        self.last_modified = 0
        self.debounce_interval = 0.5  # 防抖间隔（秒）
    
    def on_modified(self, event):
        """文件修改事件处理 - 修复跨线程事件循环问题[8,11](@ref)"""
        if event.src_path == str(self.preview_server.file_path):
            current_time = time.time()
            
            # 防抖处理
            if current_time - self.last_modified < self.debounce_interval:
                return
                
            self.last_modified = current_time
            print(f"\n🔄 检测到文件变化: {event.src_path}")
            
            # 修复：使用线程安全的方式通知主线程[8](@ref)
            if self.preview_server.loop and self.preview_server.loop.is_running():
                # 使用线程安全的call_soon_threadsafe方法
                asyncio.run_coroutine_threadsafe(
                    self.handle_file_change(), 
                    self.preview_server.loop
                )
            else:
                print("⚠️ 事件循环不可用，无法处理文件变化")
    
    async def handle_file_change(self):
        """处理文件变化事件 - 在主线程的事件循环中执行"""
        # 等待一小段时间，确保文件写入完成
        await asyncio.sleep(0.1)
        
        # 执行编译并通知客户端
        await self.preview_server.compile_and_notify()


def make_request_handler_class(output_dir):
    """创建HTTP请求处理器类 - 修复output_dir问题"""
    class PreviewHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            # 使用闭包中的output_dir
            self.directory = str(output_dir)
            super().__init__(*args, directory=self.directory, **kwargs)
        
        def log_message(self, format, *args):
            # 简化日志输出
            print(f"🌐 HTTP请求: {self.address_string()} - {format % args}")
    
    return PreviewHTTPRequestHandler


class PreviewHTTPServer:
    """预览HTTP服务器"""
    
    def __init__(self, port: int, output_dir: Path):
        self.port = port
        self.output_dir = output_dir
        self.server = None
        self.thread = None
    
    def start(self):
        """启动HTTP服务器"""
        # 改变工作目录到输出目录
        os.chdir(str(self.output_dir))
        
        # 创建自定义请求处理器类
        RequestHandlerClass = make_request_handler_class(self.output_dir)
        
        # 启动服务器
        try:
            self.server = socketserver.ThreadingTCPServer(("", self.port), RequestHandlerClass)
            self.server.allow_reuse_address = True
            
            def run_server():
                try:
                    print(f"🌐 HTTP服务器启动在端口 {self.port}")
                    self.server.serve_forever()
                except Exception as e:
                    print(f"❌ HTTP服务器错误: {e}")
            
            self.thread = threading.Thread(target=run_server, daemon=True)
            self.thread.start()
            
        except Exception as e:
            print(f"❌ 启动HTTP服务器失败: {e}")
            raise
    
    def stop(self):
        """停止HTTP服务器"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()


def generate_websocket_client_script(ws_port: int) -> str:
    """生成WebSocket客户端脚本"""
    return f"""
<script>
class RemUpLivePreview {{
    constructor(wsPort = {ws_port}) {{
        this.wsPort = wsPort;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.isConnected = false;
        
        this.init();
    }}
    
    init() {{
        this.createStatusPanel();
        this.connect();
        this.bindEvents();
    }}
    
    createStatusPanel() {{
        // 创建状态面板
        const panel = document.createElement('div');
        panel.id = 'remup-live-preview-panel';
        panel.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            font-family: Arial, sans-serif;
            font-size: 12px;
            z-index: 10000;
            min-width: 200px;
            backdrop-filter: blur(10px);
        `;
        
        panel.innerHTML = `
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <span style="flex: 1;">RemUp Live Preview</span>
                <button id="remup-reload-btn" style="background: #007acc; border: none; color: white; padding: 2px 8px; border-radius: 3px; cursor: pointer; font-size: 10px;">刷新</button>
            </div>
            <div id="remup-status" style="font-size: 11px; opacity: 0.8;">连接中...</div>
            <div id="remup-message" style="font-size: 11px; margin-top: 3px;"></div>
        `;
        
        document.body.appendChild(panel);
    }}
    
    connect() {{
        try {{
            this.ws = new WebSocket(`ws://${{window.location.hostname}}:{ws_port}`);
            
            this.ws.onopen = () => {{
                this.onConnected();
            }};
            
            this.ws.onmessage = (event) => {{
                this.handleMessage(JSON.parse(event.data));
            }};
            
            this.ws.onclose = () => {{
                this.onDisconnected();
            }};
            
            this.ws.onerror = (error) => {{
                this.onError(error);
            }};
            
        }} catch (error) {{
            console.error('WebSocket连接错误:', error);
            this.scheduleReconnect();
        }}
    }}
    
    bindEvents() {{
        // 绑定手动刷新按钮
        const reloadBtn = document.getElementById('remup-reload-btn');
        if (reloadBtn) {{
            reloadBtn.onclick = () => {{
                this.requestCompile();
            }};
        }}
        
        // 键盘快捷键: Ctrl+R 重新编译
        document.addEventListener('keydown', (e) => {{
            if (e.ctrlKey && e.key === 'r') {{
                e.preventDefault();
                this.requestCompile();
            }}
        }});
    }}
    
    onConnected() {{
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.updateStatus('connected', '已连接');
        console.log('✅ WebSocket连接成功');
        
        // 发送初始状态请求
        this.sendMessage({{ type: 'get_status' }});
    }}
    
    onDisconnected() {{
        this.isConnected = false;
        this.updateStatus('disconnected', '连接断开');
        this.scheduleReconnect();
    }}
    
    onError(error) {{
        console.error('WebSocket错误:', error);
        this.updateStatus('error', '连接错误');
    }}
    
    scheduleReconnect() {{
        if (this.reconnectAttempts < this.maxReconnectAttempts) {{
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
            
            this.updateStatus('reconnecting', `尝试重新连接 (${{this.reconnectAttempts}}/${{this.maxReconnectAttempts}})...`);
            
            setTimeout(() => {{
                this.connect();
            }}, delay);
        }} else {{
            this.updateStatus('failed', '连接失败，请检查服务器状态');
        }}
    }}
    
    handleMessage(data) {{
        if (!data || typeof data !== 'object') return;
        
        switch (data.type) {{
            case 'pong':
                // 心跳响应，忽略
                break;
                
            case 'status':
                this.updateStatus('connected', '已连接', data.data);
                break;
                
            case 'compile_start':
                this.updateStatus('compiling', '正在编译...');
                this.showMessage('文件变化检测到，正在重新编译...', 'info');
                break;
                
            case 'compile_success':
                this.updateStatus('success', '编译成功');
                this.showMessage('编译完成，页面即将刷新...', 'success');
                
                // 2秒后刷新页面
                setTimeout(() => {{
                    window.location.reload();
                }}, 100);
                break;
                
            case 'compile_error':
                this.updateStatus('error', '编译错误');
                this.showMessage(data.error, 'error');
                break;
        }}
    }}
    
    updateStatus(status, message, data = null) {{
        const statusEl = document.getElementById('remup-status');
        if (!statusEl) return;
        
        const statusMap = {{
            connected: '🟢 已连接',
            disconnected: '🔴 连接断开',
            reconnecting: '🟡 重新连接中',
            compiling: '🟡 编译中',
            success: '🟢 编译成功',
            error: '🔴 错误',
            failed: '🔴 连接失败'
        }};
        
        statusEl.innerHTML = `${{statusMap[status] || status}} | ${{message}}`;
    }}
    
    showMessage(message, type = 'info') {{
        const messageEl = document.getElementById('remup-message');
        if (!messageEl) return;
        
        const colorMap = {{
            info: '#007acc',
            success: '#00cc00',
            error: '#cc0000'
        }};
        
        messageEl.textContent = message;
        messageEl.style.color = colorMap[type] || '#007acc';
        
        // 3秒后清除消息
        setTimeout(() => {{
            if (messageEl.textContent === message) {{
                messageEl.textContent = '';
            }}
        }}, 3000);
    }}
    
    sendMessage(message) {{
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {{
            this.ws.send(JSON.stringify(message));
        }}
    }}
    
    requestCompile() {{
        this.sendMessage({{ type: 'compile_request' }});
    }}
}}

// 页面加载完成后初始化
if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', () => {{
        new RemUpLivePreview();
    }});
}} else {{
    new RemUpLivePreview();
}}
</script>
"""


def inject_websocket_client(html_path: str, ws_port: int):
    """将WebSocket客户端脚本注入到HTML文件中"""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经注入了客户端脚本
        if 'RemUpLivePreview' in content:
            # 更新现有的脚本
            import re
            pattern = r'<script>\s*class RemUpLivePreview.*?</script>'
            replacement = generate_websocket_client_script(ws_port)
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        else:
            # 在</body>标签前插入客户端脚本
            client_script = generate_websocket_client_script(ws_port)
            if '</body>' in content:
                content = content.replace('</body>', f'{client_script}</body>')
            else:
                content += client_script
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 已注入WebSocket客户端脚本到: {html_path}")
        
    except Exception as e:
        print(f"❌ 注入WebSocket客户端脚本失败: {e}")


async def start_websocket_preview(file_path: str, http_port: int = 8000, ws_port: int = 8001, theme: str = 'RemStyle'):
    """启动WebSocket实时预览服务器 - 修复版本"""
    
    # 验证文件存在
    if not os.path.exists(file_path):
        print(f"❌ 错误：文件不存在: {file_path}")
        return
    
    # 创建预览服务器实例
    preview_server = WebSocketPreviewServer(file_path, http_port, ws_port, theme)
    
    # 初始编译
    try:
        print("🔨 执行初始编译...")
        preview_server.output_path = compile_remup(file_path, theme=theme)
        preview_server.last_compile_time = time.time()
        print(f"✅ 初始编译完成: {preview_server.output_path}")
    except Exception as e:
        print(f"❌ 初始编译错误: {e}")
        return
    
    # 获取输出目录
    output_dir = Path(preview_server.output_path).parent
    
    # 注入WebSocket客户端脚本到HTML文件
    inject_websocket_client(str(preview_server.output_path), ws_port)
    
    # 启动HTTP服务器
    http_server = PreviewHTTPServer(http_port, output_dir)
    try:
        http_server.start()
    except Exception as e:
        print(f"❌ 启动HTTP服务器失败: {e}")
        return
    
    # 设置事件循环引用
    preview_server.set_event_loop(asyncio.get_running_loop())
    
    # 启动文件监视
    file_handler = FileChangeHandler(preview_server)
    observer = Observer()
    try:
        observer.schedule(file_handler, str(preview_server.file_path.parent), recursive=False)
        observer.start()
        print(f"👀 开始监视文件: {preview_server.file_path}")
    except Exception as e:
        print(f"❌ 启动文件监视器失败: {e}")
        return
    
    # 启动WebSocket服务器
    try:
        # 创建handler函数适配器
        async def handler(websocket):
            await preview_server.handle_websocket(websocket)
        
        # 使用新版本的websockets API
        start_server = await websockets.serve(
            handler, 
            "localhost", 
            ws_port
        )
        
        print(f"🔌 WebSocket服务器启动在端口 {ws_port}")
        
        # 修复关键错误：使用 os.path.basename() 而不是 .name
        output_filename = os.path.basename(preview_server.output_path)
        url = f"http://localhost:{http_port}/{output_filename}"
        print(f"🌐 打开浏览器: {url}")
        webbrowser.open(url)
        
        print("🚀 WebSocket实时预览服务器已启动!")
        print("   按 Ctrl+C 停止服务器")
        print("   快捷键: Ctrl+R 手动重新编译")
        
        # 保持服务器运行
        preview_server.is_running = True
        await asyncio.Future()  # 永久运行
        
    except Exception as e:
        print(f"❌ WebSocket服务器启动失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        preview_server.is_running = False
        observer.stop()
        observer.join()
        http_server.stop()


async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("WebSocket实时预览服务器 v1.0 - 完整修复版")
        print("用法: python -m remup.websocket_preview <remup文件> [HTTP端口] [WebSocket端口] [主题]")
        return
    
    # 解析命令行参数
    file_path = sys.argv[1]
    http_port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    ws_port = int(sys.argv[3]) if len(sys.argv) > 3 else 8001
    theme = sys.argv[4] if len(sys.argv) > 4 else 'RemStyle'
    
    # 启动预览服务器
    await start_websocket_preview(file_path, http_port, ws_port, theme)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器运行错误: {e}")
        import traceback
        traceback.print_exc()