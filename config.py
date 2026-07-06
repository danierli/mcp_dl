# -*- coding: utf-8 -*-
"""
test 目录自包含配置（与 beijing-data 主项目零耦合）。

所有配置项均支持同名环境变量覆盖；敏感信息（百炼 API Key、MCP 鉴权 token）
请通过环境变量注入，不要硬编码到本文件。
"""
import os

# ============ 百炼 Responses API（/chat 调用）============
# 百炼 OpenAI 兼容入口；responses 端点为 {BAILIAN_URL}/responses
BAILIAN_URL = os.getenv("BAILIAN_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
# 必填：百炼平台 API Key（DashScope），通过环境变量 BAILIAN_API_KEY 注入
# 必填：百炼平台 API Key，兼容官方 DASHSCOPE_API_KEY 环境变量
BAILIAN_API_KEY = os.getenv("BAILIAN_API_KEY") or os.getenv("DASHSCOPE_API_KEY", "")
BAILIAN_MODEL = os.getenv("BAILIAN_MODEL", "qwen3.6-plus")

# ============ MCP 服务信息（/chat 透传给百炼）============
MCP_SERVER_LABEL = os.getenv("MCP_SERVER_LABEL", "geo-mcp-service")
MCP_SERVER_DESC = os.getenv(
    "MCP_SERVER_DESC",
    "地理工具：地点聚类分组、两地直线距离计算、多地方向排序",
)
# MCP 服务的 SSE 端点；本地开发为 localhost，注册到百炼时需改为公网可达地址
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:9876/sse")
# MCP 鉴权 token：两端（MCP 服务校验 / 百炼请求携带）需保持一致；留空则不校验
MCP_TOKEN = os.getenv("MCP_TOKEN", "")

# ============ 服务监听 ============
GEO_MCP_HOST = os.getenv("GEO_MCP_HOST", "0.0.0.0")
GEO_MCP_PORT = int(os.getenv("GEO_MCP_PORT", "9876"))
CHAT_HOST = os.getenv("CHAT_HOST", "0.0.0.0")
CHAT_PORT = int(os.getenv("CHAT_PORT", "9000"))
