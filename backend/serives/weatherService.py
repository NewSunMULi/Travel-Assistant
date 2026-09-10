# weather_service.py
import requests


class AmapWeather:
    """高德天气查询服务：地名→adcode→实况/预报天气。"""

    BASE_URL = "https://restapi.amap.com/v3"

    def __init__(self, key: str, timeout: int = 10):
        if not key:
            raise ValueError("必须提供高德 Web 服务 API Key")
        self.key = key
        self.timeout = timeout
        self._adcode_cache: dict[str, str] = {}  # 地名 -> adcode 缓存，减少重复查询

    # ---------- 内部方法 ----------
    def _get(self, path: str, params: dict) -> dict:
        params = {**params, "key": self.key, "output": "JSON"}
        resp = requests.get(f"{self.BASE_URL}{path}", params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "1":
            raise RuntimeError(
                f"高德API错误 infocode={data.get('infocode')}: {data.get('info')}"
            )
        return data

    def resolve_adcode(self, city: str, use_cache: bool = True) -> str:
        """把中文/英文地名转成 adcode（城市编码），结果带内存缓存。"""
        if use_cache and city in self._adcode_cache:
            return self._adcode_cache[city]
        data = self._get("/config/district", {"keywords": city, "subdistrict": 0})
        districts = data.get("districts") or []
        if not districts:
            raise ValueError(f"未找到城市：{city}")
        adcode = districts[0]["adcode"]
        self._adcode_cache[city] = adcode
        return adcode

    # ---------- 对外接口 ----------
    def get_live(self, city: str) -> dict:
        """实况天气：天气现象、气温、湿度、风向风力、发布时间。"""
        adcode = self.resolve_adcode(city)
        data = self._get("/weather/weatherInfo", {"city": adcode, "extensions": "base"})
        lives = data.get("lives") or [{}]
        return {"adcode": adcode, **lives[0]}

    def get_forecast(self, city: str, days: int = 4) -> list[dict]:
        """预报天气：按顺序为当天起的逐日预报，默认最多4天。"""
        adcode = self.resolve_adcode(city)
        data = self._get("/weather/weatherInfo", {"city": adcode, "extensions": "all"})
        forecasts = data.get("forecasts") or [{}]
        return forecasts[0].get("casts", [])[:days]

    def get_weather(self, city: str, forecast: bool = True, days: int = 3) -> dict:
        """组合查询：实况 + 可选的未来预报（默认3天）。"""
        result: dict = {"city": city, "live": self.get_live(city)}
        if forecast:
            result["forecast"] = self.get_forecast(city, days=days)
        return result