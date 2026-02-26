---
title: VibeSync Framework Development Guide
description: Guidelines for developing dual-platform applications using VibeSync framework
tags: [vibesync, pywebview, dual-platform, framework]
---

# VibeSync Framework Development Guide

## Framework Overview

VibeSync is a dual-platform framework that enables Python applications to run seamlessly on both desktop (pywebview) and web (browser) environments with a single codebase.

### Core Architecture

```
┌─────────────────────────────────────────┐
│         index.html (UI Layer)           │
│  ┌───────────────────────────────────┐  │
│  │      bridge.js (Magic Proxy)      │  │
│  │  - Auto-detect environment        │  │
│  │  - Route API calls                │  │
│  │  - Unified I/O interface          │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────┐
│      main.py (Entry & Adapter)          │
│  ┌───────────────────────────────────┐  │
│  │    UniversalApi (Auto-mount)      │  │
│  │  - sys_* methods (I/O)            │  │
│  │  - Dynamic method binding         │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────┐
│      core.py (Business Logic)           │
│  - Pure Python methods                  │
│  - No platform awareness needed         │
└─────────────────────────────────────────┘
```

## Development Rules

### 1. DO NOT Modify Framework Files

The following files are framework core and should NOT be modified:
- `bridge.js` - Frontend bridge layer
- `main.py` - Desktop entry point (unless extending framework)

### 2. Business Logic in `core.py`

All business logic goes into `core.py` as methods of the `AppCore` class:

```python
# core.py
class AppCore:
    def __init__(self):
        self.data = {}
    
    def your_method(self, param1, param2):
        """
        - Method names without leading underscore are auto-exposed
        - Return JSON-serializable data (dict, list, str, int, etc.)
        - Use type hints for clarity
        """
        return {"result": param1 + param2}
    
    def _private_method(self):
        """Methods starting with _ are NOT exposed to frontend"""
        pass
```

### 3. Frontend Calls via `bridge`

In `index.html` or separate JS modules:

```javascript
import { bridge } from './bridge.js';

// Call backend methods (auto-adapts to desktop/web)
const result = await bridge.your_method(10, 20);
console.log(result); // {"result": 30}

// File I/O (unified interface)
const file = await bridge.openFile("image/*");
if (file) {
    // file.name: filename
    // file.content: Base64 data URL
    document.getElementById('preview').src = file.content;
}

await bridge.saveFile("output.txt", dataURL);
```

## Common Development Patterns

### Pattern 1: Data Processing

```python
# core.py
class AppCore:
    def process_data(self, items: list) -> dict:
        processed = [item.upper() for item in items]
        return {"processed": processed, "count": len(processed)}
```

```javascript
// frontend
const result = await bridge.process_data(["hello", "world"]);
// {"processed": ["HELLO", "WORLD"], "count": 2}
```

### Pattern 2: File Processing

```python
# core.py
import base64
import json

class AppCore:
    def analyze_file(self, file_data: dict) -> dict:
        """
        file_data: {name: str, content: str (Base64 data URL)}
        """
        # Remove data URL prefix if present
        content = file_data['content']
        if ',' in content:
            content = content.split(',', 1)[1]
        
        # Decode and process
        data = base64.b64decode(content)
        
        return {
            "filename": file_data['name'],
            "size": len(data),
            "preview": data[:100].decode('utf-8', errors='ignore')
        }
```

```javascript
// frontend
const file = await bridge.openFile();
if (file) {
    const analysis = await bridge.analyze_file(file);
    console.log(analysis);
}
```

### Pattern 3: State Management

```python
# core.py
class AppCore:
    def __init__(self):
        self.state = {"counter": 0}
    
    def get_state(self) -> dict:
        return self.state
    
    def update_state(self, key: str, value) -> dict:
        self.state[key] = value
        return self.state
```

```javascript
// frontend
await bridge.update_state("counter", 42);
const state = await bridge.get_state();
```

## Adding New Features

### Extending System-Level APIs

Add `sys_` prefixed methods to `UniversalApi` in `main.py`:

```python
class UniversalApi:
    # Existing methods...
    
    def sys_get_clipboard(self):
        """Desktop-specific system API"""
        import pyperclip
        return {"text": pyperclip.paste()}
    
    def sys_show_notification(self, title: str, message: str):
        """Cross-platform notification"""
        if hasattr(webview, 'windows'):
            # Desktop implementation
            pass
        return {"status": "shown"}
```

Frontend usage:
```javascript
const clip = await bridge.sys_get_clipboard();
await bridge.sys_show_notification("Alert", "Task completed!");
```

## Project Scaffolding Checklist

When creating a new VibeSync app:

1. ✅ Copy `bridge.js` and `main.py` (framework core)
2. ✅ Create `core.py` with `AppCore` class
3. ✅ Create `index.html` with `<script type="module">` importing bridge
4. ✅ Add dependencies to `pyproject.toml` or `requirements.txt`:
   ```toml
   [project]
   dependencies = ["pywebview"]
   ```
5. ✅ Test desktop mode: `python main.py`
6. ✅ (Optional) Implement web server for web mode

## Quick Start Template

### Minimal `core.py`
```python
class AppCore:
    def hello(self, name: str = "World") -> str:
        return f"Hello, {name}!"
```

### Minimal `index.html`
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>VibeSync App</title>
</head>
<body>
    <h1>VibeSync App</h1>
    <button id="btn">Click Me</button>
    <div id="output"></div>

    <script type="module">
    import { bridge } from './bridge.js';
    
    document.getElementById('btn').onclick = async () => {
        const result = await bridge.hello("VibeSync");
        document.getElementById('output').textContent = result;
    };
    </script>
</body>
</html>
```

## Debugging Tips

### Desktop Mode
- Set `webview.start(debug=True)` in `main.py` to enable DevTools
- Use `console.log()` in frontend
- Use `print()` in Python backend

### Common Issues

1. **"pywebview is not defined" in browser**
   - Expected behavior in web mode
   - Bridge automatically falls back to fetch API

2. **MIME type errors on Windows**
   - Already fixed in `main.py` with `mimetypes.add_type()`

3. **Method not found**
   - Ensure method name doesn't start with `_`
   - Check method is defined in `AppCore` class
   - Verify `inspect.getmembers()` can detect it

4. **JSON serialization errors**
   - Return only JSON-serializable types
   - Avoid returning class instances or complex objects

## Best Practices

1. **Keep `core.py` platform-agnostic** - No direct file system access, use bridge I/O
2. **Return structured data** - Use dicts with clear keys
3. **Handle errors gracefully** - Return `{"error": "message"}` on failures
4. **Use type hints** - Improves code clarity and IDE support
5. **Test both modes** - Desktop and web may behave differently with I/O

## AI Assistant Instructions

When helping users develop with VibeSync:

1. **Always check** if `bridge.js` and `main.py` exist before suggesting modifications
2. **Default to editing** `core.py` for business logic
3. **Use `bridge.*` calls** in frontend code, never direct `window.pywebview`
4. **Suggest minimal changes** - Framework is designed to be simple
5. **Remind about dual-platform** - Code should work in both desktop and web modes
6. **Auto-mount awareness** - New methods in `AppCore` are automatically available in frontend

## Example: Complete Feature Implementation

User request: "Add a feature to count words in uploaded text files"

### Step 1: Add backend method
```python
# core.py
class AppCore:
    def count_words(self, file_data: dict) -> dict:
        import base64
        content = file_data['content']
        if ',' in content:
            content = content.split(',', 1)[1]
        
        text = base64.b64decode(content).decode('utf-8')
        words = len(text.split())
        
        return {
            "filename": file_data['name'],
            "word_count": words,
            "char_count": len(text)
        }
```

### Step 2: Add frontend UI
```html
<!-- In index.html -->
<button id="upload">Upload Text File</button>
<div id="result"></div>

<script type="module">
import { bridge } from './bridge.js';

document.getElementById('upload').onclick = async () => {
    const file = await bridge.openFile("text/*");
    if (file) {
        const stats = await bridge.count_words(file);
        document.getElementById('result').innerHTML = `
            <p>File: ${stats.filename}</p>
            <p>Words: ${stats.word_count}</p>
            <p>Characters: ${stats.char_count}</p>
        `;
    }
};
</script>
```

Done! No framework modifications needed.
