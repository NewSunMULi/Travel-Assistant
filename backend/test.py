# -*- coding: utf-8 -*-
"""
test_amap_fastapi_server.py
===========================
amap_fastapi_server.py 的自动化测试（pytest）。

运行方式：
    pip install pytest httpx fastapi "uvicorn[standard]"
    export AMAP_KEY=110
    pytest test_amap_fastapi_server.py -v

说明：
    key 为假值（110），真实高德接口无法调通，因此：
    - 不依赖高德 API 的接口（/、/api/health、/api/budget）直接测真实逻辑；
    - 依赖高德的接口用 Mock 替换底层 MapServices / AmapWeather，
      验证路由、参数透传与异常分支的正确性。
"""

import os
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

# 必须在 import 服务模块之前设置 Key，模拟用户指定的测试 Key
os.environ["AMAP_KEY"] = "110"

import api as srv  # noqa: E402
from serives.MapSerive import AmapAPIError  # noqa: E402


# ─────────────────────────── fixtures ───────────────────────────

@pytest.fixture()
def client():
    """每个用例使用全新的 TestClient。"""
    with TestClient(srv.app) as c:
        yield c


@pytest.fixture()
def mock_map_service(monkeypatch):
    """用 MagicMock 替换 MapServices 单例，返回可控的假数据。"""
    fake = MagicMock()
    monkeypatch.setattr(srv, "_SERVICE", fake)
    yield fake
    monkeypatch.setattr(srv, "_SERVICE", None)


@pytest.fixture()
def mock_weather(monkeypatch):
    """用 MagicMock 替换 AmapWeather 单例。"""
    fake = MagicMock()
    monkeypatch.setattr(srv, "_WEATHER", fake)
    yield fake
    monkeypatch.setattr(srv, "_WEATHER", None)


# ═══════════════════════ 基础接口 ═══════════════════════

class TestBasic:
    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        body = r.json()
        assert body["service"] == "amap-kunming-travel-map"
        assert body["amap_key_configured"] is True  # AMAP_KEY=110 已设置

    def test_health(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


# ═══════════════════════ 预算计算器（真实逻辑，无需 Key） ═══════════════════════

class TestBudget:
    def test_normal(self, client):
        r = client.get("/api/budget", params={"budget": 3000, "days": 3, "people": 2})
        assert r.status_code == 200
        body = r.json()
        assert body["total_budget"] == 3000.0
        assert body["per_person"] == 1500.0
        assert body["per_day"] == 1000.0
        alloc = body["allocation"]
        assert alloc["住宿"] == 1050
        assert alloc["餐饮"] == 750
        assert alloc["门票"] == 450
        assert alloc["市内交通"] == 300
        assert alloc["其他/购物"] == 450
        assert "人均 1500.0 元" in body["budget_summary"]

    def test_days_people_floor_to_one(self, client):
        """days / people 传入 0 或负数时应按 1 处理，不得除零。"""
        r = client.get("/api/budget", params={"budget": 1000, "days": 0, "people": -2})
        assert r.status_code == 200
        body = r.json()
        assert body["per_day"] == 1000.0
        assert body["per_person"] == 1000.0

    def test_missing_param_422(self, client):
        """缺少必填参数时应返回 422。"""
        r = client.get("/api/budget", params={"budget": 1000})
        assert r.status_code == 422


# ═══════════════════════ 地理编码 ═══════════════════════

class TestGeocode:
    def test_found(self, client, mock_map_service):
        mock_map_service.geocode.return_value = [{
            "location": "102.712251,25.040609",
            "province": "云南省", "city": "昆明市",
            "district": "五华区", "adcode": "530102", "level": "兴趣点",
        }]
        r = client.get("/api/geocode",
                       params={"address": "昆明市翠湖公园", "city": "昆明"})
        assert r.status_code == 200
        body = r.json()
        assert body["found"] is True
        assert body["location"] == "102.712251,25.040609"
        assert body["district"] == "五华区"
        # 验证参数透传
        mock_map_service.geocode.assert_called_once_with("昆明市翠湖公园", city="昆明")

    def test_not_found(self, client, mock_map_service):
        mock_map_service.geocode.return_value = []
        r = client.get("/api/geocode", params={"address": "不存在的地址xyz"})
        assert r.status_code == 200
        body = r.json()
        assert body["found"] is False
        assert body["location"] is None

    def test_amap_error(self, client, mock_map_service):
        """高德 API 抛错时返回 found=False 和 error 信息，而不是 500。"""
        mock_map_service.geocode.side_effect = AmapAPIError("INVALID_USER_KEY")
        r = client.get("/api/geocode", params={"address": "翠湖公园"})
        assert r.status_code == 200
        body = r.json()
        assert body["found"] is False
        assert "INVALID_USER_KEY" in body["error"]


class TestBatchGeocode:
    def test_batch(self, client, mock_map_service):
        mock_map_service.batch_geocode.return_value = [
            {"address": "昆明市翠湖公园", "location": "102.712251,25.040609", "detail": {}},
            {"address": "滇池海埂大坝", "location": None, "detail": {}},
        ]
        r = client.post("/api/geocode/batch", json={
            "addresses": ["昆明市翠湖公园", "滇池海埂大坝"],
            "city": "昆明",
        })
        assert r.status_code == 200
        body = r.json()
        assert len(body) == 2
        assert body[0]["location"] is not None
        assert body[1]["location"] is None
        mock_map_service.batch_geocode.assert_called_once_with(
            ["昆明市翠湖公园", "滇池海埂大坝"], city="昆明")

    def test_empty_addresses_422(self, client, mock_map_service):
        """缺少 addresses 字段应返回 422。"""
        r = client.post("/api/geocode/batch", json={})
        assert r.status_code == 422


class TestReverseGeocode:
    def test_regeo(self, client, mock_map_service):
        mock_map_service.regeo.return_value = {
            "province": "云南省", "city": "昆明市", "district": "五华区",
        }
        r = client.get("/api/reverse_geocode",
                       params={"location": "102.712251,25.040609"})
        assert r.status_code == 200
        assert r.json()["city"] == "昆明市"
        mock_map_service.regeo.assert_called_once_with("102.712251,25.040609")


# ═══════════════════════ 路径规划 ═══════════════════════

class TestRoute:
    def test_driving(self, client, mock_map_service):
        mock_map_service.route_planning.return_value = {
            "distance": 12500, "duration": 1800,
            "distance_km": 12.5, "duration_min": 30.0,
            "taxi_cost": 35.0, "steps": ["沿翠湖南路行驶 500 米"],
        }
        r = client.get("/api/route", params={
            "origin": "102.712251,25.040609",
            "destination": "102.671859,24.974336",
            "mode": "driving",
        })
        assert r.status_code == 200
        body = r.json()
        assert body["distance_km"] == 12.5
        assert body["taxi_cost"] == 35.0
        mock_map_service.route_planning.assert_called_once_with(
            "102.712251,25.040609", "102.671859,24.974336", mode="driving")

    def test_default_mode(self, client, mock_map_service):
        mock_map_service.route_planning.return_value = {}
        client.get("/api/route", params={
            "origin": "102.7,25.0", "destination": "102.6,24.9"})
        _, kwargs = mock_map_service.route_planning.call_args
        assert kwargs["mode"] == "driving"  # 默认驾车

    def test_multi(self, client, mock_map_service):
        mock_map_service.route_multi.return_value = {
            "distance": 30000, "duration": 3600,
            "taxi_cost": 80.0, "legs": [{}, {}], "steps": [],
        }
        r = client.post("/api/route/multi", json={
            "origin": "102.7,25.0",
            "destination": "102.6,24.9",
            "waypoints": ["102.65,24.95"],
            "mode": "driving",
        })
        assert r.status_code == 200
        assert r.json()["taxi_cost"] == 80.0
        mock_map_service.route_multi.assert_called_once_with(
            "102.7,25.0", "102.6,24.9", ["102.65,24.95"], mode="driving")

    def test_multi_missing_waypoints_422(self, client, mock_map_service):
        r = client.post("/api/route/multi", json={
            "origin": "102.7,25.0", "destination": "102.6,24.9"})
        assert r.status_code == 422


class TestTaxiCost:
    def test_taxi_cost(self, client, mock_map_service):
        mock_map_service.route_planning.return_value = {
            "taxi_cost": 42.0, "distance_km": 15.2, "duration_min": 28.0,
            "distance": 15200, "duration": 1680, "steps": [],
        }
        r = client.get("/api/taxi_cost", params={
            "origin": "102.7,25.0", "destination": "102.6,24.9"})
        assert r.status_code == 200
        body = r.json()
        # 只返回裁剪后的三个字段
        assert set(body.keys()) == {"taxi_cost", "distance_km", "duration_min"}
        assert body["taxi_cost"] == 42.0
        # 内部必须以 driving 模式调用
        _, kwargs = mock_map_service.route_planning.call_args
        assert kwargs["mode"] == "driving"


# ═══════════════════════ 餐厅 / 景点推荐 ═══════════════════════

class TestRestaurants:
    def test_recommend(self, client, mock_map_service):
        mock_map_service.restaurant_recommend.return_value = [
            {"name": "桥香园过桥米线", "distance_km": 0.3, "cost": "35",
             "rating": "4.5", "address": "五华区xx路", "tel": "0871-xxx",
             "location": "102.71,25.04"},
        ]
        r = client.get("/api/restaurants", params={
            "location": "102.712251,25.040609",
            "radius": 1000, "keyword": "米线", "size": 5,
        })
        assert r.status_code == 200
        body = r.json()
        assert body[0]["name"] == "桥香园过桥米线"
        mock_map_service.restaurant_recommend.assert_called_once_with(
            "102.712251,25.040609", radius=1000, keyword="米线", size=5)

    def test_defaults(self, client, mock_map_service):
        mock_map_service.restaurant_recommend.return_value = []
        r = client.get("/api/restaurants",
                       params={"location": "102.7,25.0"})
        assert r.status_code == 200
        _, kwargs = mock_map_service.restaurant_recommend.call_args
        assert kwargs == {"radius": 2000, "keyword": None, "size": 10}


class TestTravelSpots:
    def test_recommend(self, client, mock_map_service):
        mock_map_service.travel_recommend.return_value = {
            "city": "昆明市", "adcode": "530100", "count": 1,
            "pois": [{"name": "翠湖公园", "type": "公园",
                      "address": "五华区", "location": "102.71,25.04",
                      "tel": "", "rating": "4.6", "cost": "0"}],
        }
        r = client.get("/api/travel_spots",
                       params={"place": "昆明", "keyword": "景点", "size": 10})
        assert r.status_code == 200
        body = r.json()
        assert body["city"] == "昆明市"
        assert body["pois"][0]["name"] == "翠湖公园"
        mock_map_service.travel_recommend.assert_called_once_with(
            "昆明", keyword="景点", size=10)


# ═══════════════════════ 天气 ═══════════════════════

class TestWeather:
    def test_live_and_forecast(self, client, mock_weather):
        mock_weather.get_weather.return_value = {
            "live": {"weather": "晴", "temperature": "22", "humidity": "45",
                     "winddirection": "西南", "windpower": "3"},
            "forecast": [
                {"date": "2026-09-10", "nighttemp": "15", "daytemp": "25",
                 "dayweather": "晴", "nightweather": "多云"},
                {"date": "2026-09-11", "nighttemp": "16", "daytemp": "26",
                 "dayweather": "多云", "nightweather": "小雨"},
            ],
        }
        r = client.get("/api/weather", params={"city": "昆明", "forecast": True})
        assert r.status_code == 200
        body = r.json()
        assert "当前天气：晴" in body["weather_summary"]
        assert "气温 22°C" in body["weather_summary"]
        assert "2026-09-10" in body["weather_summary"]
        assert body["raw"]["live"]["weather"] == "晴"
        mock_weather.get_weather.assert_called_once_with("昆明", forecast=True, days=3)

    def test_exception_fallback(self, client, mock_weather):
        """天气服务异常（如假 Key 110 鉴权失败）时应返回兜底文案而非 500。"""
        mock_weather.get_weather.side_effect = RuntimeError("INVALID_USER_KEY")
        r = client.get("/api/weather", params={"city": "昆明"})
        assert r.status_code == 200
        body = r.json()
        assert body["weather_summary"] == "天气数据解析失败，请按常规准备雨具与防晒。"
        assert "INVALID_USER_KEY" in body["error"]

    def test_empty_data_fallback(self, client, mock_weather):
        """返回数据为空时同样走兜底文案。"""
        mock_weather.get_weather.return_value = {}
        r = client.get("/api/weather", params={"city": "昆明"})
        assert r.status_code == 200
        assert r.json()["weather_summary"] == "天气数据解析失败，请按常规准备雨具与防晒。"


# ═══════════════════════ Key 未配置场景 ═══════════════════════

class TestKeyNotConfigured:
    def test_weather_without_key(self, client, monkeypatch):
        """AMAP_KEY 为空时，天气接口走异常兜底且 error 提示设置 Key。"""
        monkeypatch.setattr(srv, "_WEATHER", None)
        monkeypatch.setitem(os.environ, "AMAP_KEY", "")
        r = client.get("/api/weather", params={"city": "昆明"})
        assert r.status_code == 200
        body = r.json()
        assert "error" in body
        assert "AMAP_KEY" in body["error"]
        monkeypatch.setitem(os.environ, "AMAP_KEY", "110")
