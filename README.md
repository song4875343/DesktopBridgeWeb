# VibeSync

一个优雅的 Python + JavaScript 双端开发框架，让你的应用同时运行在桌面和 Web 平台。

## 核心理念

通过两个核心文件（`bridge.js` + `main.py`），实现"写一次，双端运行"：

- 编写业务逻辑（`core.py`）
- 编写 UI 界面（`index.html`）
- 自动适配桌面（pywebview）和 Web（浏览器）环境

无需关心平台差异，框架自动处理 API 调用、文件 I/O 等跨平台问题。

## 特性

- 🎯 **零配置切换**：同一套代码，桌面/Web 自动适配
- 🔌 **智能代理**：JavaScript 端自动检测运行环境并路由 API 调用
- 📁 **统一 I/O**：文件打开/保存在两端使用相同接口
- 🚀 **极简开发**：只需编写 `core.py` 业务逻辑和 HTML 界面
- 🔧 **动态挂载**：Python 方法自动暴露给前端调用

## 快速开始

### 安装依赖

```bash
pip install pywebview
```

### 项目结构

```
your-app/
├── bridge.js       # 前端桥接层（自动适配环境）
├── main.py         # 启动入口（桌面模式）
├── core.py         # 业务逻辑（你的代码）
└── index.html      # UI 界面（你的代码）
```

### 编写业务逻辑

在 `core.py` 中定义方法：

```python
class AppCore:
    def greet(self, name):
        return f"Hello, {name}!"
    
    def calculate(self, a, b):
        return {"result": a + b}
```

### 前端调用

在 `index.html` 中导入并使用：

```html
<script type="module">
import { bridge } from './bridge.js';

// 调用后端方法（桌面/Web 自动适配）
const result = await bridge.greet("World");
console.log(result); // "Hello, World!"

// 文件操作（统一接口）
const file = await bridge.openFile();
if (file) {
    console.log(file.name, file.content);
}
</script>
```

### 运行

```bash
# 桌面模式
python main.py

# Web 模式（需自行实现 FastAPI 服务端）
# uvicorn server:app --reload
```

## 工作原理

### 桌面模式（pywebview）

1. `main.py` 启动 pywebview 窗口
2. `bridge.js` 检测到 `window.pywebview` 存在
3. 前端调用直接通过 `pywebview.api` 同步到 Python

### Web 模式（浏览器）

1. 启动 FastAPI/Flask 等 Web 服务
2. `bridge.js` 检测到无 `window.pywebview`
3. 前端调用通过 `fetch('/api/method')` 发送 HTTP 请求

### 魔法代理（Magic Proxy）

`bridge.js` 使用 ES6 Proxy 实现动态方法拦截：

```javascript
const bridge = new Proxy(ioShim, {
    get(target, prop) {
        // 运行时检测环境并路由调用
        if (window.pywebview) {
            return window.pywebview.api[prop];
        } else {
            return (...args) => fetch(`/api/${prop}`, ...);
        }
    }
});
```

## 核心文件说明

### `bridge.js`

- 智能环境检测（桌面 vs Web）
- 统一 API 调用接口
- 内置文件 I/O 封装（`openFile`/`saveFile`）

### `main.py`

- 动态挂载 `core.py` 的所有公开方法
- 提供桌面端系统级 I/O（原生文件对话框）
- 修复 Windows MIME 类型问题

## 开发规则

1. **业务逻辑**：只写 `core.py`，方法自动暴露
2. **UI 界面**：只写 `index.html`，通过 `bridge` 调用后端
3. **不要修改** `bridge.js` 和 `main.py`（除非扩展框架）

## 扩展

### 添加新的系统级功能

在 `UniversalApi` 类中添加 `sys_` 前缀的方法：

```python
class UniversalApi:
    def sys_show_notification(self, title, message):
        # 桌面端实现
        pass
```

前端调用：

```javascript
await bridge.sys_show_notification("提示", "操作成功");
```

## 注意事项

- 桌面模式下，文件路径使用本地文件系统
- Web 模式下，文件通过 Base64 编码传输
- 方法名不要以 `_` 开头（会被过滤）
- 确保 Python 方法返回 JSON 可序列化的数据

## 许可证

MIT

## 贡献

欢迎提交 Issue 和 Pull Request！
