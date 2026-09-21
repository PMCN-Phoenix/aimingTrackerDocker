import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Select, Button, Spin } from 'antd'
import { ReloadOutlined } from '@ant-design/icons'
import { useDaylists, useDaylistProgress } from '../api/hooks'
import ProgressTable from '../components/ProgressTable'
import ComparisonTable from '../components/ComparisonTable'
import ScenarioPopup from '../components/ScenarioPopup'
import DateRangePicker from '../components/DateRangePicker'
import dayjs from 'dayjs'

export default function DaylistDashboard() {
  const { daylistId } = useParams()
  const navigate = useNavigate()
  const [selectedScenario, setSelectedScenario] = useState(null)
  const [popupVisible, setPopupVisible] = useState(false)
  const [dateRange, setDateRange] = useState([dayjs(), dayjs()])

  // 获取清单列表
  const { data: daylists, isLoading: daylistsLoading } = useDaylists()
  
  // 获取当前清单的完成度数据
  const { data: progressData, isLoading: progressLoading, refetch } = useDaylistProgress(daylistId)

  // 切换清单
  const handleDaylistChange = (value) => {
    navigate(`/daylist/${value}`)
  }

  // 切换日期范围
  const handleDateChange = (dates) => {
    setDateRange(dates)
    // TODO: 日期变化后重新查询数据
  }

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

  if (progressLoading || daylistsLoading) {
    return <Spin size="large" style={{ display: 'block', marginTop: '100px' }} />
  }

  return (
    <div>
      {/* 过滤器栏 */}
      <div style={{ marginBottom: '24px', display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
        <Select
          value={daylistId}
          onChange={handleDaylistChange}
          style={{ width: 200 }}
          options={daylists?.map(d => ({ value: d.daylist, label: `${d.daylist} - ${d.label}` })) || []}
        />
        <DateRangePicker value={dateRange} onChange={handleDateChange} />
        <Button 
          type="primary" 
          icon={<ReloadOutlined />} 
          onClick={() => refetch()}
        >
          刷新
        </Button>
      </div>

      {/* 完成度面板 */}
      <div style={{ marginBottom: '32px' }}>
        <h2>今日清单·完成度</h2>
        <ProgressTable 
          data={progressData?.rows || []} 
          loading={progressLoading}
          onScenarioClick={handleScenarioClick}
        />
      </div>

      {/* 目标对比面板 */}
      <div style={{ marginBottom: '32px' }}>
        <h2>今日清单·目标对比</h2>
        <ComparisonTable 
          data={progressData?.rows || []} 
          loading={progressLoading}
          onScenarioClick={handleScenarioClick}
        />
      </div>

      {/* 场景详情弹窗（优化版：合并所有数据到一个接口） */}
      <ScenarioPopup
        scenario={selectedScenario}
        visible={popupVisible}
        onClose={handlePopupClose}
        daylist={daylistId}
        startTs={progressData?.start_ts || 0}
        endTs={progressData?.end_ts || 0}
      />
    </div>
  )
}
