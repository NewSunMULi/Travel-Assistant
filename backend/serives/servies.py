import requests as rt

def get_walk_step(origin: str, to: str, key: str):
    url = "https://restapi.amap.com/v3/direction/walking"
    params = {
        "key": key,               # 请求服务权限标识（必填）
        "origin": origin,         # 出发点：经度,纬度（必填）
        "destination": to,        # 目的地：经度,纬度（必填）
    }

    response = rt.get(url, params=params, timeout=10)
    data = response.json()
    print(data)   # 查看完整返回


if __name__ == "__main__":
    import os

    get_walk_step(
        "117.502244,40.417801",
        "117.502244,40.417801",
        os.environ["AMAP_KEY"],
    )
