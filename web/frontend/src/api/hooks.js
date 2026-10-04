import { useQuery } from '@tanstack/react-query'
import { getDaylists, getDaylistProgress, getScenarioPopup, getScenarioHistory, getDaylistExtras } from '../api/client'

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
