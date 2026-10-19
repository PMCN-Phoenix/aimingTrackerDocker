import React from 'react'
import { Drawer, Spin, Descriptions, Tag, Divider, Empty } from 'antd'
import { useQuery } from '@tanstack/react-query'
import { getScenarioPopup } from '../api/client'
import ReflectionList from './ReflectionList'
import ReflectionForm from './ReflectionForm'
import HistoryChart from './HistoryChart'
import TierLadder from './TierLadder'

export default function ScenarioDrawer({
  scenario,
  open,
  onClose,
  daylist,
  startTs,
  endTs,
  rowBench,
  roundStats,
}) {
  const { data: popupData, isLoading } = useQuery({
    queryKey: ['scenarioPopup', scenario, startTs, endTs],
    queryFn: () => getScenarioPopup(scenario, startTs, endTs),
    enabled: open && !!scenario,
    staleTime: 5 * 60 * 1000,
  })

  // 优先用父组件行传进来的 bench.targets，其次用 popup 内部的
  const benchData = rowBench || popupData?.bench
  const targets = benchData?.targets

  return (
    <Drawer
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontFamily: 'monospace', fontWeight: 700, fontSize: '15px' }}>
            {scenario}
          </span>
        </div>
      }
      placement="right"
      width={520}
      open={open}
      onClose={onClose}
      destroyOnClose
    >
      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <Spin size="large" />
        </div>
      ) : popupData ? (
        <div>
          {/* 1. 当天成绩 & 轮次衰减 */}
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ margin: '0 0 12px 0', color: '#1f1f1f', fontSize: '14px', fontWeight: 600 }}>
              🎯 当日训练表现
            </h4>
            <Descriptions size="small" bordered column={2}>
              <Descriptions.Item label="当日最佳">
                <span style={{ fontWeight: 700, fontSize: '15px', color: '#1677ff', fontFamily: 'monospace' }}>
                  {popupData.today_score?.score ?? '—'}
                </span>
              </Descriptions.Item>
              <Descriptions.Item label="命中率">
                <span style={{ fontWeight: 600, fontFamily: 'monospace' }}>
                  {popupData.today_score?.accuracy ? `${popupData.today_score.accuracy}%` : '—'}
                </span>
              </Descriptions.Item>
              {roundStats && (
                <>
                  <Descriptions.Item label="首轮得分">
                    <span style={{ fontFamily: 'monospace' }}>{roundStats.first}</span>
                  </Descriptions.Item>
                  <Descriptions.Item label="末轮得分">
                    <span style={{ fontFamily: 'monospace' }}>{roundStats.last}</span>
                  </Descriptions.Item>
                  <Descriptions.Item label="轮次衰减 (末 vs 峰)">
                    <span
                      style={{
                        fontFamily: 'monospace',
                        fontWeight: 600,
                        color: roundStats.drop_pct <= -15 ? '#ff4d4f' : '#52c41a',
                      }}
                    >
                      {roundStats.drop_pct}%
                    </span>
                  </Descriptions.Item>
                  <Descriptions.Item label="今日总轮数">
                    <span style={{ fontFamily: 'monospace' }}>{roundStats.n} 轮</span>
                  </Descriptions.Item>
                </>
              )}
            </Descriptions>
          </div>

          <Divider style={{ margin: '16px 0' }} />

          {/* 2. 基准档位与阶梯 */}
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ margin: '0 0 12px 0', color: '#1f1f1f', fontSize: '14px', fontWeight: 600 }}>
              🏆 基准档位
            </h4>
            {benchData?.nextLine ? (
              <div>
                <Descriptions size="small" bordered column={2} style={{ marginBottom: '12px' }}>
                  <Descriptions.Item label="当前档位">
                    <Tag color="blue">{benchData.rank || '未评定'}</Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="下一档位">
                    <Tag color="cyan">{benchData.subRank || benchData.rank || '—'}</Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="下一档线">
                    <span style={{ fontWeight: 600, fontFamily: 'monospace' }}>{benchData.nextLine}</span>
                  </Descriptions.Item>
                  <Descriptions.Item label="达成率">
                    <span style={{ fontWeight: 600, fontFamily: 'monospace' }}>
                      {benchData.pct ? `${benchData.pct}%` : '—'}
                    </span>
                  </Descriptions.Item>
                </Descriptions>

                {/* 9 档阶梯条 */}
                {targets && (
                  <div style={{ background: '#fafafa', padding: '12px', borderRadius: '8px', border: '1px solid #f0f0f0' }}>
                    <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '4px' }}>
                      Viscose 阶梯进阶线
                    </div>
                    <TierLadder
                      targets={targets}
                      achIdx={benchData.achIdx}
                      currentScore={popupData.today_score?.score}
                      style={{ maxWidth: '100%' }}
                    />
                  </div>
                )}
              </div>
            ) : (
              <div style={{ padding: '16px', background: '#fafafa', borderRadius: '8px', color: '#8c8c8c', fontSize: '13px', textAlign: 'center' }}>
                该场景暂无 Viscose 官方基准档位数据
              </div>
            )}
          </div>

          <Divider style={{ margin: '16px 0' }} />

          {/* 3. 历史曲线 (近 30 天) */}
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ margin: '0 0 8px 0', color: '#1f1f1f', fontSize: '14px', fontWeight: 600 }}>
              📈 历史成绩趋势（最近 30 天）
            </h4>
            <HistoryChart
              data={popupData.history || []}
              nextLine={benchData?.nextLine}
              loading={false}
            />
          </div>

          <Divider style={{ margin: '16px 0' }} />

          {/* 4. 场景历史感悟与写入 */}
          <div>
            <h4 style={{ margin: '0 0 12px 0', color: '#1f1f1f', fontSize: '14px', fontWeight: 600 }}>
              💡 训练感悟
            </h4>
            <ReflectionList reflections={popupData.reflections || []} />
            <div style={{ marginTop: '16px' }}>
              <ReflectionForm scenario={scenario} daylist={daylist} />
            </div>
          </div>
        </div>
      ) : (
        <Empty description="暂无该场景详情" />
      )}
    </Drawer>
  )
}
