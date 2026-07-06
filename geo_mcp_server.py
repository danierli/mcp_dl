# -*- coding: utf-8 -*-
"""
MCP 地理工具服务（SSE 协议）。

将 geo_tools 中的三个地理计算能力暴露为 MCP 工具，供阿里百炼平台
通过 Responses API（tools=[{type:"mcp", ...}]）拉取调用。

启动：python geo_mcp_server.py
默认监听 0.0.0.0:9001，SSE 端点 /sse（百炼侧 server_url 填 http://<公网地址>:9001/sse）。
"""
from config import MCP_SERVER_LABEL, GEO_MCP_HOST, GEO_MCP_PORT, MCP_TOKEN

from geo_tools import (
    Location,
    cluster_locations as _cluster_locations,
    calc_distance as _calc_distance,
    sort_locations as _sort_locations,
)
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(MCP_SERVER_LABEL)


@mcp.tool()
def cluster_locations(locations: list[Location], threshold_km: float = 5.0) -> dict:
    """地理聚类分组：对传入的多个地点（含名称、经度、纬度）进行分组。
    两两直线距离在 threshold_km（默认5公里）以内的地点通过传递闭包归入同一个景点群
    （A-B<=阈值 且 B-C<=阈值 时，即便 A-C>阈值，三者也归同一群）。
    参数：
      locations: 地点对象列表，每个对象包含 name(名称)、longitude(经度)、latitude(纬度)
      threshold_km: 聚类距离阈值，单位公里，默认 5.0
    返回：JSON 对象，含 threshold_km、total、groups（每个 group 含 group_id、count、center、locations）。
    """
    return _cluster_locations(locations, threshold_km)


@mcp.tool()
def calc_distance(location1: Location, location2: Location) -> dict:
    """两地直线距离计算：传入两个地点对象，返回依据经纬度用 Haversine 公式计算的球面直线距离（公里）。
    参数：
      location1: 第一个地点，含 name、longitude、latitude
      location2: 第二个地点，含 name、longitude、latitude
    返回：JSON 对象，含 distance_km（公里）、location1、location2。
    """
    return _calc_distance(location1, location2)


@mcp.tool()
def sort_locations(locations: list[Location], direction: int) -> dict:
    """多地方向排序：传入多个地点对象与方向标识，按指定方向线性排序，并注明相邻两地的间隔距离与累计距离。
    direction 取值：1=由北向南、2=由南向北、3=由东向西、4=由西向东。
    参数：
      locations: 地点对象列表，每个含 name、longitude、latitude
      direction: 方向标识，1/2/3/4
    返回：JSON 对象，含 direction、direction_desc、ordered（每个地点含 order、name、longitude、latitude、segment_km、cumulative_km）、total_km。
    """
    return _sort_locations(locations, direction)


def _bearer_auth(app, token: str):
    """用 Bearer token 包装一个 ASGI app，未通过校验返回 401。"""
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import JSONResponse

    class _Auth(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            auth = request.headers.get("authorization", "")
            if auth != f"Bearer {token}":
                return JSONResponse({"error": "unauthorized"}, status_code=401)
            return await call_next(request)

    return _Auth(app)


def run():
    """启动 SSE 服务。优先用 sse_app + uvicorn（支持鉴权中间件），否则回退 mcp.run。"""
    import uvicorn

    # 不同版本 mcp SDK 暴露 ASGI app 的方法名不同，做兼容
    app_getter = getattr(mcp, "sse_app", None) or getattr(mcp, "http_app", None)
    if app_getter is not None:
        app = app_getter()
        if MCP_TOKEN:
            app = _bearer_auth(app, MCP_TOKEN)
            print(f"[MCP] 已启用 Bearer 鉴权（token 长度 {len(MCP_TOKEN)}）")
        else:
            print("[MCP] 未设置 MCP_TOKEN，跳过鉴权（仅供本地调试）")
        print(f"[MCP] SSE 服务启动：http://{GEO_MCP_HOST}:{GEO_MCP_PORT}/sse")
        uvicorn.run(app, host=GEO_MCP_HOST, port=GEO_MCP_PORT)
    else:
        # 回退：FastMCP 内置启动（不支持自定义鉴权中间件）
        mcp.settings.host = GEO_MCP_HOST
        mcp.settings.port = GEO_MCP_PORT
        print("[MCP] 回退到 mcp.run(transport='sse')，不支持鉴权中间件")
        mcp.run(transport="sse")


if __name__ == "__main__":
    run()
