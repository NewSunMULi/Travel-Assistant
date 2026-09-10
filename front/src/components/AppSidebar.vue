<template>
  <div class="sidebar-inner">
    <div class="sidebar-head">
      <router-link to="/" class="brand">
        <span class="brand-logo">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2a7 7 0 0 1 7 7c0 3-2 5-2 8h-2c0-3 1-5 1-6a5 5 0 1 0-10 0c0 1 1 3 1 6H4c0-3-2-5-2-8a7 7 0 0 1 10-7z" />
            <path d="M9 17h6M10 20h4" />
          </svg>
        </span>
        <span class="brand-text">
          <strong>🧭 通用旅行助手</strong>
          <small>酒店景点图片版 · 高德 API</small>
        </span>
      </router-link>
    </div>

    <nav class="sidebar-nav">
      <div class="nav-section">
        <div class="nav-section-title">工作台</div>
        <router-link to="/" class="nav-item" exact-active-class="active">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 2"/></svg>
          <span>首页 Overview</span>
        </router-link>
      </div>

      <div class="nav-section">
        <div class="nav-section-title">能力</div>
        <router-link to="/kb" class="nav-item" active-class="active">
          <span class="nav-badge">1</span>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
          <span>昆明知识库问答</span>
        </router-link>
        <router-link to="/planner" class="nav-item" active-class="active">
          <span class="nav-badge">2</span>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
          <span>通用旅行助手</span>
        </router-link>
      </div>

      <div class="nav-section">
        <div class="nav-section-title">数据源</div>
        <div class="kb-list">
          <div class="kb-item">
            <span class="kb-dot" style="background: #10a37f"></span>
            <span>昆明自建知识库</span>
            <span class="kb-count">3 KB</span>
          </div>
          <div class="kb-item">
            <span class="kb-dot" style="background: #f59e0b"></span>
            <span>高德 POI v5</span>
            <span class="kb-count">景点/酒店</span>
          </div>
          <div class="kb-item">
            <span class="kb-dot" style="background: #60a5fa"></span>
            <span>高德天气 v3</span>
            <span class="kb-count">预报</span>
          </div>
          <div class="kb-item">
            <span class="kb-dot" style="background: #a78bfa"></span>
            <span>高德路线 v5</span>
            <span class="kb-count">驾车</span>
          </div>
        </div>
      </div>
    </nav>

    <div class="sidebar-foot">
      <div class="foot-card">
        <div class="foot-card-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        </div>
        <div class="foot-card-text">
          <strong>展示具体名称 + 图片</strong>
          <small>图片待核实时不伪造</small>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup></script>

<style scoped>
.sidebar-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 16px 10px;
}

.sidebar-head {
  padding: 4px 8px 16px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 12px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: inherit;
}
.brand:hover {
  text-decoration: none;
}
.brand-logo {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
  min-width: 0;
}
.brand-text strong {
  font-size: 14px;
  color: var(--text);
  font-weight: 600;
}
.brand-text small {
  font-size: 11px;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding-right: 2px;
}
.nav-section {
  margin-bottom: 18px;
}
.nav-section-title {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  padding: 0 10px 8px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border-radius: 8px;
  font-size: 14px;
  color: var(--text-soft);
  text-decoration: none;
  transition: all var(--transition);
  margin-bottom: 2px;
  position: relative;
}
.nav-item:hover {
  background: var(--surface-2);
  color: var(--text);
  text-decoration: none;
}
.nav-item.active {
  background: var(--surface-2);
  color: var(--text);
  font-weight: 500;
}
.nav-item.active::before {
  content: '';
  position: absolute;
  left: -2px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--primary);
  border-radius: 3px;
}
.nav-item svg {
  flex-shrink: 0;
}
.nav-badge {
  width: 20px;
  height: 20px;
  border-radius: 6px;
  background: var(--primary);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kb-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.kb-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 8px;
  font-size: 13px;
  color: var(--text-soft);
  transition: background var(--transition);
}
.kb-item:hover {
  background: var(--surface-2);
}
.kb-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.kb-count {
  margin-left: auto;
  font-size: 11px;
  color: var(--muted);
  font-family: var(--mono);
}

.sidebar-foot {
  padding-top: 12px;
  border-top: 1px solid var(--border);
}
.foot-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: var(--surface-2);
  border-radius: 10px;
  border: 1px solid var(--border);
}
.foot-card-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--primary-soft);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.foot-card-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}
.foot-card-text strong {
  font-size: 12px;
  color: var(--text);
}
.foot-card-text small {
  font-size: 11px;
  color: var(--muted);
}
</style>
