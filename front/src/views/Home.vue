<template>
  <div class="home">
    <!-- Hero -->
    <section class="hero">
      <div class="hero-bg"></div>
      <div class="hero-inner">
        <div class="hero-badge">
          <span class="pulse"></span>
          Dify + RAG + Human-in-the-loop
        </div>
        <h1>昆明智能旅行决策 Agent</h1>
        <p class="hero-sub">
          像旅行顾问一样:先调研、再规划、再让你确认,最后给出能执行的方案。
          不是"帮你写攻略",而是融合 RAG、工具调用与人机协同的个性化旅行规划系统。
        </p>
        <div class="hero-actions">
          <router-link to="/planner" class="btn primary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
            开始智能规划
          </router-link>
          <router-link to="/kb" class="btn ghost">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            浏览知识库
          </router-link>
        </div>
      </div>
    </section>

    <!-- 对比 -->
    <section class="card compare">
      <div class="section-title"><span class="dot"></span><h2>为什么不是普通旅游助手</h2></div>
      <div class="compare-grid">
        <div class="compare-col compare-bad">
          <div class="col-head">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
            <h3>普通助手</h3>
          </div>
          <div class="flow-mini">
            <span>用户输入地点</span>
            <span class="arrow">↓</span>
            <span>LLM 直接生成攻略</span>
          </div>
          <p class="muted">无来源 · 无约束 · 无校验 · 易幻觉</p>
        </div>
        <div class="compare-col compare-good">
          <div class="col-head">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <h3>本系统</h3>
          </div>
          <div class="flow-mini">
            <span>用户输入需求</span>
            <span class="arrow">↓</span>
            <span>Agent 分析目标与约束</span>
            <span class="arrow">↓</span>
            <span>调研 RAG + 天气 + 地图 + 美食</span>
            <span class="arrow">↓</span>
            <span>规划候选方案 → 校验</span>
            <span class="arrow">↓</span>
            <span>人工审核 → 重规划</span>
            <span class="arrow">↓</span>
            <span class="highlight">输出可执行方案</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 两阶段 -->
    <section class="grid-2">
      <router-link to="/kb" class="card stage-card clickable">
        <div class="stage-head">
          <span class="tag primary">阶段 1</span>
          <svg class="arrow-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
        </div>
        <h3>RAG + LLM + 昆明知识底座</h3>
        <ul class="stage-list">
          <li><strong>KB1</strong> 景区卡 {{ attractions.length }} 张 · 天气/体力标签</li>
          <li><strong>KB2</strong> 美食卡 {{ foods.length }} 张</li>
          <li><strong>KB3</strong> 避坑 FAQ {{ pitfalls.length }} 条</li>
          <li>向量索引 + BM25 混合检索</li>
          <li>回答带引用 · 不足则拒答</li>
        </ul>
      </router-link>
      <router-link to="/planner" class="card stage-card clickable">
        <div class="stage-head">
          <span class="tag purple">阶段 2</span>
          <svg class="arrow-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
        </div>
        <h3>多 Agent 协同 + 人机协同</h3>
        <ul class="stage-list">
          <li>需求采集 → Planner Agent 拆解</li>
          <li>Router 路由 RAG/天气/地图/餐厅/预算</li>
          <li>Verifier 校验预算/时间/天气/体力</li>
          <li>Human Review Node 审核闭环</li>
          <li>Report Generator 输出 + 导出</li>
        </ul>
      </router-link>
    </section>

    <!-- 创新点 -->
    <section class="card">
      <div class="section-title"><span class="dot" style="background: var(--purple)"></span><h2>四个创新点</h2></div>
      <div class="innov-grid">
        <div class="innov">
          <span class="innov-no">01</span>
          <h4>多 Agent 协同</h4>
          <p class="muted">需求分析 / 规划 / 餐厅 / 报告生成 Agent 分工明确,体现任务拆解能力。</p>
        </div>
        <div class="innov">
          <span class="innov-no">02</span>
          <h4>约束感知规划</h4>
          <p class="muted">显式建模预算、天气、时间、体力、返程,让方案"能落地"。</p>
        </div>
        <div class="innov">
          <span class="innov-no">03</span>
          <h4>人机协同</h4>
          <p class="muted">AI 初稿 → 人工修改 → 系统重规划,兼顾智能与可控。</p>
        </div>
        <div class="innov">
          <span class="innov-no">04</span>
          <h4>RAG 知识治理</h4>
          <p class="muted">景区/美食/避坑卡 + 标签 + 来源引用,可信可追溯。</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { attractions } from '@/data/attractions.js'
import { foods } from '@/data/foods.js'
import { pitfalls } from '@/data/pitfalls.js'
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ---------- Hero ---------- */
.hero {
  position: relative;
  border-radius: var(--radius-xl);
  padding: 48px 36px;
  overflow: hidden;
  background: linear-gradient(135deg, #10a37f 0%, #0d8a6b 40%, #6c5ce7 100%);
  box-shadow: var(--shadow-lg);
}
.hero-bg {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 80%, rgba(255,255,255,0.12) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255,255,255,0.08) 0%, transparent 40%);
  pointer-events: none;
}
.hero-inner {
  position: relative;
  max-width: 760px;
  color: #fff;
}
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 14px 5px 8px;
  border-radius: 999px;
  background: rgba(255,255,255,0.18);
  backdrop-filter: blur(6px);
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 18px;
  border: 1px solid rgba(255,255,255,0.25);
}
.pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #fff;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.3); }
}
.hero h1 {
  color: #fff;
  font-size: 40px;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-bottom: 14px;
}
.hero-sub {
  font-size: 15.5px;
  line-height: 1.85;
  color: rgba(255,255,255,0.9);
  margin-bottom: 26px;
}
.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.hero-actions .btn {
  background: #fff;
  color: var(--primary);
  border-color: #fff;
  padding: 10px 20px;
}
.hero-actions .btn.primary {
  background: #fff;
  color: var(--primary);
}
.hero-actions .btn:hover {
  background: rgba(255,255,255,0.9);
  transform: translateY(-1px);
}
.hero-actions .btn.ghost {
  background: transparent;
  color: #fff;
  border-color: rgba(255,255,255,0.5);
}
.hero-actions .btn.ghost:hover {
  background: rgba(255,255,255,0.15);
  color: #fff;
}

/* ---------- Compare ---------- */
.compare-grid {
  display: grid;
  grid-template-columns: 1fr 1.4fr;
  gap: 16px;
}
@media (max-width: 760px) {
  .compare-grid { grid-template-columns: 1fr; }
}
.compare-col {
  padding: 18px 18px 14px;
  border-radius: var(--radius);
}
.col-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.col-head h3 {
  margin: 0;
  font-size: 15px;
}
.compare-bad {
  background: var(--surface-2);
  border: 1px dashed var(--border-strong);
  color: var(--muted);
}
.compare-bad h3 { color: var(--text-soft); }
.compare-good {
  background: var(--primary-soft);
  border: 1px solid transparent;
  color: var(--text);
}
.flow-mini {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 10px 0;
  font-size: 13px;
}
.flow-mini span {
  background: var(--surface);
  padding: 7px 12px;
  border-radius: 8px;
  border: 1px solid var(--border);
  text-align: center;
}
.compare-bad .flow-mini span {
  background: var(--surface-3);
  border-color: transparent;
  color: var(--muted);
}
.flow-mini .arrow {
  background: transparent;
  border: none;
  padding: 0;
  color: var(--muted);
  font-size: 12px;
}
.flow-mini .highlight {
  background: var(--primary);
  color: #fff;
  font-weight: 600;
  border-color: transparent;
}

/* ---------- Stage Cards ---------- */
.stage-card.clickable {
  display: flex;
  flex-direction: column;
  gap: 12px;
  color: inherit;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}
.stage-card.clickable:hover {
  text-decoration: none;
  border-color: var(--primary);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}
.stage-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.arrow-icon {
  color: var(--muted);
  transition: transform var(--transition), color var(--transition);
}
.stage-card.clickable:hover .arrow-icon {
  color: var(--primary);
  transform: translateX(4px);
}
.stage-card h3 {
  font-size: 16px;
}
.stage-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 13.5px;
  color: var(--text-soft);
}
.stage-list li {
  padding-left: 16px;
  position: relative;
}
.stage-list li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 9px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--primary);
  opacity: 0.6;
}

/* ---------- Innov ---------- */
.innov-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}
@media (max-width: 760px) {
  .innov-grid { grid-template-columns: 1fr; }
}
.innov {
  padding: 18px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface-2);
  transition: border-color var(--transition), transform var(--transition);
}
.innov:hover {
  border-color: var(--border-strong);
  transform: translateY(-1px);
}
.innov-no {
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 700;
  color: var(--primary);
  letter-spacing: 0.05em;
}
.innov h4 {
  margin: 6px 0;
  font-size: 15px;
}
.innov p {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
}
</style>
