# -*- coding: utf-8 -*-
"""
ModelScope 创空间入口（默认启动文件 app.py）。

创空间会执行 `python app.py`，并把容器内 0.0.0.0:7860 反向代理为公网域名，
因此 MCP SSE 端点对外即：https://<创空间域名>/sse

本地也可直接运行：python app.py  （等价于监听 0.0.0.0:7860，与线上环境一致）
"""
import os

import uvicorn

from geo_mcp_server import build_app

# 创空间约定：host 必须 0.0.0.0，端口 7860（由创空间注入 PORT 环境变量）
HOST = os.getenv("GEO_MCP_HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "7860"))

# FastMCP SSE ASGI app（已按 MCP_TOKEN 决定是否加鉴权）
app = build_app()
if app is None:
    raise RuntimeError("当前 mcp SDK 未暴露 sse_app/http_app，无法以 ASGI 方式启动")


if __name__ == "__main__":
    print(f"[MCP] 创空间入口启动：http://{HOST}:{PORT}/sse")
    uvicorn.run(app, host=HOST, port=PORT)
