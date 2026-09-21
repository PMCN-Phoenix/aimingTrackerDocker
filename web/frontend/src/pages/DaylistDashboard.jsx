import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Select, Button, Modal, Spin } from 'antd'
import { ReloadOutlined } from '@ant-design/icons'
import { useDaylists, useDaylistProgress, useScenarioPopup, useScenarioHistory } from '../api/hooks'
import ProgressTable from '../components/ProgressTable'
import ComparisonTable from '../components/ComparisonTable'
import ReflectionList from '../components/ReflectionList'
import HistoryChart from '../components/HistoryChart'
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

  // 获取弹窗数据
  const { data: popupData, isLoading: popupLoading } = useScenarioPopup(
    selectedScenario,
    progressData?.start_ts || 0,
    progressData?.end_ts || 0,
    popupVisible
  )

  // 获取历史曲线数据
  const { data: historyData, isLoading: historyLoading } = useScenarioHistory(
    selectedScenario,
    30,
    popupVisible
  )

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

  // 组合完成度 + 目标对比数据
  const comparisonData = progressData?.rows?.map(row => {
    return {
      ...row,
      today_score: popupData?.scenario === row.scenario ? popupData.today_score : null,
      bench: popupData?.scenario === row.scenario ? popupData.bench : null,
    }
  }) || []

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
          data={comparisonData} 
          loading={progressLoading}
          onScenarioClick={handleScenarioClick}
        />
      </div>

      {/* 场景详情弹窗 */}
      <Modal
        title={selectedScenario}
        open={popupVisible}
        onCancel={handlePopupClose}
        footer={null}
        width={700}
      >
        {popupLoading ? (
          <Spin />
        ) : popupData ? (
          <div>
            {/* 当天成绩 */}
            <div style={{ marginBottom: '24px' }}>
              <h3>当天成绩</h3>
              <p>得分：{popupData.today_score?.score || '-'}</p>
              <p>命中率：{popupData.today_score?.accuracy ? `${popupData.today_score.accuracy}%` : '-'}</p>
            </div>

            {/* 基准数据 */}
            <div style={{ marginBottom: '24px' }}>
              <h3>基准数据</h3>
              <p>下一档线：{popupData.bench?.nextLine || '-'}</p>
              <p>达成率：{popupData.bench?.pct ? `${popupData.bench.pct}%` : '-'}</p>
            </div>

            {/* 历史曲线 */}
            <div style={{ marginBottom: '24px' }}>
              <h3>历史趋势（最近30天）</h3>
              <HistoryChart 
                data={historyData} 
                nextLine={popupData.bench?.nextLine}
                loading={historyLoading}
              />
            </div>

            {/* 历史感悟 */}
            <div>
              <h3>历史感悟</h3>
              <ReflectionList reflections={popupData.reflections || []} />
            </div>
          </div>
        ) : (
          <p>暂无数据</p>
        )}
      </Modal>
    </div>
  )
}
