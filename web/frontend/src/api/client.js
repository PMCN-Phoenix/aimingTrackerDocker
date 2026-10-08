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

// 加练清单相关
export function getDaylistExtras(daylistId) {
  return request(`/daylists/${encodeURIComponent(daylistId)}/extras`)
}

export function getDaylistWithExtras(daylistId) {
  return request(`/daylists/${encodeURIComponent(daylistId)}/with-extras`)
}

export function createExtraDaylist(data) {
  return fetch(`${BASE_URL}/daylists/extras`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  }).then(res => res.json())
    .then(json => {
      if (json.code !== 0) {
        throw new Error(json.message || '创建失败')
      }
      return json.data
    })
}

export function deleteExtraDaylist(extraId) {
  return fetch(`${BASE_URL}/daylists/extras/${encodeURIComponent(extraId)}`, {
    method: 'DELETE',
  }).then(res => res.json())
    .then(json => {
      if (json.code !== 0) {
        throw new Error(json.message || '删除失败')
      }
      return json.data
    })
}

// 导出 playlist
export function exportPlaylist(daylistId, name = null) {
  const url = name
    ? `${BASE_URL}/daylists/${encodeURIComponent(daylistId)}/export-playlist?name=${encodeURIComponent(name)}`
    : `${BASE_URL}/daylists/${encodeURIComponent(daylistId)}/export-playlist`
  return fetch(url, { method: 'POST' })
    .then(res => res.json())
    .then(json => {
      if (json.code !== 0) {
        throw new Error(json.message || '导出失败')
      }
      return json.data
    })
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

// Aim Lab 相关
export function getAimlabTasks() {
  return request('/aimlab/tasks')
}

export function getAimlabTaskHistory(task, days = 30) {
  return request(`/aimlab/tasks/${encodeURIComponent(task)}/history?days=${days}`)
}

// VDIM 相关
export function getVdimToday() {
  return request('/vdim/today')
}

export function getVdimDay(cycle, day) {
  return request(`/vdim/day/${cycle}/${encodeURIComponent(day)}`)
}

export function getVdimOverview() {
  return request('/vdim/overview')
}

export function getVdimPlaylists() {
  return request('/vdim/playlists')
}

export function getVdimScenarioHistory(scenario, days = 30) {
  return request(`/vdim/scenario/${encodeURIComponent(scenario)}/history?days=${days}`)
}

export function createVdimCheckin(date, note = '') {
  return fetch(`${BASE_URL}/vdim/checkin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ date, note }),
  }).then(res => res.json())
    .then(json => {
      if (json.code !== 0) throw new Error(json.message || '打卡失败')
      return json.data
    })
}

export function createVdimScore(data) {
  return fetch(`${BASE_URL}/vdim/score`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }).then(res => res.json())
    .then(json => {
      if (json.code !== 0) throw new Error(json.message || '保存失败')
      return json.data
    })
}

export function importVdimScores(data) {
  return fetch(`${BASE_URL}/vdim/import`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }).then(res => res.json())
    .then(json => {
      if (json.code !== 0) throw new Error(json.message || '导入失败')
      return json.data
    })
}
