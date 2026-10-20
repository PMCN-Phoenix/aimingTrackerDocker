import React from 'react'
import { Card, Row, Col, Typography, theme } from 'antd'
import {
  CheckCircleOutlined,
  ThunderboltOutlined,
  TrophyOutlined,
  AlertOutlined,
} from '@ant-design/icons'

const { Text } = Typography

export default function SummaryStrip({ rows = [], roundsTotal = 0 }) {
  const { token } = theme.useToken()

  const totalItems = rows.length
  const doneItems = rows.filter(r => r.status === '已完成').length
  const itemPct = totalItems > 0 ? Math.round((doneItems / totalItems) * 100) : 0

  const doneRounds = rows.reduce((acc, r) => acc + (r.done_rounds || 0), 0)
  const reqRounds = roundsTotal || rows.reduce((acc, r) => acc + (r.required_rounds || 0), 0)
  const roundsPct = reqRounds > 0 ? Math.round((doneRounds / reqRounds) * 100) : 0

  const benchRows = rows.filter(r => r.bench && typeof r.bench.nextLine === 'number')
  const hasBench = benchRows.length > 0
  const achievedItems = hasBench
    ? benchRows.filter(r => r.today_score?.score && r.today_score.score >= r.bench.nextLine).length
    : 0

  const decayedRows = rows.filter(r => r.round_stats && typeof r.round_stats.drop_pct === 'number' && r.round_stats.drop_pct <= -15)
  const hasDecay = decayedRows.length > 0
  const worstDrop = hasDecay
    ? Math.min(...decayedRows.map(r => r.round_stats.drop_pct))
    : 0

  const cardStyle = {
    borderRadius: '10px',
    boxShadow: '0 2px 6px rgba(0,0,0,0.03)',
    border: `1px solid ${token.colorBorderSecondary}`,
    background: token.colorBgContainer,
    height: '100%',
    transition: 'background 0.3s, border-color 0.3s',
  }

  return (
    <div style={{ marginBottom: '24px' }}>
      <Row gutter={[16, 16]}>
        {/* 卡片 1: 完成度 */}
        <Col xs={12} sm={6}>
          <Card size="small" style={cardStyle} styles={{ body: { padding: '16px' } }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <CheckCircleOutlined style={{ color: itemPct === 100 ? '#52c41a' : '#1677ff', fontSize: '18px' }} />
              <Text type="secondary" style={{ fontSize: '13px' }}>场景完成度</Text>
            </div>
            <div style={{ fontSize: '24px', fontWeight: 700, color: token.colorText, fontFamily: 'monospace' }}>
              {doneItems} / {totalItems}
              <span style={{ fontSize: '14px', fontWeight: 500, color: token.colorTextSecondary, marginLeft: '6px' }}>
                ({itemPct}%)
              </span>
            </div>
            <div style={{ fontSize: '12px', color: itemPct === 100 ? '#52c41a' : token.colorTextSecondary, marginTop: '2px' }}>
              {itemPct === 100 ? '清单场景已全部打完' : `尚余 ${totalItems - doneItems} 项待完成`}
            </div>
          </Card>
        </Col>

        {/* 卡片 2: 训练量 */}
        <Col xs={12} sm={6}>
          <Card size="small" style={cardStyle} styles={{ body: { padding: '16px' } }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <ThunderboltOutlined style={{ color: '#fa8c16', fontSize: '18px' }} />
              <Text type="secondary" style={{ fontSize: '13px' }}>训练轮数</Text>
            </div>
            <div style={{ fontSize: '24px', fontWeight: 700, color: token.colorText, fontFamily: 'monospace' }}>
              {doneRounds} / {reqRounds}
              <span style={{ fontSize: '14px', fontWeight: 500, color: token.colorTextSecondary, marginLeft: '6px' }}>
                轮
              </span>
            </div>
            <div style={{ fontSize: '12px', color: roundsPct >= 100 ? '#52c41a' : token.colorTextSecondary, marginTop: '2px' }}>
              {roundsPct >= 100 ? '训练量达成 100%' : `已完成计划训练量 ${roundsPct}%`}
            </div>
          </Card>
        </Col>

        {/* 卡片 3: 达标项 */}
        <Col xs={12} sm={6}>
          <Card size="small" style={cardStyle} styles={{ body: { padding: '16px' } }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <TrophyOutlined style={{ color: hasBench ? '#722ed1' : token.colorTextSecondary, fontSize: '18px' }} />
              <Text type="secondary" style={{ fontSize: '13px' }}>基准达标</Text>
            </div>
            {hasBench ? (
              <>
                <div style={{ fontSize: '24px', fontWeight: 700, color: token.colorText, fontFamily: 'monospace' }}>
                  {achievedItems} / {benchRows.length}
                  <span style={{ fontSize: '14px', fontWeight: 500, color: token.colorTextSecondary, marginLeft: '6px' }}>
                    项
                  </span>
                </div>
                <div style={{ fontSize: '12px', color: token.colorTextSecondary, marginTop: '2px' }}>
                  达成率 {Math.round((achievedItems / benchRows.length) * 100)}%
                </div>
              </>
            ) : (
              <>
                <div style={{ fontSize: '20px', fontWeight: 600, color: token.colorTextSecondary, marginTop: '4px' }}>
                  无基准数据
                </div>
                <div style={{ fontSize: '12px', color: token.colorTextSecondary, marginTop: '4px' }}>
                  该清单场景不在基准表内
                </div>
              </>
            )}
          </Card>
        </Col>

        {/* 卡片 4: 衰减预警 */}
        <Col xs={12} sm={6}>
          <Card size="small" style={cardStyle} styles={{ body: { padding: '16px' } }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <AlertOutlined style={{ color: hasDecay ? '#ff4d4f' : '#52c41a', fontSize: '18px' }} />
              <Text type="secondary" style={{ fontSize: '13px' }}>后段疲劳衰减</Text>
            </div>
            {hasDecay ? (
              <>
                <div style={{ fontSize: '24px', fontWeight: 700, color: '#ff4d4f', fontFamily: 'monospace' }}>
                  {decayedRows.length} 项
                  <span style={{ fontSize: '14px', fontWeight: 600, marginLeft: '6px' }}>
                    衰减&gt;15%
                  </span>
                </div>
                <div style={{ fontSize: '12px', color: '#cf1322', marginTop: '2px', fontWeight: 500 }}>
                  最差掉分: {worstDrop.toFixed(1)}% (末轮 vs 峰值)
                </div>
              </>
            ) : (
              <>
                <div style={{ fontSize: '20px', fontWeight: 600, color: '#52c41a', marginTop: '4px' }}>
                  状态稳定
                </div>
                <div style={{ fontSize: '12px', color: '#52c41a', marginTop: '4px' }}>
                  末轮无显著体能/专注度衰减
                </div>
              </>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}
