# -*- coding: utf-8 -*-
"""
geo_tools 纯算法自测脚本（不联网、不依赖 MCP）。

运行：python test/test_geo_tools.py
"""
import os
import sys

# 确保能 import 同目录的 geo_tools（无论从哪个 cwd 运行）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from geo_tools import Location, haversine_km, cluster_locations, calc_distance, sort_locations


def test_distance():
    # 同经度、纬度差 0.008°，约 0.9 公里
    d = haversine_km(116.397, 39.916, 116.397, 39.908)
    print(f"[距离] 纬度差 0.008° ≈ {d:.3f} km")
    assert 0.5 < d < 1.5, f"距离异常: {d}"

    r = calc_distance(
        Location(name="故宫", longitude=116.397, latitude=39.916),
        Location(name="天安门", longitude=116.397, latitude=39.908),
    )
    print(f"[calc_distance] {r}")
    assert r["location1"] == "故宫" and r["distance_km"] > 0
    print("[calc_distance] 通过 [OK]\n")


def test_cluster_transitive():
    # A-B 约 3.4km，B-C 约 3.4km，A-C 约 6.8km（>5km）：传递闭包应让 A/B/C 同组
    a = Location(name="A", longitude=116.30, latitude=39.95)
    b = Location(name="B", longitude=116.34, latitude=39.95)
    c = Location(name="C", longitude=116.38, latitude=39.95)
    far = Location(name="FAR", longitude=120.00, latitude=30.00)  # 远点，单独成组

    r = cluster_locations([a, b, c, far], threshold_km=5.0)
    print(f"[聚类] 分组数={len(r['groups'])}，明细：{r}")
    assert len(r["groups"]) == 2, f"应分为 2 组: {r}"
    big = [g for g in r["groups"] if g["count"] == 3]
    assert len(big) == 1, f"应有一个 3 点群（传递闭包）: {r}"
    print("[cluster_locations] 传递闭包通过 [OK]\n")


def test_sort():
    south = Location(name="南", longitude=116.40, latitude=39.90)
    mid = Location(name="中", longitude=116.40, latitude=39.95)
    north = Location(name="北", longitude=116.40, latitude=40.00)

    # direction=1 由北向南（纬度降序）：北 → 中 → 南
    r1 = sort_locations([mid, south, north], direction=1)
    names1 = [o["name"] for o in r1["ordered"]]
    print(f"[排序 dir=1 由北向南] {names1}，累计={[o['cumulative_km'] for o in r1['ordered']]}")
    assert names1 == ["北", "中", "南"], names1
    cams = [o["cumulative_km"] for o in r1["ordered"]]
    assert cams == sorted(cams), cams

    # direction=2 由南向北（纬度升序）：南 → 中 → 北
    r2 = sort_locations([mid, south, north], direction=2)
    names2 = [o["name"] for o in r2["ordered"]]
    print(f"[排序 dir=2 由南向北] {names2}")
    assert names2 == ["南", "中", "北"], names2

    print("[sort_locations] 方向排序通过 [OK]\n")


if __name__ == "__main__":
    print("=== geo_tools 自测 ===\n")
    test_distance()
    test_cluster_transitive()
    test_sort()
    print("=== 全部通过 ===")
