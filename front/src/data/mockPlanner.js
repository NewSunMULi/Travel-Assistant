const img = (prompt, size = 'landscape_4_3') =>
  `https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent(prompt)}&image_size=${size}`

export const defaultForm = {
  destination: '昆明',
  departure: '成都',
  days: 3,
  people: 2,
  budget: 3000,
  style: '休闲',
  special_request: '帮我安排完整行程'
}

export const paramCheck = {
  city: '昆明',
  days: 3,
  people: 2,
  budget: 3000,
  style: '休闲',
  special_request: '帮我安排完整行程',
  kb_query: '昆明 休闲 热门景点 美食餐厅 避坑注意事项',
  cls_query: '旅行风格：休闲；需求描述：帮我安排完整行程；天数：3天'
}

export const classifierResult = {
  type: '完整规划',
  label: 'n2 完整规划',
  reason: '用户明确要求"帮我安排完整行程",需要逐日行程安排、预算分配和路线规划。'
}

export const sourceAgg = {
  source: '昆明自建知识库 + 高德地图 API',
  kb_hits: 6,
  kb_citations: ['KM-SPOT-001', 'KM-SPOT-002', 'KM-FOOD-003', 'KM-FOOD-007', 'KM-PIT-002', 'KM-PIT-009']
}

export const weatherResult = {
  status: 'success',
  city: '昆明',
  forecasts: [
    {
      city: '昆明市',
      adcode: '530100',
      province: '云南',
      reporttime: '2026-09-10 08:00:00',
      casts: [
        {
          date: '2026-10-01',
          week: '星期四',
          dayweather: '多云',
          nightweather: '阵雨',
          daytemp: '24',
          nighttemp: '15',
          daywind: '东南',
          daypower: '3',
          nightwind: '东南',
          nightpower: '2'
        },
        {
          date: '2026-10-02',
          week: '星期五',
          dayweather: '晴',
          nightweather: '晴',
          daytemp: '26',
          nighttemp: '14',
          daywind: '西南',
          daypower: '2',
          nightwind: '西南',
          nightpower: '1'
        },
        {
          date: '2026-10-03',
          week: '星期六',
          dayweather: '晴',
          nightweather: '多云',
          daytemp: '25',
          nighttemp: '13',
          daywind: '西',
          daypower: '2',
          nightwind: '西',
          nightpower: '1'
        }
      ]
    }
  ]
}

export const spotsResult = {
  status: 'success',
  pois: [
    { name: '翠湖公园', address: '昆明市五华区翠湖南路', location: '102.7001,25.0456', business: { rating: 4.7 }, photos: [{ url: img('翠湖公园 昆明 红嘴鸥 湖景') }] },
    { name: '滇池海埂公园', address: '昆明市西山区滇池路1318号', location: '102.6412,24.8583', business: { rating: 4.6 }, photos: [{ url: img('滇池海埂公园 昆明 湖光山色') }] },
    { name: '西山龙门景区', address: '昆明市西山区西山森林公园内', location: '102.6001,24.9123', business: { rating: 4.5 }, photos: [{ url: img('西山龙门 昆明 悬崖 俯瞰滇池') }] },
    { name: '斗南花市', address: '昆明市呈贡区兴呈路', location: '102.8456,24.8833', business: { rating: 4.8 }, photos: [{ url: img('斗南花市 昆明 鲜花 色彩斑斓') }] },
    { name: '金马碧鸡坊', address: '昆明市五华区金碧路', location: '102.7123,25.0389', business: { rating: 4.4 }, photos: [{ url: img('金马碧鸡坊 昆明 地标建筑 夜景') }] },
    { name: '云南省博物馆', address: '昆明市官渡区广福路6393号', location: '102.7345,24.9812', business: { rating: 4.5 }, photos: [{ url: img('云南省博物馆 现代建筑') }] }
  ]
}

export const hotelsResult = {
  status: 'success',
  pois: [
    { name: '昆明翠湖宾馆', address: '昆明市五华区翠湖南路6号', location: '102.7012,25.0467', business: { rating: 4.6 }, photos: [{ url: img('昆明翠湖宾馆 豪华酒店 湖景房') }] },
    { name: '昆明中心皇冠假日酒店', address: '昆明市盘龙区北京路118号', location: '102.7156,25.0533', business: { rating: 4.5 }, photos: [{ url: img('昆明中心皇冠假日酒店 商务酒店') }] },
    { name: '昆明索菲特大酒店', address: '昆明市官渡区彩云路1688号', location: '102.7623,25.0211', business: { rating: 4.4 }, photos: [{ url: img('昆明索菲特大酒店 五星级酒店') }] },
    { name: '昆明洲际酒店', address: '昆明市西山区滇池度假区怡景路9号', location: '102.6389,24.8612', business: { rating: 4.7 }, photos: [{ url: img('昆明洲际酒店 度假酒店 滇池景') }] },
    { name: '昆明悦榕庄', address: '昆明市官渡区昌宏西路', location: '102.7834,24.9890', business: { rating: 4.3 }, photos: [{ url: '图片待核实' }] },
    { name: '昆明君悦酒店', address: '昆明市盘龙区东风东路', location: '102.7211,25.0445', business: { rating: 4.2 }, photos: [{ url: '图片待核实' }] }
  ]
}

export const routeResult = {
  status: 'success',
  origin: '102.7001,25.0456',
  destination: '102.6412,24.8583',
  route_info: '翠湖公园 → 滇池海埂公园: 全程约12公里,驾车约35分钟,公交44路直达',
  duration: '35分钟',
  distance: '12公里'
}

export const mediaResult = {
  spots: spotsResult.pois.map(p => ({
    name: p.name,
    address: p.address,
    rating: (p.business && p.business.rating) || '评分待核实',
    image_url: p.photos && p.photos.length ? p.photos[0].url : '图片待核实'
  })),
  hotels: hotelsResult.pois.map(p => ({
    name: p.name,
    address: p.address,
    rating: (p.business && p.business.rating) || '评分待核实',
    image_url: p.photos && p.photos.length ? p.photos[0].url : '图片待核实'
  }))
}

export const budgetResult = {
  status: 'estimated',
  total_budget: 3000,
  days: 3,
  display_days: 3,
  people: 2,
  per_day_total: 1000,
  per_person_per_day: 500,
  daily_budget: [
    { day: 'D1', day_budget_total: 1000, per_person_budget: 500, suggested_allocation: { '住宿': 350, '餐饮': 250, '门票活动': 150, '市内交通': 100, '机动': 150 } },
    { day: 'D2', day_budget_total: 1000, per_person_budget: 500, suggested_allocation: { '住宿': 350, '餐饮': 250, '门票活动': 150, '市内交通': 100, '机动': 150 } },
    { day: 'D3', day_budget_total: 1000, per_person_budget: 500, suggested_allocation: { '住宿': 350, '餐饮': 250, '门票活动': 150, '市内交通': 100, '机动': 150 } }
  ],
  allocation: { '住宿估算': 1050, '餐饮估算': 750, '门票活动估算': 450, '市内交通估算': 300, '机动费用估算': 450 },
  note: '预算为规则估算,不含实时酒店、车票和门票价格;具体价格仍需核实。'
}

export const checkResult = {
  status: 'checked',
  days: 3,
  people: 2,
  budget_total: 3000,
  per_person_per_day: 500,
  warnings: [
    '路线耗时未完全核实,行程需预留交通缓冲',
    '预算、路线和天气未发现明显硬冲突,但价格和开放时间仍需出行前复核'
  ]
}

export const dailyWeatherBudget = {
  display_days: 3,
  note: '最终方案最多展开3天;天气来自高德可用预报,缺失日期标待核实。',
  daily_weather: [
    { day: 'D1', date: '2026-10-01', weather: '多云/阵雨', temperature: '15-24℃', wind: '东南风 3级' },
    { day: 'D2', date: '2026-10-02', weather: '晴/晴', temperature: '14-26℃', wind: '西南风 2级' },
    { day: 'D3', date: '2026-10-03', weather: '晴/多云', temperature: '13-25℃', wind: '西风 2级' }
  ],
  daily_budget: budgetResult.daily_budget
}

export const reasonText = '1) 目的地昆明,命中自建知识库,资料来源以本地经验为主,辅以高德 POI 和天气数据;2) 景点取舍优先选择游客高频打卡且距离较近的翠湖、滇池、海埂、斗南;酒店优先选择翠湖附近和滇池度假区;3) 风险点:Day1 下午有阵雨,户外行程需准备雨具;价格均待出行前核实。'

export const finalMarkdown = `## ① 需求摘要
- 目的地:昆明 / 天数:3天 / 人数:2人 / 总预算:3000元
- 风格:休闲 / 需求:帮我安排完整行程

## ② 规划依据
${reasonText}

## ③ 推荐酒店
- **昆明翠湖宾馆**: 五华区翠湖南路6号 · 评分 4.6 · 图片待核实
- **昆明洲际酒店**: 西山区滇池度假区 · 评分 4.7 · 图片待核实
- **昆明索菲特大酒店**: 官渡区彩云路 · 评分 4.4 · 图片待核实

## ④ 每日行程

### D1 · 10月1日(多云转阵雨)
| 时段 | 安排 |
|---|---|
| 上午 | 翠湖公园(红嘴鸥+拍照) |
| 中午 | 文化巷 + 建新园米线 |
| 下午 | 云南省博物馆(室内备选,避雨) |
| 晚上 | 篆新豆花米线 + 南屏街夜市 |

### D2 · 10月2日(晴)
| 时段 | 安排 |
|---|---|
| 上午 | 海埂大坝 + 滇池海埂公园 |
| 中午 | 菌王府野生菌火锅 |
| 下午 | 西山龙门索道(轻量观景) |
| 晚上 | 翠湖咖啡馆下午茶 |

### D3 · 10月3日(晴)
| 时段 | 安排 |
|---|---|
| 上午 | 斗南花市(拍照+伴手礼) |
| 中午 | 金马碧鸡坊打卡 |
| 下午 | 返程(长水机场,提前3小时) |
| 晚上 | — |

## ⑤ 每日天气与预算
| 天 | 天气 | 温度 | 预算 |
|---|---|---|---|
| D1 | 多云/阵雨 | 15-24℃ | 1000元 |
| D2 | 晴/晴 | 14-26℃ | 1000元 |
| D3 | 晴/多云 | 13-25℃ | 1000元 |

## ⑥ 待核实
- 酒店价格、空房情况需出行前确认
- 门票价格、开放时间以高德为准
- Day1下午阵雨,户外行程备折叠伞
- 长水机场国庆高峰,建议提前4小时出发`

export const finalItinerary = [
  {
    day: 'D1',
    date: '2026-10-01',
    weather: '多云/阵雨',
    temperature: '15-24℃',
    wind: '东南风 3级',
    budget: 1000,
    morning: { place: '翠湖公园', note: '红嘴鸥+拍照', spot: mediaResult.spots[0] },
    noon: { place: '文化巷 + 建新园米线', note: '本地老字号' },
    afternoon: { place: '云南省博物馆', note: '室内避雨备选', spot: mediaResult.spots[5] },
    evening: { place: '篆新豆花米线 + 南屏街夜市', note: '本地小吃' }
  },
  {
    day: 'D2',
    date: '2026-10-02',
    weather: '晴/晴',
    temperature: '14-26℃',
    wind: '西南风 2级',
    budget: 1000,
    morning: { place: '海埂大坝 + 滇池海埂公园', note: '观鸥+湖景', spot: mediaResult.spots[1] },
    noon: { place: '菌王府野生菌火锅', note: '雨季正季' },
    afternoon: { place: '西山龙门索道', note: '轻量观景', spot: mediaResult.spots[2] },
    evening: { place: '翠湖咖啡馆下午茶', note: '休闲放松' }
  },
  {
    day: 'D3',
    date: '2026-10-03',
    weather: '晴/多云',
    temperature: '13-25℃',
    wind: '西风 2级',
    budget: 1000,
    morning: { place: '斗南花市', note: '拍照+伴手礼', spot: mediaResult.spots[3] },
    noon: { place: '金马碧鸡坊', note: '市区地标', spot: mediaResult.spots[4] },
    afternoon: { place: '返程(长水机场)', note: '提前3小时' },
    evening: { place: '—', note: '已返程' }
  }
]

export const toolCalls = [
  { id: 'n02', node: 'n02_check', name: '参数校验', type: 'code', status: 'success', duration: '<0.1s', output: paramCheck },
  { id: 'n03', node: 'n03_cls', name: '需求分类', type: 'question-classifier', status: 'success', duration: '1.2s', output: classifierResult },
  { id: 'n20', node: 'n20_kb', name: '知识库检索', type: 'knowledge-retrieval', status: 'success', duration: '0.8s', output: sourceAgg },
  { id: 'n21', node: 'n21_weather', name: '天气查询', type: 'http-request', status: 'success', duration: '0.4s', output: weatherResult, api: '高德 v3 weatherInfo' },
  { id: 'n22', node: 'n22_spots', name: '景点推荐', type: 'http-request', status: 'success', duration: '0.5s', output: spotsResult, api: '高德 v5 place/text' },
  { id: 'n22h', node: 'n22_hotels', name: '酒店推荐', type: 'http-request', status: 'success', duration: '0.6s', output: hotelsResult, api: '高德 v5 place/text' },
  { id: 'n22m', node: 'n22_media', name: '景点酒店图片整理', type: 'code', status: 'success', duration: '<0.1s', output: mediaResult },
  { id: 'n25', node: 'n25_route', name: '路线规划', type: 'http-request', status: 'success', duration: '0.3s', output: routeResult, api: '高德 v5 direction/driving' },
  { id: 'n27', node: 'n27_budget', name: '预算分配', type: 'code', status: 'success', duration: '<0.1s', output: budgetResult },
  { id: 'n27c', node: 'n27_check', name: '约束检查', type: 'code', status: 'success', duration: '<0.1s', output: checkResult },
  { id: 'n28', node: 'n28_plan_llm', name: '最终方案生成', type: 'llm', status: 'success', duration: '2.1s', output: finalMarkdown }
]

export const flowSteps = [
  { key: 'start', name: '用户输入', node: 's_start', icon: '🧭', desc: 'destination / departure / days / people / budget / style / special_request' },
  { key: 'check', name: '参数校验', node: 'n02_check', icon: '✅', desc: '规范化输入,生成 kb_query & cls_query' },
  { key: 'cls', name: '需求分类', node: 'n03_cls', icon: '🔀', desc: '简要建议 / 完整规划' },
  { key: 'route_check', name: '城市判断', node: 'n04_city_if', icon: '🏛️', desc: '昆明→知识库 / 其他→通用调研' },
  { key: 'kb', name: '资料获取', node: 'n20', icon: '📚', desc: '知识库检索 or 通用调研' },
  { key: 'weather', name: '天气查询', node: 'n21_weather', icon: '☁️', desc: '高德 v3 weatherInfo API' },
  { key: 'spots', name: '景点推荐', node: 'n22_spots', icon: '🏖️', desc: '高德 v5 place/text API' },
  { key: 'hotels', name: '酒店推荐', node: 'n22_hotels', icon: '🏨', desc: '高德 v5 place/text API' },
  { key: 'media', name: '图片整理', node: 'n22_media', icon: '🖼️', desc: '提取 spots/hotels 卡片(名称+地址+评分+图片)' },
  { key: 'route', name: '路线规划', node: 'n25_route', icon: '🛣️', desc: '高德 direction/driving' },
  { key: 'budget', name: '预算分配', node: 'n27_budget', icon: '💰', desc: '住宿35% / 餐饮25% / 门票15% / 交通10% / 机动15%' },
  { key: 'daily', name: '每日天气预算', node: 'n27_daily', icon: '📅', desc: '整理最多3天 daily_weather + daily_budget' },
  { key: 'plan', name: '最终方案生成', node: 'n28_plan_llm', icon: '✍️', desc: 'LLM 输出 Markdown 方案(含图片)' },
  { key: 'end', name: '输出', node: 'n99_end', icon: '🎯', desc: 'n30_agg 合并后返回' }
]

export const simpleAdvice = `## 昆明简要建议

1. 3天2人预算3000元,人均日500元,预算充足。
2. 推荐必去:翠湖公园、滇池海埂大坝、斗南花市,拍照出片。
3. 美食优先:建新园米线、菌王府野生菌(需煮20分钟以上)、篆新豆花米线。
4. 高原紫外线强,全程 SPF50+;10月温差大,带薄外套。
5. 酒店建议选翠湖或滇池度假区附近,交通方便。`
