# core.py
class AppCore:
    def greet(self, name):
        """简单的字符串处理"""
        return f"你好, {name}! 欢迎来到 Vibe Coding 世界。"

    def analyze_file(self, file_data):
        """
        处理文件逻辑
        file_data: { name: str, content: str(Base64) }
        """
        # 模拟：返回文件大小和类型信息
        header = file_data['content'][:30] + "..."
        size = len(file_data['content'])
        return {
            "filename": file_data['name'],
            "size_bytes": size,
            "preview": header,
            "message": "Python 成功读取并分析了你的文件！"
        }