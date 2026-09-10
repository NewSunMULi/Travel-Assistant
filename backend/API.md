# 高德地图服务 MCP Server — 接口文档

`backend/api.py` 基于 **FastMCP** 封装 `serives/MapSerive.py`（底层调用高德地图 Web 服务 API），
对外暴露 7 个 MCP 工具（Tool）。本服务属于《昆明智能旅行决策 Agent》的工具层，
供 Dify / Claude Desktop / 大模型 Agent 通过 MCP 协议调用。

- **传输协议**：`stdio`（本地客户端）或 `SSE`（Dify 等远程平台，地址 `http://<host>:8000/sse`）
- **依赖**：`pip install mcp requests fastmcp`
- **鉴权**：环境变量 `AMAP_KEY`（高德 **Web 服务类型** Key），未设置时调用工具会报错

---

## 1. 服务信息

| 项 | 值 |
|---|---|
| MCP Server 名称 | `amap-kunming-travel-map` |
| 启动文件 | `backend/api.py` |
| 服务封装 | `serives/MapSerive.py` 中的 `MapServices` 类 |
| 请求根域名 | `https://restapi.amap.com` |
| 超时时间 | 10 秒 |

### 启动方式

```bash
# 方式 1：stdio（本地 MCP Client / Claude Desktop）
export AMAP_KEY=你的key
python api.py

# 方式 2：SSE（供 Dify 等远程平台接入）
export AMAP_KEY=你的key
python api.py --transport sse --host 0.0.0.0 --port 8000
```

**命令行参数**

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--transport` | `stdio` | `stdio`（本地）/ `sse`（远程） |
| `--host` | `127.0.0.1` | SSE 监听地址 |
| `--port` | `8000` | SSE 监听端口 |

---

## 2. 通用说明

### 坐标格式
所有坐标统一使用 `"经度,纬度"` 字符串格式，小数点后不超过 6 位，如 `"102.712251,25.040609"`。
非法坐标会抛错；途经点列表按游览顺序传入。

### 出行方式（`mode`）
| 取值 | 含义 | 支持途经点 |
|---|---|---|
| `driving` | 驾车（返回打车费） | ✅（最多 16 个） |
| `walking` | 步行 | ✅ |
| `bicycling` | 骑车/骑行 | ❌ |

### 返回约定
- 正常返回 JSON；高德侧业务错误（`status != "1"`）时抛出 `AmapAPIError`。
- 工具层多数方法在捕获异常后返回 `{"found": False, "error": ...}` 或 `None` 字段，不直接中断。

### 常用 POI 分类码（`types`）
| 分类 | 码值 |
|---|---|
| 餐饮服务 | `050000` |
| 住宿服务 | `100000` |
| 风景名胜 | `110000` |
| 购物服务 | `060000` |
| 交通设施 | `150000` |

---

## 3. 工具接口总览

| # | 工具名 | 对应需求 | 功能 |
|---|---|---|---|
| 1 | `geocode_address` | 节点4 Tool2 | 文字地址 → 经纬度 |
| 2 | `batch_geocode_addresses` | 阶段1 KB1 | 批量文字地址 → 经纬度 |
| 3 | `reverse_geocode` | 备用 | 经纬度 → 结构化地址 |
| 4 | `plan_route` | 节点4 Tool2 / Verifier | 两点路径规划（驾车/步行/骑车） |
| 5 | `plan_route_multi` | Verifier / Demo | 多途经点路线串联 |
| 6 | `estimate_taxi_cost` | 节点4 Tool3 | 打车费估算（预算计算器） |
| 7 | `recommend_restaurants` | 节点4 Tool4 | 周边餐厅推荐（餐厅 Agent） |
| 8 | `recommend_travel_spots` | Demo | 地点 → 旅游景点推荐 |

> 注：下方接口参数均基于 `api.py` 对外暴露的工具签名整理。

---

## 4. 接口详情

### 4.1 `geocode_address` — 地理编码（地址 → 坐标）

定位景点/餐厅/酒店、路径规划前坐标准备、知识库"位置"字段填充。

**参数**

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `address` | string | ✅ | — | 结构化地址，如 `"云南省昆明市五华区翠湖公园"` 或 `"翠湖公园"` |
| `city` | string | ❌ | `null` | 限定城市，如 `"昆明"` 或 `"530100"`，提高匹配精度 |

**返回**

```json
{
  "found": true,
  "address": "昆明市翠湖公园",
  "location": "102.708615,25.054831",
  "province": "云南省",
  "city": "昆明市",
  "district": "五华区",
  "adcode": "530102",
  "level": "风景区"
}
```

| 字段 | 说明 |
|---|---|
| `found` | 是否匹配成功 |
| `location` | `"经度,纬度"`；无匹配为 `null` |
| `province/city/district/adcode/level` | 地址要素（仅匹配成功返回） |

无匹配：`{"found": false, "address": "...", "location": null}`；
异常：`{"found": false, "error": "<异常信息>"}`。

---

### 4.2 `batch_geocode_addresses` — 批量地理编码

阶段1 KB1 景区知识库"位置"字段批量填充。单条失败不影响其他条目。

**参数**

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `addresses` | string[] | ✅ | — | 地址列表，如 `["昆明市翠湖公园", "滇池海埂大坝", "石林风景区"]` |
| `city` | string | ❌ | `null` | 统一限定城市（可选） |

**返回** — 与输入等长的列表，每项：
```json
{
  "address": "昆明市翠湖公园",
  "location": "102.708615,25.054831",
  "detail": { "location": "...", "city": "昆明市", "adcode": "530100", "...": "..." }
}
```
单条失败时 `location`、`detail` 为 `null`，并追加 `error` 字段。

---

### 4.3 `reverse_geocode` — 逆地理编码（坐标 → 地址）

备用：当前位置解析、坐标可读化。

**参数**

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `location` | string | ✅ | — | 坐标 `"经度,纬度"`，如 `"102.712251,25.040609"` |

**返回** — `regeocode` 对象：
```json
{
  "addressComponent": {
    "province": "云南省", "city": "昆明市", "district": "五华区",
    "streetNumber": { "street": "翠湖南路", "number": "6号" }
  },
  "formatted_address": "云南省昆明市五华区翠湖南路6号"
}
```

---

### 4.4 `plan_route` — 两点路径规划

景点间通勤时间估算（Verifier 时间冲突校验）、交通建议、体力强度评估（步行距离）。

**参数**

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `origin` | string | ✅ | — | 出发点坐标 `"经度,纬度"` |
| `destination` | string | ✅ | — | 目的地坐标 `"经度,纬度"` |
| `mode` | string | ❌ | `driving` | `driving` / `walking` / `bicycling` |

**返回**
```json
{
  "mode": "driving",
  "distance": 12500,
  "duration": 1800,
  "distance_km": 12.5,
  "duration_min": 30.0,
  "taxi_cost": 35.0,
  "steps": [
    { "instruction": "沿XX路行驶500米", "distance": 500, "road": "翠湖北路" }
  ]
}
```

| 字段 | 说明 |
|---|---|
| `distance` / `duration` | 总距离（米）/ 总耗时（秒） |
| `distance_km` / `duration_min` | 距离（公里）/ 耗时（分钟，保留 1 位小数） |
| `taxi_cost` | 预估打车费（元），**仅 `driving` 返回**，其他方式为 `null` |
| `steps` | 分路段指引 `[{instruction, distance, road}]` |

---

### 4.5 `plan_route_multi` — 多途经点路线规划

把一天多个景点按顺序串联成一条线。用于 Demo "Day2 滇池→海埂大坝→西山"、
Verifier 校验全天总耗时/总里程、防止 AI 把路线排反。

**参数**

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `origin` | string | ✅ | — | 出发点坐标 |
| `destination` | string | ✅ | — | 终点坐标 |
| `waypoints` | string[] | ✅ | — | 途经点坐标列表（按游览顺序），如 `["102.671859,24.974336"]`；不能为空，驾车最多 16 个 |
| `mode` | string | ❌ | `driving` | 仅 `driving` / `walking`（骑车不支持途经点） |

**返回** — 与 `plan_route` 结构一致，另含 `legs`：
```json
{
  "mode": "driving",
  "waypoints": ["102.671859,24.974336"],
  "distance": 20000,
  "duration": 3000,
  "distance_km": 20.0,
  "duration_min": 50.0,
  "taxi_cost": 45.0,
  "legs": [
    { "distance": 8000, "duration": 1200 },
    { "distance": 12000, "duration": 1800 }
  ],
  "steps": []
}
```

> `legs` 为每段子路线（出发点→途经点→…→终点）的距离/耗时明细，便于 Verifier 检查单段耗时。

---

### 4.6 `estimate_taxi_cost` — 打车费估算

预算计算器的交通费来源。内部调用驾车 `plan_route`，仅返回三项精简字段。

**参数**

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `origin` | string | ✅ | — | 出发点坐标 |
| `destination` | string | ✅ | — | 目的地坐标 |

**返回**
```json
{ "taxi_cost": 35.0, "distance_km": 12.5, "duration_min": 30.0 }
```

---

### 4.7 `recommend_restaurants` — 周边餐厅推荐

餐厅推荐 Agent 数据源；输出可直接组装为 `餐厅 | 距离 | 人均 | 评分` 表格。

**参数**

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `location` | string | ✅ | — | 中心点坐标（景点/酒店） |
| `radius` | int | ❌ | `2000` | 搜索半径（米） |
| `keyword` | string | ❌ | `null` | 口味关键词，如 `"云南菜"` / `"米线"` / `"火锅"` |
| `size` | int | ❌ | `10` | 返回条数 |

**返回** — 餐厅列表：
```json
[
  {
    "name": "桥香园过桥米线",
    "distance": 350,
    "distance_km": 0.35,
    "cost": 32,
    "rating": "4.3",
    "address": "昆明市五华区翠湖南路",
    "location": "102.708615,25.054831",
    "tel": "0871-12345678"
  }
]
```

> `distance` 为距中心点（米）；`cost` 为人均消费（元）；`distance_km` 保留 2 位小数。

---

### 4.8 `recommend_travel_spots` — 旅游景点推荐

输入城市/地区名，推荐当地景点。用于行程候选景点调研（Planner Agent）、RAG 之外的实时 POI 补充。
实现：先把 `place` 地理编码解析出城市 adcode，再在城市内做关键字 POI 搜索。

**参数**

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `place` | string | ✅ | — | 地点名，如 `"昆明"` / `"大理古城"` |
| `keyword` | string | ❌ | `"景点"` | 搜索词，可换 `"美食"` / `"公园"` / `"博物馆"` |
| `size` | int | ❌ | `10` | 返回条数（底层上限 25） |

**返回**
```json
{
  "place": "昆明",
  "city": "昆明市",
  "adcode": "530100",
  "count": "83",
  "pois": [
    {
      "name": "翠湖公园",
      "type": "风景名胜;风景名胜;公园广场",
      "address": "昆明市五华区翠湖南路",
      "location": "102.708615,25.054831",
      "tel": "0871-65312342",
      "rating": "4.5",
      "cost": null
    }
  ]
}
```

| 字段 | 说明 |
|---|---|
| `place` | 查询地点 |
| `city` | 解析到的城市名 |
| `adcode` | 城市区域编码（解析失败为 `null`） |
| `count` | 服务端匹配总数（字符串） |
| `pois` | 推荐列表，每项含 `name/type/address/location/tel/rating/cost` |

---

## 5. Dify 接入指引

1. 启动服务（SSE 方式）：`export AMAP_KEY=你的key && python api.py --transport sse --host 0.0.0.0 --port 8000`
2. Dify 1.x → **设置 → 工具 → 添加 MCP 服务器 → 选择 SSE**
3. 填写 `http://<主机IP>:8000/sse`
4. 在 Agent 节点中选择 `amap-kunming-travel-map`，即可调用上述 8 个工具。

---

## 6. 常见错误

| 场景 | 表现 |
|---|---|
| 未设置 `AMAP_KEY` | 启动打印警告；调用工具报错 |
| 高德返回业务错误（如 INVALID_USER_KEY / 参数错误） | 抛出 `AmapAPIError`，含 `info` 与 `infocode` |
| 坐标格式非法 / 出行方式不支持 / waypoints 为空 | 抛出 `ValueError` |
| 地址无法解析坐标 | `geocode_address` 返回 `found: false`；`MapServices.get_location` 抛 `ValueError` |
