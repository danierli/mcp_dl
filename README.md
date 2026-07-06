# mcp_dl

基于阿里百炼 Responses API + MCP 的地理工具服务 demo。

## 功能

三个地理计算能力，通过 MCP（SSE 协议）暴露，供百炼平台大模型按需调用：

- **地点聚类分组**：对多个地点按直线距离阈值做传递闭包聚类（单链接连通分量）。
- **两地直线距离**：基于经纬度用 Haversine 公式计算球面距离（公里）。
- **多地方向排序**：按 北→南 / 南→北 / 东→西 / 西→东 线性排序，并给出相邻间隔距离与累计距离。

另含一个 `/chat` 流式接口：调用百炼 Responses API，并把上述 MCP 工具透传给模型（SSE 增量返回）。

## 文件说明

| 文件 | 作用 |
|------|------|
| `geo_tools.py` | 纯算法模块（仅依赖 `math` + `pydantic`，无网络/MCP 依赖） |
| `geo_mcp_server.py` | MCP 地理工具服务（SSE），把算法包装为 MCP 工具 |
| `chat_api.py` | `/chat` 流式对话接口（百炼 Responses + MCP 透传） |
| `config.py` | 自包含配置，所有配置项支持同名环境变量覆盖 |
| `test_geo_tools.py` | 纯算法自测脚本（不联网） |
| `requirements.txt` | 依赖清单 |

## 运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动 MCP 地理工具服务（默认 0.0.0.0:9876，SSE 端点 /sse）
python geo_mcp_server.py

# 启动 /chat 流式接口（默认 0.0.0.0:9000）
python chat_api.py

# 运行算法自测（不联网、不依赖 MCP）
python test_geo_tools.py
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `BAILIAN_API_KEY`（或 `DASHSCOPE_API_KEY`） | 百炼平台 API Key，**必填** | 空 |
| `BAILIAN_URL` | 百炼 OpenAI 兼容入口 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `BAILIAN_MODEL` | 模型名 | `qwen3.6-plus` |
| `MCP_SERVER_URL` | MCP 服务 SSE 端点（注册到百炼需改为公网可达地址） | `http://localhost:9876/sse` |
| `MCP_TOKEN` | MCP 鉴权 token，两端需一致；留空则不校验 | 空 |
| `GEO_MCP_PORT` / `CHAT_PORT` | 服务监听端口 | `9876` / `9000` |

> 敏感信息请通过环境变量注入，不要硬编码。
