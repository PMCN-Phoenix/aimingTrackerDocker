// API 请求封装
const BASE_URL = 'http://127.0.0.1:8000/api'

async function request(path) {
  const res = await fetch(`${BASE_URL}${path}`)
  const json = await res.json()
  if (json.code !== 0) {
    throw new Error(json.message || '请求失败')
  }
  return json.data
}

// 清单相关
export function getDaylists() {
  return request('/daylists')
}

export function getDaylistProgress(daylistId) {
  return request(`/daylists/${encodeURIComponent(daylistId)}/progress`)
}

// 场景相关
export function getScenarioPopup(scenario, startTs, endTs) {
  return request(`/scenarios/${encodeURIComponent(scenario)}/popup?start_ts=${startTs}&end_ts=${endTs}`)
}

export function getScenarioHistory(scenario, days = 30) {
  return request(`/scenarios/${encodeURIComponent(scenario)}/history?days=${days}`)
}

// 基准总览相关
export function getBenchGroups(list = 'viscose-s2-easier') {
  return request(`/bench/groups?list=${encodeURIComponent(list)}`)
}

export function getBenchScenarios(list = 'viscose-s2-easier') {
  return request(`/bench/scenarios?list=${encodeURIComponent(list)}`)
}

// 感悟相关
export function createReflection(data) {
  return fetch(`${BASE_URL}/reflections`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  }).then(res => res.json())
    .then(json => {
      if (json.code !== 0) {
        throw new Error(json.message || '保存失败')
      }
      return json.data
    })
}
