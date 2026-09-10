export function mockRunAgent(form) {
  const city = form.destination || '昆明'
  const days = form.days || 3
  const people = form.people || 2
  const budget = form.budget || 3000
  const style = form.style || '休闲'
  const fullPlan = form.fullPlan !== false

  const outputs = [
    { id: 'n02', node: 'n02_check', name: '参数校验', type: 'code', status: 'success', outputs: { city, days, people, budget } },
    { id: 'n03', node: 'n03_cls', name: '问题分类', type: 'question-classifier', status: 'success', outputs: { type: fullPlan ? 'PLAN' : 'SIMPLY' } },
    { id: 'n20', node: 'n20_kb', name: '景点知识检索', type: 'knowledge-retrieval', status: 'success', outputs: { hit: 6 } },
    { id: 'n21', node: 'n21_weather', name: '天气查询', type: 'http-request', status: 'success', outputs: { city } },
    { id: 'n27b', node: 'n27_budget_pre', name: '预算预分配', type: 'http-request', status: 'success', outputs: { total_budget: budget } },
    { id: 'n28', node: 'n28_planner', name: '行程 Planner', type: 'llm', status: 'success', outputs: { routes: [] } },
    { id: 'n29', node: 'n29_normalize', name: 'Plan 规范化', type: 'code', status: 'success' },
    { id: 'n30', node: 'n30_geocode', name: '批量地理编码', type: 'http-request', status: 'success' },
    { id: 'n31', node: 'n31_route', name: '逐日路线查询', type: 'iteration', status: 'success' },
    { id: 'n32', node: 'n32_budget_chk', name: '预算约束核算', type: 'code', status: 'success' },
    { id: 'n33', node: 'n33_verify', name: 'Trip Verifier', type: 'code', status: 'success', outputs: { valid: true } },
    { id: 'n34', node: 'n34_report', name: '最终报告', type: 'llm', status: 'success' }
  ]

  if (!fullPlan) {
    return {
      outputs,
      simpleMarkdown: `## ${city} 简要建议

1. ${days}天${people}人预算${budget}元,人均日约 ${Math.round(budget / people / days)} 元。
2. 推荐必去:${city === '昆明' ? '翠湖公园、滇池海埂大坝、斗南花市' : `${city} 地标景点`},拍照出片。
3. ${city} 早晚温差较大,注意带外套;高原地区注意防晒。
4. 酒店建议选市中心或主要景区附近,交通方便。`
    }
  }

  const weatherData = {
    weather_summary: [
      `当前天气:多云,气温 22°C,湿度 60%`,
      `${dateStr(1)}: 多云转阵雨,15~24°C`,
      `${dateStr(2)}: 晴,14~26°C`,
      `${dateStr(3)}: 晴转多云,13~25°C`
    ].join('\n'),
    high_risk: true,
    risky_days: [{ date: dateStr(1), weather: '多云 转 阵雨' }]
  }

  const allocation = { '住宿': Math.round(budget * 0.35), '餐饮': Math.round(budget * 0.25), '门票': Math.round(budget * 0.15), '市内交通': Math.round(budget * 0.10), '其他': Math.round(budget * 0.15) }
  const budgetStruct = {
    total_budget: budget,
    per_person: Math.round(budget / people),
    per_day: Math.round(budget / days),
    allocation,
    budget_summary: `总预算 ${budget} 元,共 ${days} 天 ${people} 人,人均 ${Math.round(budget / people)} 元,日均 ${Math.round(budget / days)} 元`
  }

  const planRoutes = cityRoutes(city, days)

  const verification = {
    valid: true,
    summary: '已逐日完成路线查询,预算未超支,未发现硬冲突。',
    errors: [],
    warnings: [
      { code: 'ROUTE_ALL_DAYS_CHECKED', message: `已查询 ${days}/${days} 天路线` },
      { code: 'PRICE_NOT_VERIFIED', message: '价格、开放时间仍需出行前复核' }
    ]
  }

  const budgetCheck = {
    estimated_total: 480,
    remaining_budget: budget - 480,
    over_budget: false,
    total_route_distance_km: 28.5,
    total_route_duration_min: 92,
    total_taxi_cost: 180
  }

  const finalMarkdown = buildMarkdown({ city, days, people, budget, style, planRoutes, weatherData, budgetStruct, verification, budgetCheck })

  return { outputs, weatherData, budgetStruct, planRoutes, verification, budgetCheck, finalMarkdown }
}

function dateStr(offset) {
  const d = new Date()
  d.setDate(d.getDate() + offset)
  return d.toISOString().slice(0, 10)
}

function cityRoutes(city, days) {
  const templates = {
    '昆明': [
      { origin: '翠湖公园', waypoints: ['文化巷', '云南省博物馆'], destination: '篆新农贸市场', ticket_total: 10, reason: '上午翠湖拍照,中午文化巷美食,下午博物馆避雨备选' },
      { origin: '海埂大坝', waypoints: ['滇池海埂公园', '西山龙门'], destination: '翠湖咖啡馆', ticket_total: 150, reason: '上午海埂观鸥,下午西山索道轻量观景' },
      { origin: '斗南花市', waypoints: ['金马碧鸡坊', '南屏街'], destination: '长水机场', ticket_total: 0, reason: '上午花市拍照伴手礼,中午金马碧鸡坊打卡,下午返程' }
    ],
    '大理': [
      { origin: '大理古城', waypoints: ['崇圣寺三塔', '海西海舌公园'], destination: '喜洲古镇', ticket_total: 120, reason: '上午古城闲逛,下午海舌拍照' },
      { origin: '双廊古镇', waypoints: ['小普陀', '南诏风情岛'], destination: '大理古城', ticket_total: 80, reason: '环海西路一日游,傍晚返回古城' }
    ],
    '成都': [
      { origin: '宽窄巷子', waypoints: ['人民公园鹤鸣茶社', '武侯祠'], destination: '锦里', ticket_total: 60, reason: '上午老城文化,下午武侯祠三国文化' },
      { origin: '大熊猫繁育研究基地', waypoints: ['东郊记忆', '建设路美食'], destination: '九眼桥酒吧街', ticket_total: 55, reason: '上午熊猫基地,下午文创园区' },
      { origin: '杜甫草堂', waypoints: ['青羊宫', '浣花溪'], destination: '春熙路太古里', ticket_total: 45, reason: '上午人文景点,下午购物美食' },
      { origin: '青城山', waypoints: ['都江堰景区'], destination: '成都东站', ticket_total: 160, reason: '全天都江堰-青城山,傍晚返程' }
    ],
    '北京': [
      { origin: '天安门广场', waypoints: ['故宫博物院', '景山公园'], destination: '南锣鼓巷', ticket_total: 60, reason: '上午天安门故宫,下午胡同文化' },
      { origin: '八达岭长城', waypoints: ['明十三陵'], destination: '鸟巢水立方', ticket_total: 160, reason: '全天长城+十三陵,傍晚看奥运建筑' },
      { origin: '颐和园', waypoints: ['圆明园遗址', '北京大学'], destination: '什刹海', ticket_total: 70, reason: '上午皇家园林,下午胡同湖畔' }
    ]
  }
  const base = templates[city] || templates['昆明']
  const routes = []
  for (let i = 0; i < Math.min(days, base.length); i++) {
    const t = base[i]
    routes.push({
      day: i + 1,
      origin: { name: t.origin },
      waypoints: t.waypoints.map(n => ({ name: n })),
      destination: { name: t.destination },
      ticket_total: t.ticket_total,
      reason: t.reason
    })
  }
  while (routes.length < days) {
    const last = routes[routes.length - 1]
    routes.push({ day: routes.length + 1, origin: { name: last.destination.name }, waypoints: [{ name: '自由活动' }], destination: { name: '酒店' }, ticket_total: 0, reason: '缓冲日,自由调整' })
  }
  return routes
}

function buildMarkdown({ city, days, people, budget, style, planRoutes, weatherData, budgetStruct, verification, budgetCheck }) {
  const routesMd = planRoutes.map(r => {
    const chain = [r.origin.name, ...r.waypoints.map(w => w.name), r.destination.name].join(' → ')
    return `### D${r.day}\n- **路线**: ${chain}\n- **门票**: ¥${r.ticket_total}/人\n- **说明**: ${r.reason}`
  }).join('\n\n')

  return `## 🧭 执行摘要
- 目的地 ${city} / ${days}天${people}人 / 总预算 ¥${budget} / 人均日 ¥${Math.round(budget / people / days)}
- 旅行风格:${style}
- 天气提示:${weatherData.high_risk ? '⚠️ 有降雨风险,备好雨具' : '天气良好'}
- 约束校验:${verification.valid ? '✅ 通过' : '⚠️ 需关注'}

## 🌤️ 天气提醒
${weatherData.weather_summary}

## 💰 预算概览
- 总预算 ¥${budgetStruct.total_budget} / 人均 ¥${budgetStruct.per_person} / 日均 ¥${budgetStruct.per_day}
- 已知费用:门票+出租车 ¥${budgetCheck.estimated_total} / 剩余 ¥${budgetCheck.remaining_budget}

## 🗺️ 每日行程
${routesMd}

## 📊 路线汇总
- 总距离 ${budgetCheck.total_route_distance_km} km · 总耗时 ${budgetCheck.total_route_duration_min} min · 出租车 ¥${budgetCheck.total_taxi_cost}

## ⚠️ 风险与提醒
${verification.warnings?.map(w => `- ${w.message}`).join('\n') || '- 价格、开放时间仍需出行前复核'}

## 📝 出发前 Checklist
- ${weatherData.high_risk ? '携带折叠伞、薄外套' : '常规防晒装备'}
- 提前预订酒店,确认空房
- 热门景点提前预约(故宫、国博、云南博物馆等)
- 高原地区注意防晒保湿,多喝水
- 交通高峰期提前出发(机场/高铁建议提前 2-3 小时)`
}
