# -*- coding: utf-8 -*-
"""
地理计算纯算法模块（仅依赖 math + pydantic，无网络/MCP 依赖）。

被 geo_mcp_server.py 包装为 MCP 工具对外暴露，也可被 test_geo_tools.py 直接测试。
"""
import math

from pydantic import BaseModel


class Location(BaseModel):
    """地点对象"""
    name: str
    longitude: float  # 经度（东西）
    latitude: float   # 纬度（南北）


# 方向标识 → 中文描述
DIRECTION_DESC = {
    1: "由北向南",
    2: "由南向北",
    3: "由东向西",
    4: "由西向东",
}


def haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """用 Haversine 公式计算两个经纬度坐标之间的球面直线距离（公里）。"""
    R = 6371.0  # 地球平均半径（公里）
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlam / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def cluster_locations(locations: list[Location], threshold_km: float = 5.0) -> dict:
    """
    地理聚类分组：对任意两两直线距离 <= threshold_km 的地点求传递闭包
    （单链接连通分量），归入同一个景点群。
    即 A-B<=阈值 且 B-C<=阈值 时，即便 A-C>阈值，三者也归同一群。
    """
    n = len(locations)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]  # 路径压缩
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    # 两两计算距离，<= 阈值则连通
    for i in range(n):
        for j in range(i + 1, n):
            d = haversine_km(
                locations[i].longitude, locations[i].latitude,
                locations[j].longitude, locations[j].latitude,
            )
            if d <= threshold_km:
                union(i, j)

    # 按 root 聚合
    groups_map = {}
    for i in range(n):
        groups_map.setdefault(find(i), []).append(i)

    groups = []
    for gid, idxs in enumerate(sorted(groups_map.values(), key=lambda g: g[0]), start=1):
        center_lon = sum(locations[i].longitude for i in idxs) / len(idxs)
        center_lat = sum(locations[i].latitude for i in idxs) / len(idxs)
        groups.append({
            "group_id": gid,
            "count": len(idxs),
            "center": {"longitude": round(center_lon, 6), "latitude": round(center_lat, 6)},
            "locations": [locations[i].model_dump() for i in idxs],
        })

    return {"threshold_km": threshold_km, "total": n, "groups": groups}


def calc_distance(location1: Location, location2: Location) -> dict:
    """计算两个地点之间的直线距离（公里，Haversine）。"""
    d = haversine_km(
        location1.longitude, location1.latitude,
        location2.longitude, location2.latitude,
    )
    return {
        "distance_km": round(d, 4),
        "location1": location1.name,
        "location2": location2.name,
    }


def sort_locations(locations: list[Location], direction: int) -> dict:
    """
    按方向对多个地点线性排序，并计算相邻两地的间隔距离与累计距离。
    direction: 1=由北向南(纬度降序) 2=由南向北(纬度升序)
               3=由东向西(经度降序) 4=由西向东(经度升序)
    """
    if direction not in DIRECTION_DESC:
        raise ValueError(f"不支持的 direction: {direction}，仅支持 1/2/3/4")

    use_lat = direction in (1, 2)        # 南北方向按纬度排序
    reverse = direction in (1, 3)        # 1 北→南、3 东→西 为降序
    key_func = (lambda l: l.latitude) if use_lat else (lambda l: l.longitude)
    ordered = sorted(locations, key=key_func, reverse=reverse)

    result = []
    cumulative = 0.0
    prev = None
    for idx, loc in enumerate(ordered, start=1):
        if prev is None:
            seg = 0.0
        else:
            seg = haversine_km(prev.longitude, prev.latitude, loc.longitude, loc.latitude)
            cumulative += seg
        result.append({
            "order": idx,
            "name": loc.name,
            "longitude": loc.longitude,
            "latitude": loc.latitude,
            "segment_km": round(seg, 4),
            "cumulative_km": round(cumulative, 4),
        })
        prev = loc

    return {
        "direction": direction,
        "direction_desc": DIRECTION_DESC[direction],
        "ordered": result,
        "total_km": round(cumulative, 4),
    }
