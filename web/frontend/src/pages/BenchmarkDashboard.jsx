import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Tabs } from 'antd'
import RankDistributionBar from '../components/RankDistributionBar'
import CategorySection from '../components/CategorySection'
import ScenarioPopup from '../components/ScenarioPopup'
import { getBenchGroups } from '../api/client'

export default function BenchmarkDashboard() {
  const navigate = useNavigate()
  const [selectedScenario, setSelectedScenario] = useState(null)
  const [popupVisible, setPopupVisible] = useState(false)

  // 获取基准分组数据
  const { data: benchData, isLoading } = useQuery({
    queryKey: ['benchGroups', 'viscose-s2-easier'],
    queryFn: () => getBenchGroups('viscose-s2-easier'),
  })

  // 点击场景名
  const handleScenarioClick = (scenario) => {
    setSelectedScenario(scenario)
    setPopupVisible(true)
  }

  // 关闭弹窗
  const handlePopupClose = () => {
    setPopupVisible(false)
    setSelectedScenario(null)
  }

  if (isLoading) {
    return <div style={{ padding: '50px', textAlign: 'center' }}>加载中...</div>
  }

  return (
    <div>
      <h1 style={{ marginBottom: '24px' }}>基准总览（Viscose S2 Easier）</h1>

      {/* 顶部档位分布条 */}
      <RankDistributionBar 
        data={benchData?.rank_distribution || {}} 
        total={benchData?.total || 0}
      />

      {/* 大类分组 */}
      <div style={{ marginTop: '32px' }}>
        {Object.entries(benchData?.groups || {}).map(([cat, subcategories]) => (
          <CategorySection
            key={cat}
            category={cat}
            subcategories={subcategories}
            onScenarioClick={handleScenarioClick}
          />
        ))}
      </div>

      {/* 场景详情弹窗 */}
      <ScenarioPopup
        scenario={selectedScenario}
        visible={popupVisible}
        onClose={handlePopupClose}
      />
    </div>
  )
}
