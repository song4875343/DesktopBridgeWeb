---
name: vibesync
description: Build dual-platform Python applications using VibeSync framework - seamlessly runs on desktop (pywebview) and web (browser) with a single codebase. Edit core.py for business logic, use bridge.js for frontend calls.
---

# VibeSync Framework Development Skill

## Overview

VibeSync is a dual-platform framework enabling Python applications to run on both desktop (pywebview) and web (browser) environments with a single codebase.

## Core Architecture

```
UI Layer (index.html)
    ↓
Bridge Layer (bridge.js) - Auto-detects environment
    ↓
Adapter Layer (main.py) - UniversalApi with auto-mount
    ↓
Business Logic (core.py) - Platform-agnostic methods
```

## Critical Rules

### DO NOT Modify Framework Files
- `bridge.js` - Frontend bridge (framework core)
- `main.py` - Desktop entry point (framework core)

### ALWAYS Edit Business Logic in core.py
All application logic goes into `core.py` as methods of `AppCore` class:

```python
class AppCore:
    def your_method(self, param1, param2):
        """
        - Method names without _ prefix are auto-exposed to frontend
        - Return JSON-serializable data only (dict, list, str, int, bool)
        - Use type hints for clarity
        """
        return {"result": param1 + param2}
```

### Frontend Calls via bridge

```javascript
import { bridge } from './bridge.js';

// Call backend (auto-adapts desktop/web)
const result = await bridge.your_method(10, 20);

// File I/O (unified interface)
const file = await bridge.openFile("image/*");
// Returns: {name: "file.jpg", content: "data:image/jpeg;base64,..."}

await bridge.saveFile("output.txt", dataURL);
```

## Development Workflow

### Step 1: Add Backend Method

```python
# core.py
class AppCore:
    def process_data(self, items: list) -> dict:
        processed = [item.upper() for item in items]
        return {"processed": processed, "count": len(processed)}
```

### Step 2: Call from Frontend

```javascript
// index.html
const result = await bridge.process_data(["hello", "world"]);
// {"processed": ["HELLO", "WORLD"], "count": 2}
```

### Step 3: Test

```bash
python main.py  # Desktop mode
```

## Common Patterns

### Pattern: File Processing

```python
# core.py
import base64

class AppCore:
    def analyze_file(self, file_data: dict) -> dict:
        # file_data: {name: str, content: str (Base64 data URL)}
        content = file_data['content']
        if ',' in content:
            content = content.split(',', 1)[1]
        
        data = base64.b64decode(content)
        
        return {
            "filename": file_data['name'],
            "size": len(data)
        }
```

```javascript
// frontend
const file = await bridge.openFile("text/*");
if (file) {
    const analysis = await bridge.analyze_file(file);
}
```

### Pattern: State Management

```python
# core.py
class AppCore:
    def __init__(self):
        self.state = {}
    
    def get_state(self) -> dict:
        return self.state
    
    def update_state(self, key: str, value) -> dict:
        self.state[key] = value
        return self.state
```

## Extending System APIs

Add `sys_` prefixed methods to `UniversalApi` in `main.py`:

```python
class UniversalApi:
    def sys_get_clipboard(self):
        """Desktop-specific system API"""
        import pyperclip
        return {"text": pyperclip.paste()}
```

Frontend usage:
```javascript
const clip = await bridge.sys_get_clipboard();
```

## Project Scaffolding

When creating new VibeSync app:

1. Copy `bridge.js` and `main.py` (framework core)
2. Create `core.py` with `AppCore` class
3. Create `index.html` importing bridge
4. Add dependencies: `pywebview` in `pyproject.toml`
5. Test: `python main.py`

## Quick Start Templates

### Minimal core.py
```python
class AppCore:
    def hello(self, name: str = "World") -> str:
        return f"Hello, {name}!"
```

### Minimal index.html
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

## Debugging

### Desktop Mode
- Set `webview.start(debug=True)` in `main.py` for DevTools
- Use `console.log()` in frontend
- Use `print()` in Python backend

### Common Issues

1. **Method not found**: Ensure method name doesn't start with `_`
2. **JSON errors**: Return only JSON-serializable types
3. **MIME errors**: Already fixed in `main.py` with `mimetypes.add_type()`

## Best Practices

1. Keep `core.py` platform-agnostic - no direct file system access
2. Return structured data with clear keys
3. Handle errors gracefully - return `{"error": "message"}`
4. Use type hints for clarity
5. Test both desktop and web modes

## AI Assistant Guidelines

When helping with VibeSync:

1. Check if `bridge.js` and `main.py` exist before suggesting modifications
2. Default to editing `core.py` for business logic
3. Use `bridge.*` calls in frontend, never direct `window.pywebview`
4. Suggest minimal changes
5. Remind about dual-platform compatibility
6. New methods in `AppCore` are automatically available in frontend

## Example: Complete Feature

User request: "Add word counter for text files"

### Backend (core.py)
```python
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

### Frontend (index.html)
```html
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

## Dependencies

- Python >= 3.8
- pywebview >= 4.0

Install with:
```bash
pip install pywebview
```

## Resources

- Framework files: `bridge.js`, `main.py`
- Business logic: `core.py`
- UI: `index.html`
