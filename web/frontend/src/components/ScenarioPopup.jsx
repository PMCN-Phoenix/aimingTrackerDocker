import { Modal, Spin } from 'antd'
import { useQuery } from '@tanstack/react-query'
import { getScenarioPopup } from '../api/client'
import ReflectionList from './ReflectionList'
import ReflectionForm from './ReflectionForm'
import HistoryChart from './HistoryChart'

export default function ScenarioPopup({ scenario, visible, onClose, daylist, startTs, endTs }) {
  // 获取弹窗数据（优化版：一个接口拿所有数据）
  const { data: popupData, isLoading } = useQuery({
    queryKey: ['scenarioPopup', scenario, startTs, endTs],
    queryFn: () => getScenarioPopup(scenario, startTs, endTs),
    enabled: visible && !!scenario && !!startTs && !!endTs,
    staleTime: 5 * 60 * 1000, // 缓存 5 分钟，第二次打开秒开
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
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Spin size="large" />
        </div>
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
              data={popupData.history || []} 
              nextLine={popupData.bench?.nextLine}
              loading={false}
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
