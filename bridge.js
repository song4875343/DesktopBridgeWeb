// bridge.js (修复版)

// === 1. 核心代理 (Magic Proxy) ===
const handler = {
    get: function(target, prop) {
        // 如果调用的是通用 I/O 方法 (如 openFile)，直接返回 target 里的实现
        if (prop in target) return target[prop];

        return async function(...args) {
            console.log(`[Bridge] 调用: ${prop}`, args);

            // 🔥 关键修改：每次调用函数时，才去检查 window.pywebview 是否存在
            // 这样避免了 js 加载太快，pywebview 还没注入导致的误判
            if (window.pywebview) {
                // === Desktop 模式 ===
                return await window.pywebview.api[prop](...args);
            } else {
                // === Web 模式 ===
                // 约定：把参数打包成数组发给后端
                const response = await fetch(`/api/${prop}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(args) 
                });
                
                // 处理 JSON 解析错误（比如后端报错返回了 HTML）
                const text = await response.text();
                try {
                    const res = JSON.parse(text);
                    if (res.error) throw new Error(res.error);
                    return res;
                } catch (e) {
                    console.error("后端返回了非 JSON 数据:", text);
                    throw new Error(`API Error: ${response.status} ${response.statusText}`);
                }
            }
        };
    }
};

// === 2. 通用文件 I/O (I/O Shim) ===
const ioShim = {
    // 统一返回: Promise<{ name: string, content: string(Base64) }>
    async openFile(accept = "*/*") {
        // 🔥 同样改为运行时检测
        if (window.pywebview) {
            return await window.pywebview.api.sys_open_file();
        } else {
            return new Promise((resolve) => {
                const input = document.createElement('input');
                input.type = 'file';
                input.accept = accept;
                input.onchange = (e) => {
                    const file = e.target.files[0];
                    if (!file) return resolve(null);
                    const reader = new FileReader();
                    reader.readAsDataURL(file); 
                    reader.onload = () => resolve({ 
                        name: file.name, 
                        content: reader.result 
                    });
                };
                input.click();
            });
        }
    },

    async saveFile(filename, content) {
        // 🔥 同样改为运行时检测
        if (window.pywebview) {
            return await window.pywebview.api.sys_save_file(filename, content);
        } else {
            const a = document.createElement('a');
            a.href = content; 
            a.download = filename;
            a.click();
            return { status: "success", mode: "web-download" };
        }
    }
};

export const bridge = new Proxy(ioShim, handler);