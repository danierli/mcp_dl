# -*- coding: utf-8 -*-
"""
流式对话接口 /chat：调用阿里百炼 Responses API，并将 MCP 地理工具透传给模型。

模型（百炼）在需要时自行拉取注册的 MCP 服务执行工具，本服务只负责
把模型最终回复的流式增量文本透传给前端（SSE）。

启动：python chat_api.py
默认监听 0.0.0.0:9000。

请求体示例（多轮）：
{
  "messages": [
    {"role": "system", "content": "你是一个地理助手"},
    {"role": "user", "content": "帮我算一下北京和上海的直线距离"}
  ],
  "use_mcp": true
}
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import AsyncOpenAI
from sse_starlette.sse import EventSourceResponse

from config import (
    BAILIAN_URL, BAILIAN_API_KEY, BAILIAN_MODEL,
    MCP_SERVER_LABEL, MCP_SERVER_DESC, MCP_SERVER_URL, MCP_TOKEN,
    CHAT_HOST, CHAT_PORT,
)

app = FastAPI(title="Chat API（百炼 Responses + MCP）")

# AsyncOpenAI：避免在 async handler 中阻塞事件循环
# 无 key 时用占位符，避免 SDK 在模块加载阶段抛错；真实校验在 /chat handler 内（空 key 返回 401）
client = AsyncOpenAI(api_key=BAILIAN_API_KEY or "EMPTY", base_url=BAILIAN_URL)


def _build_mcp_tool() -> dict:
    """构造透传给百炼的 MCP 工具配置（即百炼文档中的 mcp_tool）。"""
    tool = {
        "type": "mcp",
        "server_protocol": "sse",
        "server_label": MCP_SERVER_LABEL,
        "server_description": MCP_SERVER_DESC,
        "server_url": MCP_SERVER_URL,
    }
    if MCP_TOKEN:
        tool["headers"] = {"Authorization": f"Bearer {MCP_TOKEN}"}
    return tool


class ChatMessage(BaseModel):
    role: str       # system / user / assistant
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    use_mcp: bool = True   # 是否把 MCP 工具传给百炼


@app.post("/chat")
async def chat(req: ChatRequest):
    if not BAILIAN_API_KEY:
        return JSONResponse(
            {"code": 401, "message": "未配置 BAILIAN_API_KEY（或 DASHSCOPE_API_KEY）"},
            status_code=400,
        )
    if not req.messages:
        return JSONResponse({"code": 401, "message": "messages 不能为空"}, status_code=400)

    tools = [_build_mcp_tool()] if req.use_mcp else None

    async def event_stream():
        try:
            stream = await client.responses.create(
                model=BAILIAN_MODEL,
                input=[m.model_dump() for m in req.messages],
                tools=tools,
                stream=True,
            )
            async for event in stream:
                etype = getattr(event, "type", "")
                # 模型最终回复的增量文本
                if etype == "response.output_text.delta":
                    delta = getattr(event, "delta", "")
                    if delta:
                        yield {"event": "delta", "data": delta}
                # 流结束
                elif etype == "response.completed":
                    yield {"event": "done", "data": "[DONE]"}
                    break
        except Exception as e:
            yield {"event": "error", "data": f"[ERROR] {e}"}

    return EventSourceResponse(event_stream())


if __name__ == "__main__":
    import uvicorn
    print(f"启动 /chat 服务：http://{CHAT_HOST}:{CHAT_PORT}/chat")
    print(f"百炼模型：{BAILIAN_MODEL} | base_url：{BAILIAN_URL}")
    print(f"MCP 透传：{MCP_SERVER_URL}")
    uvicorn.run(app, host=CHAT_HOST, port=CHAT_PORT)
