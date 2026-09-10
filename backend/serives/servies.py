import requests as rt

def get_walk_step(origin: str, to: str, key: str):
    url = "https://restapi.amap.com/v3/direction/walking"
    params = {
        "key": "328dce04c8af238cccf56965d1a6a2fa",                        # 请求服务权限标识（必填）
        "origin": "117.502244,40.417801",    # 出发点：经度,纬度（必填）
        "destination": "117.502244,40.417801" # 目的地：经度,纬度（必填）
    }

    response = rt.get(url, params=params, timeout=10)
    data = response.json()
    print(data)   # 查看完整返回


if __name__ == "__main__":
    get_walk_step('a', 'b', 'c')
