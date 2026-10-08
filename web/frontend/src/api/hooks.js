import { useQuery } from '@tanstack/react-query'
import { getDaylists, getDaylistProgress, getScenarioPopup, getScenarioHistory, getDaylistExtras, getVdimToday, getVdimDay, getVdimOverview, getVdimPlaylists, getVdimScenarioHistory } from '../api/client'

// 清单列表
export function useDaylists() {
  return useQuery({
    queryKey: ['daylists'],
    queryFn: getDaylists,
    staleTime: 5 * 60 * 1000, // 5分钟
  })
}

// 完成度面板数据
export function useDaylistProgress(daylistId) {
  return useQuery({
    queryKey: ['daylistProgress', daylistId],
    queryFn: () => getDaylistProgress(daylistId),
    staleTime: 60 * 1000, // 1分钟
  })
}

// 加练清单列表
export function useDaylistExtras(daylistId) {
  return useQuery({
    queryKey: ['daylistExtras', daylistId],
    queryFn: () => getDaylistExtras(daylistId),
    staleTime: 60 * 1000, // 1分钟
  })
}

// 场景弹窗数据
export function useScenarioPopup(scenario, startTs, endTs, enabled = true) {
  return useQuery({
    queryKey: ['scenarioPopup', scenario, startTs, endTs],
    queryFn: () => getScenarioPopup(scenario, startTs, endTs),
    enabled: enabled && !!scenario,
    staleTime: 0, // 不缓存，每次打开都重新查
  })
}

// 场景历史数据
export function useScenarioHistory(scenario, days = 30, enabled = true) {
  return useQuery({
    queryKey: ['scenarioHistory', scenario, days],
    queryFn: () => getScenarioHistory(scenario, days),
    enabled: enabled && !!scenario,
    staleTime: 60 * 1000,
  })
}

// VDIM 相关 hooks
export function useVdimToday() {
  return useQuery({
    queryKey: ['vdimToday'],
    queryFn: getVdimToday,
    staleTime: 60 * 1000,
  })
}

export function useVdimDay(cycle, day) {
  return useQuery({
    queryKey: ['vdimDay', cycle, day],
    queryFn: () => getVdimDay(cycle, day),
    enabled: !!cycle && !!day,
    staleTime: 60 * 1000,
  })
}

export function useVdimOverview() {
  return useQuery({
    queryKey: ['vdimOverview'],
    queryFn: getVdimOverview,
    staleTime: 60 * 1000,
  })
}

export function useVdimPlaylists() {
  return useQuery({
    queryKey: ['vdimPlaylists'],
    queryFn: getVdimPlaylists,
    staleTime: 5 * 60 * 1000,
  })
}

export function useVdimScenarioHistory(scenario, days = 30, enabled = true) {
  return useQuery({
    queryKey: ['vdimScenarioHistory', scenario, days],
    queryFn: () => getVdimScenarioHistory(scenario, days),
    enabled: enabled && !!scenario,
    staleTime: 60 * 1000,
  })
}
