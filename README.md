# mcp_dl

基于 MCP（SSE 协议）的地理工具服务。

将三个地理计算能力暴露为 MCP 工具，供阿里百炼等支持 MCP 的平台按需调用。

## 功能

- **地点聚类分组**：对多个地点按直线距离阈值做传递闭包聚类（单链接连通分量）。
- **两地直线距离**：基于经纬度用 Haversine 公式计算球面距离（公里）。
- **多地方向排序**：按 北→南 / 南→北 / 东→西 / 西→东 线性排序，并给出相邻间隔距离与累计距离。

## 文件说明

| 文件 | 作用 |
|------|------|
| `geo_tools.py` | 纯算法模块（仅依赖 `math` + `pydantic`，无网络/MCP 依赖） |
| `geo_mcp_server.py` | MCP 地理工具服务（SSE），把算法包装为 MCP 工具 |
| `config.py` | 配置，所有配置项支持同名环境变量覆盖 |
| `requirements.txt` | 依赖清单 |

## 运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动 MCP 地理工具服务（默认 0.0.0.0:9876，SSE 端点 /sse）
python geo_mcp_server.py
```

注册到百炼等平台时，`MCP_SERVER_URL` 需改为公网可达地址，例如 `http://<公网IP>:9876/sse`。

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MCP_SERVER_LABEL` | MCP 服务标识 | `geo-mcp-service` |
| `MCP_SERVER_DESC` | MCP 服务描述 | 地理工具：聚类分组、距离计算、方向排序 |
| `MCP_SERVER_URL` | 对外暴露的 SSE 端点（注册到平台时填） | `http://localhost:9876/sse` |
| `MCP_TOKEN` | MCP 鉴权 token，两端需一致；留空则不校验 | 空 |
| `GEO_MCP_HOST` / `GEO_MCP_PORT` | 服务监听地址 / 端口 | `0.0.0.0` / `9876` |

> 敏感信息请通过环境变量注入，不要硬编码。
