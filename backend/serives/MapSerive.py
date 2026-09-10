# -*- coding: utf-8 -*-
"""
MapServices.py  v2.0
====================
基于高德地图 Web 服务 API 的封装类（文档: https://lbs.amap.com/api/webservice/summary）

对应《昆明智能旅行决策 Agent》需求文档，本模块覆盖的任务：
    [节点4 Tool2] 地图/POI/路线工具 ......... geocode / get_location / search_poi
    [节点4 Tool3] 预算计算器(交通费) ........ taxi_cost（driving 返回 taxi_cost）
    [节点4 Tool4] 餐厅推荐 Agent ............ restaurant_recommend / poi_around
    [节点5 Verifier] 时间/体力/返程校验 ..... route_planning / route_multi
    [阶段1 KB1] 景区知识库"位置"字段 ........ batch_geocode / regeo
    [Demo] 旅游推荐 .......................... travel_recommend

Key 从环境变量 AMAP_KEY 读取，其余必填参数均为函数形参，各方法相互解耦。

用法示例：
    export AMAP_KEY=你的key
    from MapServices import MapServices
    ms = MapServices()
    loc = ms.get_location("昆明市翠湖公园")
    route = ms.route_planning(loc, "102.683669,25.031319", mode="walking")
    spots = ms.travel_recommend("昆明")
"""

import os
import requests


# ────────────────────────────── 自定义异常 ──────────────────────────────
class AmapAPIError(Exception):
    """高德 API 返回业务错误时抛出（status != "1"）。"""

    def __init__(self, info: str, infocode: str = None):
        self.info = info
        self.infocode = infocode
        super().__init__(f"[高德API错误] info={info}, infocode={infocode}")


class MapServices:
    """高德地图 Web 服务 API 封装。

    Attributes:
        key:     从环境变量 AMAP_KEY 读取的 Web 服务类型 Key
        session: 复用的 HTTP 会话（连接池，提升多次调用性能）
    """

    BASE_URL = "https://restapi.amap.com"
    TIMEOUT = 10

    # 支持的出行方式 → API 路径（节点4 Tool2 / 节点5 Verifier）
    ROUTE_MODES = {
        "driving": "/v3/direction/driving",     # 驾车
        "walking": "/v3/direction/walking",     # 步行
        "bicycling": "/v3/direction/bicycling", # 骑车（骑行）
    }

    # 常用 POI 分类码（place/text 与 place/around 的 types 参数）
    POI_TYPES = {
        "restaurant": "050000",   # 餐饮服务（餐厅推荐 Agent）
        "hotel": "100000",        # 住宿服务
        "scenic": "110000",       # 风景名胜（景区知识库 / 旅游推荐）
        "shopping": "060000",     # 购物服务
        "transport": "150000",    # 交通设施服务
    }

    def __init__(self, key: str = None, env_var: str = "AMAP_KEY"):
        """初始化。

        Args:
            key:     可选，直接传入 Key；不传则从环境变量 env_var 读取
            env_var: 环境变量名，默认为 "AMAP_KEY"
        """
        self.key = key or os.environ.get(env_var, "").strip()
        if not self.key:
            raise EnvironmentError(
                f"未找到高德 Key：请设置环境变量 {env_var}，"
                f"或实例化时传入 key 参数，如 MapServices(key='你的key')"
            )
        self.session = requests.Session()

    # ──────────────────────── 底层请求（私有） ────────────────────────
    def _request(self, endpoint: str, params: dict) -> dict:
        """发送 GET 请求并解析 JSON，统一做状态检查。各功能方法共用。"""
        params = {**params, "key": self.key, "output": "json"}
        resp = self.session.get(self.BASE_URL + endpoint,
                                params=params, timeout=self.TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if str(data.get("status")) != "1":
            raise AmapAPIError(data.get("info", "unknown"), data.get("infocode"))
        return data

    # ───────────────────── 1. 地理编码：文字 → 经纬度 ─────────────────────
    def geocode(self, address: str, city: str = None) -> list:
        """根据文字地址获取经纬度。

        对应接口: https://restapi.amap.com/v3/geocode/geo

        Args:
            address: 结构化地址（必填），如 "云南省昆明市五华区翠湖公园"
            city:    指定查询城市（可选），城市中文/全拼/citycode/adcode，
                     如 "昆明" 或 "530100"，可提高匹配精度

        Returns:
            geocodes 列表，每个元素含 location("经度,纬度")、province、
            city、district、adcode、level 等字段；无结果返回空列表。
        """
        params = {"address": address}
        if city:
            params["city"] = city
        data = self._request("/v3/geocode/geo", params)
        return data.get("geocodes", [])

    def get_location(self, address: str, city: str = None) -> str:
        """geocode 的便捷封装：返回首个结果的 "经度,纬度" 字符串。

        Args:
            address: 结构化地址（必填）
            city:    指定查询城市（可选）

        Returns:
            "经度,纬度" 字符串，可直接作为路径规划 origin/destination。

        Raises:
            ValueError: 地址无法解析出坐标时抛出。
        """
        geocodes = self.geocode(address, city=city)
        if not geocodes:
            raise ValueError(f"无法解析地址坐标: {address}")
        return geocodes[0]["location"]

    def batch_geocode(self, addresses: list, city: str = None) -> list:
        """批量地理编码（阶段1 KB1 景区知识库"位置"字段批量填充）。

        Args:
            addresses: 地址列表（必填），如 ["昆明市翠湖公园", "滇池海埂大坝"]
            city:      统一指定城市（可选），提高匹配精度

        Returns:
            与输入等长的结果列表，每项为
            {"address": 原地址, "location": "经度,纬度" 或 None, "detail": geocodes[0] 或 None}
            单条失败不影响其他条目。
        """
        results = []
        for addr in addresses:
            try:
                g = self.geocode(addr, city=city)
                results.append({
                    "address": addr,
                    "location": g[0]["location"] if g else None,
                    "detail": g[0] if g else None,
                })
            except AmapAPIError as e:
                results.append({"address": addr, "location": None, "detail": None, "error": str(e)})
        return results

    def regeo(self, location: str, radius: int = 1000) -> dict:
        """逆地理编码：经纬度 → 结构化地址（备用，可用于当前位置解析）。

        对应接口: https://restapi.amap.com/v3/geocode/regeo

        Args:
            location: "经度,纬度"（必填），小数点后不超过6位
            radius:   搜索半径，0~3000 米，默认 1000

        Returns:
            regeocode 对象，含 addressComponent（省/市/区/街道等）。
        """
        data = self._request("/v3/geocode/regeo", {
            "location": location, "radius": radius,
        })
        return data.get("regeocode", {})

    # ───────────────────── 2. POI 搜索：关键字 / 分类 ─────────────────────
    def search_poi(self, keywords: str = None, types: str = None,
                   city: str = None, citylimit: bool = True,
                   size: int = 20, page: int = 1) -> dict:
        """POI 关键字/分类搜索（节点4 Tool2 的核心，travel_recommend 底层）。

        对应接口: https://restapi.amap.com/v3/place/text

        Args:
            keywords: 查询关键字（keywords 与 types 至少传一个）
            types:    POI 分类码（可选），如 "110000"(风景名胜)、"050000"(餐饮)，
                      见 POI_TYPES 常量；分类搜索比泛关键词更精确
            city:     城市中文/citycode/adcode（可选），不填则全国搜索
            citylimit: 是否仅返回指定城市数据，默认 True
            size:     每页条数（可选，建议 ≤25，默认 20）
            page:     页码（可选，默认 1；翻页最多取 200 条）

        Returns:
            dict，含 count(总数) 与 pois 列表（含 name/type/address/location/tel/rating）。
        """
        if not keywords and not types:
            raise ValueError("keywords 与 types 至少传入一个")
        params = {
            "citylimit": "true" if citylimit else "false",
            "offset": min(max(size, 1), 25),
            "page": max(page, 1),
            "extensions": "all",   # 返回评分(rating)等深度信息
        }
        if keywords:
            params["keywords"] = keywords
        if types:
            params["types"] = types
        if city:
            params["city"] = city

        data = self._request("/v3/place/text", params)
        return self._format_pois(data)

    def poi_around(self, location: str, keywords: str = None,
                   types: str = None, radius: int = 3000,
                   sortrule: str = "distance", size: int = 20) -> dict:
        """周边搜索：给定中心点坐标，搜半径内的 POI。

        对应接口: https://restapi.amap.com/v3/place/around
        支撑《节点4 Tool4 餐厅推荐 Agent》——输入景点坐标，搜周边餐厅。

        Args:
            location: 中心点坐标（必填），"经度,纬度"
            keywords: 查询关键字（可选），如 "米线"/"火锅"；与 types 至少传一个
            types:    POI 分类码（可选），如 "050000"(餐饮)
            radius:   搜索半径（可选），0~50000 米，默认 3000
            sortrule: 排序（可选），distance(距离)/weight(综合)，默认 distance
            size:     每页条数（可选，≤25，默认 20）

        Returns:
            dict，含 count 与 pois 列表，pois 含 distance(距中心点，米)。
        """
        if not keywords and not types:
            raise ValueError("keywords 与 types 至少传入一个")
        params = {
            "location": location,
            "radius": min(max(radius, 0), 50000),
            "sortrule": sortrule,
            "offset": min(max(size, 1), 25),
            "page": 1,
            "extensions": "all",
        }
        if keywords:
            params["keywords"] = keywords
        if types:
            params["types"] = types

        data = self._request("/v3/place/around", params)
        return self._format_pois(data, with_distance=True)

    def poi_polygon(self, polygon: list | str, keywords: str = None,
                    types: str = None, size: int = 20, page: int = 1) -> dict:
        """多边形区域搜索：在给定的多边形范围内搜 POI。

        对应接口: https://restapi.amap.com/v3/place/polygon
        适用场景：搜索某个行政区/商圈/景区范围内的景点或餐厅，
                  比周边搜索(圆形)更贴合"某一片区域"的需求。

        Args:
            polygon:  多边形顶点坐标（必填）。
                      - 传 list：["经度,纬度", ...]，矩形可只传左上、右下两顶点，
                        其他多边形首尾坐标需相同；
                      - 传 str：已是 "lng,lat|lng,lat|..." 格式则原样使用。
            keywords: 查询关键字（可选），与 types 至少传一个
            types:    POI 分类码（可选），如 "110000"(风景名胜)
            size:     每页条数（可选，≤25，默认 20）
            page:     页码（可选，默认 1；翻页最多取 200 条）

        Returns:
            dict，含 count(总数) 与 pois 列表（格式同 search_poi）。

        Raises:
            ValueError: keywords 与 types 均未传，或 polygon 坐标格式非法。
        """
        if not keywords and not types:
            raise ValueError("keywords 与 types 至少传入一个")
        if isinstance(polygon, (list, tuple)):
            if len(polygon) < 2:
                raise ValueError("polygon 至少需要 2 个顶点坐标")
            for i, pt in enumerate(polygon):
                self._check_coord(f"polygon[{i}]", pt)
            polygon = "|".join(polygon)
        params = {
            "polygon": polygon,
            "offset": min(max(size, 1), 25),
            "page": max(page, 1),
            "extensions": "all",
        }
        if keywords:
            params["keywords"] = keywords
        if types:
            params["types"] = types

        data = self._request("/v3/place/polygon", params)
        return self._format_pois(data)

    def poi_detail(self, poi_id: str) -> dict:
        """POI ID 查询：根据唯一 ID 查询某个 POI 的详情。

        对应接口: https://restapi.amap.com/v3/place/detail
        适用场景：search_poi / poi_around / travel_recommend 返回的 POI
                  均带 id 字段，可用本方法二次查询详情（评分、人均、
                  电话、商圈等深度信息），为知识卡片补全字段。

        Args:
            poi_id: POI 唯一 ID（必填），如 "B0FFFAB6J2"

        Returns:
            dict，POI 详情 {id, name, type, address, location, tel,
            rating, cost, ...}；未找到时返回空 dict。

        Raises:
            ValueError: poi_id 为空时抛出。
        """
        if not poi_id:
            raise ValueError("poi_id 不能为空")
        data = self._request("/v3/place/detail", {"id": poi_id})
        pois = data.get("pois") or []
        if not pois:
            return {}
        p = pois[0]
        return {
            "id": p.get("id"),
            "name": p.get("name"),
            "type": p.get("type"),
            "typecode": p.get("typecode"),
            "address": p.get("address"),
            "location": p.get("location"),
            "tel": p.get("tel"),
            "rating": (p.get("biz_ext") or {}).get("rating"),
            "cost": (p.get("biz_ext") or {}).get("cost"),
            "business_area": p.get("business_area"),   # 所属商圈
            "tag": p.get("tag"),                       # 特色内容（美食类为招牌菜）
            "photos": [ph.get("url") for ph in (p.get("photos") or []) if isinstance(ph, dict)],
        }

    def _format_pois(self, data: dict, with_distance: bool = False) -> dict:
        """统一 POI 返回格式（私有）。"""
        pois = []
        for p in data.get("pois", []):
            item = {
                "id": p.get("id"),   # POI 唯一 ID，供 poi_detail 二次查询详情
                "name": p.get("name"),
                "type": p.get("type"),
                "typecode": p.get("typecode"),
                "address": p.get("address"),
                "location": p.get("location"),
                "tel": p.get("tel"),
                "rating": (p.get("biz_ext") or {}).get("rating"),   # 景点/餐厅评分
                "cost": (p.get("biz_ext") or {}).get("cost"),       # 人均消费
            }
            if with_distance:
                item["distance"] = int(p.get("distance", 0))        # 距中心点，米
            pois.append(item)
        return {"count": data.get("count", "0"), "pois": pois}

    def restaurant_recommend(self, location: str, radius: int = 2000,
                             keyword: str = None, size: int = 10) -> list:
        """餐厅推荐（节点4 Tool4 餐厅推荐 Agent 的直接数据支撑）。

        以景点/酒店坐标为中心，搜索周边餐饮 POI，并按距离排序，
        返回可生成"餐厅|距离|人均|评分"表格的结构化数据。

        Args:
            location: 中心点坐标（必填），"经度,纬度"，如景点坐标
            radius:   搜索半径（可选），默认 2000 米
            keyword:  口味/品类关键词（可选），如 "云南菜"/"米线"/"火锅"
            size:     返回条数（可选，默认 10）

        Returns:
            餐厅列表 [{name, distance, cost, rating, address, location, tel}, ...]
        """
        data = self.poi_around(
            location,
            keywords=keyword,
            types=self.POI_TYPES["restaurant"],
            radius=radius,
            sortrule="distance",
            size=size,
        )
        return [
            {
                "name": p["name"],
                "distance": p.get("distance"),      # 距景点，米
                "distance_km": round(p.get("distance", 0) / 1000, 2),
                "cost": p.get("cost"),              # 人均消费（元）
                "rating": p.get("rating"),          # 评分
                "address": p.get("address"),
                "location": p.get("location"),
                "tel": p.get("tel"),
            }
            for p in data["pois"]
        ]

    # ───────────────────── 3. 路径规划：多出行方式 ─────────────────────
    @staticmethod
    def _check_coord(name: str, coord: str) -> None:
        """坐标格式校验（私有）：必须为 '经度,纬度'。"""
        parts = coord.split(",")
        if len(parts) != 2 or not all(p.strip() for p in parts):
            raise ValueError(f"{name} 坐标格式应为 '经度,纬度'，当前值: {coord}")

    def route_planning(self, origin: str, destination: str,
                       mode: str = "driving") -> dict:
        """根据出发点与目的地做路径规划（节点4 Tool2 / 节点5 Verifier）。

        对应接口:
            驾车  /v3/direction/driving
            步行  /v3/direction/walking
            骑车  /v3/direction/bicycling

        Args:
            origin:      出发点坐标（必填），格式 "经度,纬度"，小数点后不超过6位
            destination: 目的地坐标（必填），格式同上
            mode:        出行方式（必填，默认 driving），可选
                         driving(驾车) / walking(步行) / bicycling(骑车)

        Returns:
            dict，包含:
                mode        出行方式
                distance    总距离（米）
                duration    总耗时（秒）
                distance_km 总距离（公里，float）
                duration_min总耗时（分钟，float）
                taxi_cost   预估打车费（元，仅驾车返回，供预算计算器使用）
                steps       分路段指引列表 [{instruction, distance, ...}, ...]

        Raises:
            ValueError:  坐标格式非法或 mode 不支持时抛出。
        """
        if mode not in self.ROUTE_MODES:
            raise ValueError(
                f"不支持的出行方式: {mode}，可选 {list(self.ROUTE_MODES)}"
            )
        self._check_coord("origin", origin)
        self._check_coord("destination", destination)

        data = self._request(self.ROUTE_MODES[mode], {
            "origin": origin,
            "destination": destination,
        })

        path = data["route"]["paths"][0]
        distance = int(path["distance"])
        duration = int(path["duration"])
        return {
            "mode": mode,
            "distance": distance,
            "duration": duration,
            "distance_km": round(distance / 1000, 2),
            "duration_min": round(duration / 60, 1),
            # 仅驾车返回：预估打车费（节点4 Tool3 预算计算器使用）
            "taxi_cost": data["route"].get("taxi_cost") if mode == "driving" else None,
            "steps": [
                {
                    "instruction": s.get("instruction"),
                    "distance": int(s.get("distance", 0)),
                    "road": s.get("road_name", ""),
                }
                for s in path.get("steps", [])
            ],
        }

    def route_multi(self, origin: str, destination: str,
                    waypoints: list, mode: str = "driving") -> dict:
        """多途经点路线规划：解决"一天多个景点串联"（节点5 Verifier 时间校验）。

        对应 Demo 场景：Day2 "滇池 → 海埂大坝 → 西山" 一线串联，
        防止 AI 把路线排反，并给出全天总耗时/总里程。

        Args:
            origin:      出发点坐标（必填），"经度,纬度"
            destination: 终点坐标（必填），"经度,纬度"
            waypoints:   途经点坐标列表（必填），如 ["102.68,24.98", "102.66,24.99"]，
                         按游览顺序传入；驾车最多 16 个
            mode:        出行方式（可选，默认 driving），仅 driving/walking
                         支持途经点，骑车(bicycling)不支持

        Returns:
            与 route_planning 相同结构的 dict（含总距离、总耗时、分段指引），
            另含 legs 每段子路线明细（便于 Verifier 检查单段耗时）。
        """
        if mode not in ("driving", "walking"):
            raise ValueError(f"途经点规划仅支持 driving/walking，不支持 {mode}")
        self._check_coord("origin", origin)
        self._check_coord("destination", destination)
        if not waypoints:
            raise ValueError("waypoints 途经点列表不能为空")
        for i, wp in enumerate(waypoints):
            self._check_coord(f"waypoints[{i}]", wp)

        data = self._request(self.ROUTE_MODES[mode], {
            "origin": origin,
            "destination": destination,
            "waypoints": ";".join(waypoints),   # 多个途经点用英文分号分隔
        })

        path = data["route"]["paths"][0]
        distance = int(path["distance"])
        duration = int(path["duration"])
        return {
            "mode": mode,
            "waypoints": waypoints,
            "distance": distance,
            "duration": duration,
            "distance_km": round(distance / 1000, 2),
            "duration_min": round(duration / 60, 1),
            "taxi_cost": data["route"].get("taxi_cost") if mode == "driving" else None,
            "legs": [
                {"distance": int(l.get("distance", 0)), "duration": int(l.get("duration", 0))}
                for l in path.get("legs", [])
            ],
            "steps": [
                {
                    "instruction": s.get("instruction"),
                    "distance": int(s.get("distance", 0)),
                    "road": s.get("road_name", ""),
                }
                for s in path.get("steps", [])
            ],
        }

    def taxi_cost(self, origin: str, destination: str) -> float:
        """预估打车费用（节点4 Tool3 预算计算器的交通费来源）。

        复用驾车路径规划接口，仅提取 taxi_cost 字段，避免冗余传输。

        Args:
            origin:      出发点坐标（必填），"经度,纬度"
            destination: 目的地坐标（必填），"经度,纬度"

        Returns:
            预估打车费（元，float）；接口未返回时为 None。
        """
        route = self.route_planning(origin, destination, mode="driving")
        return route["taxi_cost"]

    # ───────────────────── 4. 旅游推荐：地点 → 景点信息 ─────────────────────
    def travel_recommend(self, place: str, keyword: str = "景点",
                         city: str = None, size: int = 10) -> dict:
        """输入一个地点，给出该地点周边的旅游推荐信息。

        实现思路：先用地理编码把 place 解析为城市 adcode，再用 POI
        关键字搜索该城市内的旅游景点。

        对应接口: https://restapi.amap.com/v3/place/text

        Args:
            place:   地点名（必填），如 "昆明" / "大理" / "丽江"
            keyword: 搜索关键词（可选，默认 "景点"），如 "景点"/"美食"/"公园"
            city:    限定城市（可选），默认根据 place 自动解析；
                     可传城市中文/citycode/adcode，精确度更高
            size:    返回推荐条数（可选，默认 10，上限 25）

        Returns:
            dict，包含:
                place    查询地点
                city     解析到的城市
                adcode   城市区域编码
                count    服务端匹配总数
                pois     推荐列表 [{name, type, address, location, tel,
                                     rating, ...}, ...]
        """
        # 1) 解析地点 → 城市 adcode（失败则退化为关键字全国搜索）
        adcode, cityname = None, place
        geocodes = self.geocode(place, city=city)
        if geocodes:
            adcode = geocodes[0].get("adcode")
            cityname = geocodes[0].get("city") or place

        # 2) 城市内搜索 POI
        result = self.search_poi(
            keywords=f"{place}{keyword}",
            city=city or adcode or place,
            citylimit=True,
            size=size,
        )
        return {
            "place": place,
            "city": cityname,
            "adcode": adcode,
            "count": result["count"],
            "pois": result["pois"],
        }


# ────────────────────────────── 自测入口 ──────────────────────────────
if __name__ == "__main__":
    import json
    ms = MapServices('328dce04c8af238cccf56965d1a6a2fa')  # 依赖环境变量 AMAP_KEY

    # 1. 文字 → 经纬度
    loc = ms.get_location("昆明市翠湖公园")
    print("翠湖公园坐标:", loc)

    # 2. 路径规划（节点4 Tool2）
    route = ms.route_planning(loc, "102.683669,25.031319", mode="walking")
    print(f"\n步行: {route['distance_km']} km, 约 {route['duration_min']} 分钟")

    # 3. 多途经点路线（节点5 Verifier：Day2 滇池→海埂大坝→西山 串联）
    try:
        multi = ms.route_multi(loc, "102.629364,24.953531",
                               waypoints=["102.671859,24.974336"],
                               mode="driving")
        print(f"\n多途经点驾车: {multi['distance_km']} km, 约 {multi['duration_min']} 分钟,"
              f" 打车费约 {multi['taxi_cost']} 元")
    except Exception as e:
        print("\n多途经点规划未成功（示例坐标可能偏出道路网）:", e)

    # 4. 餐厅推荐（节点4 Tool4：翠湖周边 2km 内餐厅）
    restaurants = ms.restaurant_recommend(loc, radius=2000, size=5)
    print("\n翠湖周边餐厅:")
    for r in restaurants:
        print(f"  - {r['name']} | 距{ r['distance_km']}km | 人均{r['cost']} | 评分{r['rating']}")

    # 5. 旅游推荐
    rec = ms.travel_recommend("昆明", keyword="景点", size=5)
    print(f"\n{rec['city']} 共匹配 {rec['count']} 个景点，推荐前 {len(rec['pois'])} 个:")
    for p in rec["pois"]:
        print(f"  - {p['name']}（{p['address']}）评分: {p['rating']}")

    # 6. 批量地理编码（阶段1 KB1 位置字段填充示例）
    batch = ms.batch_geocode(["昆明市翠湖公园", "滇池海埂大坝"], city="昆明")
    print("\n批量地理编码:")
    for b in batch:
        print(f"  - {b['address']}: {b['location']}")
