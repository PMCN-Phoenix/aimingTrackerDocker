import { Modal, Spin } from 'antd'
import { useQuery } from '@tanstack/react-query'
import { getScenarioPopup } from '../api/client'
import ReflectionList from './ReflectionList'
import ReflectionForm from './ReflectionForm'
import HistoryChart from './HistoryChart'

export default function ScenarioPopup({ scenario, visible, onClose, daylist }) {
  // 获取弹窗数据
  const { data: popupData, isLoading } = useQuery({
    queryKey: ['scenarioPopup', scenario],
    queryFn: () => getScenarioPopup(scenario, 1789920000, 1790006399),
    enabled: visible && !!scenario,
  })

  // 获取历史曲线数据
  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ['scenarioHistory', scenario],
    queryFn: () => import('../api/client').then(m => m.getScenarioHistory(scenario, 30)),
    enabled: visible && !!scenario,
  })

  return (
    <Modal
      title={scenario}
      open={visible}
      onCancel={onClose}
      footer={null}
      width={700}
    >
      {isLoading ? (
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
            {/* 写入感悟 */}
            <ReflectionForm scenario={scenario} daylist={daylist} />
          </div>
        </div>
      ) : (
        <p>暂无数据</p>
      )}
    </Modal>
  )
}
