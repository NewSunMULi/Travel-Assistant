# -*- coding: utf-8 -*-
"""
amap_fastapi_server.py
======================
高德地图服务 FastAPI Server —— 为 AI Agent（Dify / 大模型 / 任意 HTTP 客户端）
提供网络查询能力（由原 MCP Server 改造而来）。

基于 MapServices.py / weatherService.py 封装，对应
《昆明智能旅行决策 Agent》需求文档中的工具层：

    [节点4 Tool2]  /api/geocode             文字地址 → 经纬度
                   /api/route               两点路径规划（驾车/步行/骑车）
                   /api/route/multi         多途经点路线（一天多景点串联）
    [节点4 Tool3]  /api/taxi_cost           打车费估算（预算计算器）
    [节点4 Tool4]  /api/restaurants         餐厅推荐（餐厅 Agent）
    [阶段1 KB1]   /api/geocode/batch       批量地理编码（知识库位置字段）
                   /api/reverse_geocode     逆地理编码（坐标 → 地址）
                   /api/poi/polygon         多边形区域搜索（商圈/片区内 POI）
                   /api/poi/detail          POI ID 查询（详情补全）
    [Demo]         /api/travel_spots        旅游推荐
    其他           /api/weather             天气查询
                   /api/budget              预算分配计算器

启动方式：
    pip install fastapi "uvicorn[standard]"

    export AMAP_KEY=你的Web服务Key
    python amap_fastapi_server.py
    # 或： uvicorn amap_fastapi_server:app --host 0.0.0.0 --port 8000

接口文档（Swagger UI）：http://127.0.0.1:8000/docs
"""

import os
import sys

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

# 确保能 import 同目录的 serives 包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from serives.MapSerive import MapServices, AmapAPIError  # noqa: E402
from serives.weatherService import AmapWeather  # noqa: E402

# ───────────────────── 全局服务实例（惰性初始化） ─────────────────────
_SERVICE: MapServices | None = None
_WEATHER: AmapWeather | None = None


def get_service() -> MapServices:
    """惰性创建 MapServices 单例，避免无 Key 时 import 即报错。"""
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = MapServices()
    return _SERVICE


def get_weather() -> AmapWeather:
    """惰性创建 AmapWeather 单例，无 Key 时在调用时才报错。"""
    global _WEATHER
    if _WEATHER is None:
        key = os.environ.get("AMAP_KEY", "").strip()
        if not key:
            raise RuntimeError("环境变量 AMAP_KEY 未设置，请先执行: export AMAP_KEY=你的Web服务Key")
        _WEATHER = AmapWeather(key=key)
    return _WEATHER


# ───────────────────── FastAPI 应用 ─────────────────────

app = FastAPI(
    title="amap-kunming-travel-map",
    description="高德地图服务 —— 昆明智能旅行决策 Agent 工具层（FastAPI 版）",
    version="1.0.0",
)


# ───────────────────── 请求体模型 ─────────────────────

class BatchGeocodeRequest(BaseModel):
    addresses: list[str] = Field(..., description='地址列表，如 ["昆明市翠湖公园", "滇池海埂大坝"]')
    city: str | None = Field(None, description='统一限定城市（可选），如 "昆明"')


class MultiRouteRequest(BaseModel):
    origin: str = Field(..., description='出发点坐标，"经度,纬度"')
    destination: str = Field(..., description='终点坐标，"经度,纬度"')
    waypoints: list[str] = Field(..., description='途经点坐标列表（按游览顺序）')
    mode: str = Field("driving", description="driving(驾车) / walking(步行)；骑车不支持途经点")


# ═══════════════════════ 基础接口 ═══════════════════════

@app.get("/", summary="服务信息")
def root() -> dict:
    return {
        "service": "amap-kunming-travel-map",
        "docs": "/docs",
        "amap_key_configured": bool(os.environ.get("AMAP_KEY", "").strip()),
    }


@app.get("/api/health", summary="健康检查")
def health() -> dict:
    return {"status": "ok"}


# ═══════════════════════ [节点4 Tool2] 地理与路线工具 ═══════════════════════

@app.get("/api/geocode", summary="文字地址 → 经纬度")
def geocode_address(
    address: str = Query(..., description='结构化地址，如 "云南省昆明市五华区翠湖公园"'),
    city: str | None = Query(None, description='限定城市（可选），如 "昆明" 或 "530100"'),
) -> dict:
    """将文字地址解析为经纬度坐标。

    用于：景点/餐厅/酒店坐标定位、路径规划前的坐标准备、
          阶段1知识库"位置"字段填充。

    Returns:
        首个匹配结果的坐标与地址要素，含 location("经度,纬度")、
        province、city、district、adcode、level；无匹配时 location 为 None。
    """
    try:
        g = get_service().geocode(address, city=city)
        if not g:
            return {"found": False, "address": address, "location": None}
        return {"found": True, "address": address, **g[0]}
    except AmapAPIError as e:
        return {"found": False, "error": str(e)}


@app.post("/api/geocode/batch", summary="批量地理编码")
def batch_geocode_addresses(req: BatchGeocodeRequest) -> list:
    """批量将地址解析为坐标（阶段1 KB1 景区知识库位置字段批量填充）。

    Returns:
        与输入等长的列表，每项含 address、location("经度,纬度"或None)、detail。
    """
    return get_service().batch_geocode(req.addresses, city=req.city)


@app.get("/api/reverse_geocode", summary="逆地理编码（坐标 → 地址）")
def reverse_geocode(
    location: str = Query(..., description='坐标 "经度,纬度"，如 "102.712251,25.040609"'),
) -> dict:
    """将经纬度坐标解析为结构化地址（备用：当前位置解析、坐标可读化）。"""
    return get_service().regeo(location)


@app.get("/api/route", summary="两点路径规划")
def plan_route(
    origin: str = Query(..., description='出发点坐标，"经度,纬度"'),
    destination: str = Query(..., description='目的地坐标，"经度,纬度"'),
    mode: str = Query("driving", description="driving(驾车) / walking(步行) / bicycling(骑车)"),
) -> dict:
    """两点间路径规划，返回距离、耗时与分段指引。

    用于：景点间通勤时间估算（Verifier 时间冲突校验）、
          交通建议生成、体力强度评估（步行距离）。

    Returns:
        含 distance(米)、duration(秒)、distance_km、duration_min、
        taxi_cost(打车费，仅驾车)、steps(分路段文字指引)。
    """
    return get_service().route_planning(origin, destination, mode=mode)


@app.post("/api/route/multi", summary="多途经点路线规划")
def plan_route_multi(req: MultiRouteRequest) -> dict:
    """多途经点路线规划：把一天多个景点按顺序串联成一条线。

    用于：Demo 场景 "Day2 滇池→海埂大坝→西山" 串联、
          Verifier 校验全天总耗时/总里程是否超标、防止 AI 把路线排反。

    Returns:
        含总距离、总耗时、taxi_cost、legs(每段子路线)与 steps(分段指引)。
    """
    return get_service().route_multi(req.origin, req.destination, req.waypoints, mode=req.mode)


# ═══════════════════════ [节点4 Tool3] 预算计算器工具 ═══════════════════════

@app.get("/api/taxi_cost", summary="打车费估算")
def estimate_taxi_cost(
    origin: str = Query(..., description='出发点坐标，"经度,纬度"'),
    destination: str = Query(..., description='目的地坐标，"经度,纬度"'),
) -> dict:
    """估算两点间打车费用（预算计算器的交通费来源）。

    Returns:
        含 taxi_cost(预估费用，元)、distance_km、duration_min。
    """
    route = get_service().route_planning(origin, destination, mode="driving")
    return {
        "taxi_cost": route["taxi_cost"],
        "distance_km": route["distance_km"],
        "duration_min": route["duration_min"],
    }


# ═══════════════════════ [节点4 Tool4] 餐厅推荐工具 ═══════════════════════

@app.get("/api/restaurants", summary="周边餐厅推荐")
def recommend_restaurants(
    location: str = Query(..., description='中心点坐标（景点/酒店），"经度,纬度"'),
    radius: int = Query(2000, description="搜索半径（米）"),
    keyword: str | None = Query(None, description='口味关键词，如 "云南菜" / "米线" / "火锅"'),
    size: int = Query(10, description="返回条数"),
) -> list:
    """以某景点/酒店为中心，推荐周边餐厅（餐厅推荐 Agent 数据源）。

    输出可直接组装为需求文档中的表格：餐厅 | 距离 | 人均 | 评分。

    Returns:
        餐厅列表 [{name, distance_km, cost(人均), rating, address, tel, location}]
    """
    return get_service().restaurant_recommend(
        location, radius=radius, keyword=keyword, size=size
    )


# ═══════════════════════ [阶段1 KB] POI 区域搜索与详情 ═══════════════════════

@app.get("/api/poi/polygon", summary="多边形区域搜索")
def search_poi_polygon(
    polygon: list[str] = Query(
        ..., description='多边形顶点坐标列表，如 ["102.70,25.05", "102.72,25.03"]；'
                         "矩形可只传左上、右下两顶点，其他多边形首尾坐标需相同"),
    keywords: str | None = Query(None, description='查询关键字，如 "景点" / "咖啡馆"'),
    types: str | None = Query(None, description='POI 分类码，如 "110000"(风景名胜)'),
    size: int = Query(20, description="每页条数（≤25）"),
    page: int = Query(1, description="页码（翻页最多取 200 条）"),
) -> dict:
    """多边形区域搜索：在给定多边形范围内搜 POI。

    用于：搜索某个商圈/片区/景区范围内的景点或餐厅，
          比周边搜索（圆形）更贴合"某一片区域"的需求。

    Returns:
        含 count(总数) 与 pois 列表 [{id, name, type, address,
        location, tel, rating, cost}]。
    """
    try:
        return get_service().poi_polygon(
            polygon, keywords=keywords, types=types, size=size, page=page
        )
    except (AmapAPIError, ValueError) as e:
        return {"count": "0", "pois": [], "error": str(e)}


@app.get("/api/poi/detail", summary="POI ID 查询（详情）")
def get_poi_detail(
    id: str = Query(..., description='POI 唯一 ID，如 "B0FFFAB6J2"'),
) -> dict:
    """根据 POI ID 查询详情。

    /api/travel_spots、/api/restaurants 等返回的 POI 均带 id 字段，
    用本接口二次查询详情（评分、人均、电话、商圈、特色菜、照片），
    为阶段1知识卡片补全字段。

    Returns:
        POI 详情 {id, name, type, address, location, tel, rating,
        cost, business_area, tag, photos}；未找到时返回 found=False。
    """
    try:
        detail = get_service().poi_detail(id)
        if not detail:
            return {"found": False, "id": id}
        return {"found": True, **detail}
    except (AmapAPIError, ValueError) as e:
        return {"found": False, "id": id, "error": str(e)}


# ═══════════════════════ [Demo] 旅游推荐工具 ═══════════════════════

@app.get("/api/travel_spots", summary="旅游景点推荐")
def recommend_travel_spots(
    place: str = Query(..., description='地点名，如 "昆明" / "大理古城"'),
    keyword: str = Query("景点", description='搜索词，可换 "美食" / "公园" / "博物馆"'),
    size: int = Query(10, description="返回条数"),
) -> dict:
    """输入城市/地区名，推荐当地旅游景点。

    用于：行程候选景点调研（Planner Agent 调用）、
          RAG 知识库之外的实时 POI 补充。

    Returns:
        含 city、adcode、count 与 pois 列表
        [{name, type, address, location, tel, rating, cost}]。
    """
    return get_service().travel_recommend(place, keyword=keyword, size=size)


# ═══════════════════════ 天气工具 ═══════════════════════

@app.get("/api/weather", summary="天气查询")
def query_weather(
    city: str = Query(..., description='城市名称，如 "北京"、"昆明"'),
    forecast: bool = Query(True, description="是否包含未来3天预报"),
) -> dict:
    """查询指定城市的实时天气和未来3天预报。"""
    try:
        data = get_weather().get_weather(city, forecast=forecast, days=3)
        lines = []
        live = data.get("live") or {}
        if live:
            lines.append(
                f"当前天气：{live.get('weather')}，气温 {live.get('temperature')}°C，"
                f"湿度 {live.get('humidity')}%，{live.get('winddirection')}风 "
                f"{live.get('windpower')}级"
            )
        for cast in data.get("forecast", []):
            lines.append(
                f"{cast['date']}：{cast['nighttemp']}~{cast['daytemp']}°C，"
                f"白天{cast['dayweather']}，夜间{cast['nightweather']}"
            )
        summary = "\n".join(lines) or "天气数据解析失败，请按常规准备雨具与防晒。"
        return {"weather_summary": summary, "raw": data}
    except Exception as e:
        return {"weather_summary": "天气数据解析失败，请按常规准备雨具与防晒。",
                "error": str(e)}


# ═══════════════════════ 预算分配计算器 ═══════════════════════

@app.get("/api/budget", summary="旅行预算分配计算器")
def calc_budget(
    budget: float = Query(..., description="总预算（元）"),
    days: int = Query(..., description="天数"),
    people: int = Query(..., description="人数"),
) -> dict:
    """旅行预算分配计算器。"""
    total, d, p = float(budget), max(int(days), 1), max(int(people), 1)
    alloc = {
        "住宿": round(total * 0.35),
        "餐饮": round(total * 0.25),
        "门票": round(total * 0.15),
        "市内交通": round(total * 0.10),
        "其他/购物": round(total * 0.15),
    }
    lines = [f"{k}：{v} 元" for k, v in alloc.items()]
    return {
        "budget_summary": (
            f"总预算 {total:.0f} 元，共 {d} 天 {p} 人，"
            f"人均 {total / p:.1f} 元，日均 {total / d:.1f} 元\n" + "\n".join(lines)
        ),
        "total_budget": total,
        "per_person": round(total / p, 1),
        "per_day": round(total / d, 1),
        "allocation": alloc,
    }


# ═══════════════════════ 启动入口 ═══════════════════════

def main() -> None:
    import uvicorn

    if not os.environ.get("AMAP_KEY", "").strip():
        print("⚠️  警告：环境变量 AMAP_KEY 未设置，调用地图/天气接口时将报错。"
              "\n    请先执行: export AMAP_KEY=你的Web服务Key", file=sys.stderr)

    uvicorn.run(app, host="localhost", port=8000)


if __name__ == "__main__":
    main()
