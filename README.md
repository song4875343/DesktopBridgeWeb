# DesktopBridgeWeb

一个优雅的 pywebview + fastapi 双端开发框架，让你的应用同时运行在桌面和 Web 平台。
一个将任意 Python 类快速转换为 FastAPI 服务的函数。


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
├── bridge.js         # 前端桥接层（自动适配环境）
├── main.py           # 启动入口（桌面模式）
├── core.py           # 业务逻辑（你的代码）
├── index.html        # UI 界面（你的代码）
├── api_generator.py  # API 自动生成器
├── run_test.py       # 测试服务启动脚本
└── test/
    └── test.py       # API 生成器测试示例
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

### API 生成器测试

项目提供了 `api_generator.py`，可以 ：

```python
# test/test.py
from api_generator import create_api_from_instance

class MathService:
    def add(self, a: int, b: int = 10):
        return {"result": a + b}

    def multiply(self, a: float, b: float):
        return {"result": a * b}

# 一行代码将类转换为 FastAPI 应用
app = create_api_from_instance(MathService(), title="数学计算服务")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

**运行测试服务：**

```bash
# 方法一：使用包装脚本
uv run python test/test.py
```

服务启动后访问：
- API 文档：http://127.0.0.1:8000/docs
- 接口示例：
  - POST/GET http://127.0.0.1:8000/add?a=1&b=2
  - POST/GET http://127.0.0.1:8000/multiply?a=2.5&b=4

**特性：**
- 自动挂载类中所有非 `_` 开头的方法为 API 接口
- 同时支持 GET 和 POST 请求
- 自动生成 OpenAPI 文档

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

## AI 助手集成

DesktopBridgeWeb 提供了完整的 AI 编程助手集成支持，让 AI 能够理解框架规范并高效开发。

### 支持的 AI 工具

| AI 工具 | 配置文件 | 状态 |
|---------|---------|------|
| Kiro / Windsurf | `.kiro/steering/desktopbridgeweb-framework.md` | ✅ 自动加载 |
| Claude Code | `.claude/skills/desktopbridgeweb/SKILL.md` | ✅ 按需加载 |
| OpenCode | `.opencode/skills/desktopbridgeweb/SKILL.md` | ✅ 自动发现 |

### Kiro / Windsurf 集成

Kiro 会自动加载 steering 规则，无需手动配置：

```
.kiro/steering/desktopbridgeweb-framework.md
```

特性：
- 自动理解框架架构和开发规范
- 只编辑 `core.py` 添加业务逻辑
- 使用 `bridge.*` 调用后端方法
- 遵循双平台开发最佳实践

### Claude Code 集成

Claude Code 会自动发现项目中的 skill：

```
.claude/skills/desktopbridgeweb/SKILL.md
```

使用方式：
- 在对话中提及 "desktopbridgeweb" 或 "dual-platform"
- Claude 会自动加载 skill 并理解框架规范
- 或手动加载：在 Claude Code 中使用 skill 工具

### OpenCode 集成

OpenCode 自动扫描并加载项目 skill：

```
.opencode/skills/desktopbridgeweb/SKILL.md
```

特性：
- 项目级自动发现
- 支持全局 skill（`~/.config/opencode/skills/`）
- 按需加载，不占用初始上下文

### 使用示例

所有 AI 助手集成后，开发变得极其简单：

```
你: "添加一个计算器功能"
AI: ✅ 在 core.py 添加 calculate() 方法
    ✅ 返回 JSON 格式数据
    ✅ 前端使用 bridge.calculate() 调用

你: "添加文件上传功能"  
AI: ✅ 使用 bridge.openFile() 模式
    ✅ 处理 Base64 编码
    ✅ 在 core.py 添加文件处理方法

你: "添加状态管理"
AI: ✅ 在 AppCore.__init__() 初始化状态
    ✅ 添加 get_state() 和 update_state() 方法
    ✅ 遵循 JSON 序列化规范
```

### 优势

- 🎯 **零学习成本**：AI 已理解所有框架规范
- 🚀 **开发提速**：无需重复解释架构
- ✅ **规范一致**：AI 自动遵循最佳实践
- 🔧 **智能建议**：AI 知道何时编辑哪个文件

### 手动安装 Skills（可选）

如果需要在其他项目中使用，可以复制 skill 文件：

```bash
# Claude Code
cp -r .claude/skills/desktopbridgeweb ~/.claude/skills/

# OpenCode  
cp -r .opencode/skills/desktopbridgeweb ~/.config/opencode/skills/

# Kiro (项目级，不建议全局)
# steering 规则通常保持在项目内
```

## 许可证

MIT

## 贡献

欢迎提交 Issue 和 Pull Request！
