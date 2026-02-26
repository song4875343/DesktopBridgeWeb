import sys
import inspect
import mimetypes
# import uvicorn
import webview
# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
from typing import Any, List, Dict, Union
# from fastapi import Body,HTTPException

# === 核心修正：强制注册 MIME 类型 ===
# 解决 Windows 下 .js 文件被识别为 text/plain 导致浏览器不加载的问题
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

# 引入你的业务逻辑
from core import AppCore

core = AppCore()

# === 桌面端专用的系统级 IO 实现（使用 pywebview 原生对话框）===
def _desktop_open_file():
    """使用 Windows 原生文件选择对话框"""
    # pywebview 的 create_file_dialog 返回元组 (file_types, path)
    result = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG)
    
    if not result or not result[0]:  # 用户取消
        return None
    
    path = result[0]  # 获取文件路径
    import base64
    with open(path, "rb") as f:
        content = f.read()
        b64 = base64.b64encode(content).decode('utf-8')
        import os
        return {"name": os.path.basename(path), "content": b64}

def _desktop_save_file(filename, content):
    """使用 Windows 原生保存对话框"""
    result = webview.windows[0].create_file_dialog(
        webview.SAVE_DIALOG,
        save_filename=filename
    )
    
    if not result or not result[0]:  # 用户取消
        return {"status": "cancelled"}
    
    path = result[0]
    import base64
    # 兼容性处理：如果前端传了 data: 前缀，去掉它
    if "," in content:
        _, content = content.split(",", 1)
    data = base64.b64decode(content)
    with open(path, "wb") as f:
        f.write(data)
    return {"status": "success", "path": path}

# === API 构造工厂 ===
class UniversalApi:
    def sys_open_file(self): return _desktop_open_file()
    def sys_save_file(self, n, c): return _desktop_save_file(n, c)

# 动态挂载 Core 方法
for name, method in inspect.getmembers(core, predicate=inspect.ismethod):
    if not name.startswith('_'):
        setattr(UniversalApi, name, method)


# === 启动入口 ===
if __name__ == '__main__':
    print("🖥 启动 桌面模式...")
    api = UniversalApi()
    webview.create_window("Vibe App", "index.html", js_api=api, width=800, height=600)
    webview.start(debug=False)