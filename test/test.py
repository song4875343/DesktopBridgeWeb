# my_business.py
import sys
from pathlib import Path
# 将父目录添加到路径，以便导入项目模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_generator import create_api_from_instance

class MathService:
    def add(self, a: int, b: int = 10):
        return {"result": a + b}
        
    def multiply(self, a: float, b: float):
        return {"result": a * b}

class TextService:
    def to_upper(self, text: str):
        return {"result": text.upper()}
        
    def _secret_method(self):
        # 这个方法因为带了下划线，绝对不会被暴露成 API
        return "I am hidden"

# ================= Vercel / Uvicorn 运行入口 =================
# 一行代码，直接把纯粹的 Python 类变成强大的 Web API！

app = create_api_from_instance(MathService(), title="数学计算服务")
# app = create_api_from_instance(TextService(), title="文本处理服务")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)