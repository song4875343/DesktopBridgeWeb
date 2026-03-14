import inspect
from fastapi import FastAPI

def create_api_from_instance(instance, title="Auto API", version="1.0.0"):
    """
    终极黑魔法：将任意 Python 类的实例，一键转化为 FastAPI 服务！
    """
    app = FastAPI(title=title, version=version)
    
    # 遍历实例的所有绑定方法
    for name, func in inspect.getmembers(instance, predicate=inspect.ismethod):
        # 核心过滤：过滤掉私有方法（_开头）和内置方法（__开头）
        if name.startswith('_'):
            continue
            
        # 自动挂载路由
        app.add_api_route(
            path=f"/{name}",
            endpoint=func,
            methods=["GET", "POST"], # 默认支持 GET 和 POST，方便调用
            name=name
        )
        print(f"✅ 成功将方法 [{name}] 挂载为 API 接口: /{name}")
        
    return app