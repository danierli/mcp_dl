# mcp_dl

基于 MCP（SSE 协议）的地理工具服务。

将三个地理计算能力暴露为 MCP 工具，供阿里百炼等支持 MCP 的平台按需调用。支持本地运行，也适配 ModelScope 创空间部署。

## 功能

- **地点聚类分组**：对多个地点按直线距离阈值做传递闭包聚类（单链接连通分量）。
- **两地直线距离**：基于经纬度用 Haversine 公式计算球面距离（公里）。
- **多地方向排序**：按 北→南 / 南→北 / 东→西 / 西→东 线性排序，并给出相邻间隔距离与累计距离。

## 文件说明

| 文件 | 作用 |
|------|------|
| `geo_tools.py` | 纯算法模块（仅依赖 `math` + `pydantic`，无网络/MCP 依赖） |
| `geo_mcp_server.py` | MCP 地理工具服务（SSE），把算法包装为 MCP 工具；`build_app()` 返回带鉴权的 ASGI app |
| `app.py` | **ModelScope 创空间默认入口**，复用 `build_app()` 用 uvicorn 监听 `0.0.0.0:7860` |
| `config.py` | 配置，所有配置项支持同名环境变量覆盖 |
| `requirements.txt` | 依赖清单 |

## 运行

### 本地启动

```bash
# 安装依赖
pip install -r requirements.txt

# 方式一：直接启动（默认 0.0.0.0:9876，SSE 端点 /sse）
python geo_mcp_server.py

# 方式二：用创空间入口启动（默认 0.0.0.0:7860，与线上环境一致）
python app.py
```

### ModelScope 创空间部署

1. 将本仓库作为创空间代码源（创空间默认执行 `app.py`，并自动 `pip install -r requirements.txt`）。
2. 创空间把容器内 `0.0.0.0:7860` 反向代理为公网域名，部署后 MCP SSE 端点对外即：

   ```
   https://<创空间域名>/sse
   ```

3. 若设置了 `MCP_TOKEN`，调用方请求需带 `Authorization: Bearer <MCP_TOKEN>`。

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MCP_SERVER_LABEL` | MCP 服务标识 | `geo-mcp-service` |
| `MCP_SERVER_DESC` | MCP 服务描述 | 地理工具：聚类分组、距离计算、方向排序 |
| `MCP_SERVER_URL` | 对外暴露的 SSE 端点（注册到平台时填） | `http://localhost:9876/sse` |
| `MCP_TOKEN` | MCP 鉴权 token，两端需一致；留空则不校验 | 空 |
| `GEO_MCP_HOST` / `GEO_MCP_PORT` | `geo_mcp_server.py` 直接启动时的监听地址 / 端口 | `0.0.0.0` / `9876` |
| `PORT` | 创空间入口 `app.py` 的监听端口（创空间约定） | `7860` |

> 敏感信息请通过环境变量注入，不要硬编码。
