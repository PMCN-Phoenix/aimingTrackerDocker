// 游戏感悟 API 服务
const BASE_URL = 'http://127.0.0.1:8000/api'

// 通用请求封装
async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  const json = await res.json()
  if (json.code !== 0) {
    throw new Error(json.message || '请求失败')
  }
  return json
}

// 获取感悟列表
export async function getGameReflections(params = {}) {
  const query = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      query.append(key, value)
    }
  })
  const queryString = query.toString()
  return request(`/game-reflections${queryString ? `?${queryString}` : ''}`)
}

// 获取单条感悟
export async function getGameReflection(id) {
  return request(`/game-reflections/${encodeURIComponent(id)}`)
}

// 创建感悟
export async function createGameReflection(payload) {
  return request('/game-reflections', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

// 更新感悟
export async function updateGameReflection(id, payload) {
  return request(`/game-reflections/${encodeURIComponent(id)}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

// 删除感悟
export async function deleteGameReflection(id) {
  return request(`/game-reflections/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  })
}

// 获取感悟统计
export async function getGameReflectionStats() {
  return request('/game-reflections/stats')
}

// 获取热身项目列表
export async function getWarmupItems() {
  return request('/warmup-items')
}

// 创建热身项目
export async function createWarmupItem(payload) {
  return request('/warmup-items', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

// 获取某个热身项目的感悟
export async function getWarmupItemReflections(itemName) {
  return request(`/warmup-items/${encodeURIComponent(itemName)}/reflections`)
}

// Markdown 相关
export async function getMarkdownDates() {
  return request('/game-reflections/markdown/dates')
}

export async function getMarkdownReflections(date) {
  return request(`/game-reflections/markdown/${encodeURIComponent(date)}`)
}

export async function importFromMarkdown() {
  return request('/game-reflections/markdown/import', { method: 'POST' })
}

export async function exportToMarkdown() {
  return request('/game-reflections/markdown/export', { method: 'POST' })
}

// 主题配置
export const THEME_CONFIG = {
  warmup: { name: '热身', icon: '🔥', color: '#ef4444' },
  aim: { name: '对枪/瞄准', icon: '🎯', color: '#3b82f6' },
  move: { name: '身法/移动', icon: '🏃', color: '#10b981' },
  mind: { name: '意识/决策', icon: '🧠', color: '#8b5cf6' },
  map: { name: '地图理解', icon: '🗺️', color: '#f59e0b' },
  agent: { name: '英雄/角色', icon: '🎭', color: '#ec4899' },
  mindset: { name: '心态/其他', icon: '💡', color: '#6b7280' },
}

export const GAME_CONFIG = {
  valorant: { name: 'Valorant', icon: '🎮' },
  apex: { name: 'Apex Legends', icon: '🎮' },
  cs2: { name: 'CS2', icon: '🎮' },
}
