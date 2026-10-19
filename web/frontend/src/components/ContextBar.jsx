import React from 'react'
import { Select, Segmented, Button, Tag, Space, Tooltip } from 'antd'
import {
  ReloadOutlined,
  DownloadOutlined,
  FieldTimeOutlined,
  AppstoreOutlined,
  BarsOutlined,
} from '@ant-design/icons'

export default function ContextBar({
  daylistId,
  daylists = [],
  onDaylistChange,
  runDate,
  session,
  density = 'card',
  onDensityChange,
  onRefresh,
  onExport,
  isRefreshing,
  isExporting,
}) {
  const formatDuration = (min) => {
    if (!min && min !== 0) return ''
    const h = Math.floor(min / 60)
    const m = min % 60
    if (h > 0) return `${h}h${m.toString().padStart(2, '0')}m`
    return `${m}m`
  }

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '12px',
        padding: '12px 16px',
        background: '#fff',
        borderRadius: '10px',
        border: '1px solid #f0f0f0',
        marginBottom: '20px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.02)',
      }}
    >
      {/* 左侧：清单下拉 + 执行日期与真实会话时段 */}
      <Space size="middle" wrap align="center">
        <Select
          value={daylistId}
          onChange={onDaylistChange}
          style={{ width: 230 }}
          options={daylists.map((d) => ({
            value: d.daylist,
            label: `${d.daylist} · ${d.label || '未命名'}`,
          }))}
        />

        {/* 执行日期与时段 */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#595959', fontSize: '13px' }}>
          <FieldTimeOutlined style={{ color: '#1677ff' }} />
          <span>{runDate || '—'}</span>
          {session ? (
            <>
              <span style={{ color: '#bfbfbf' }}>|</span>
              <span style={{ fontFamily: 'monospace', fontWeight: 600 }}>
                {session.start}–{session.end} ({formatDuration(session.duration_min)})
              </span>
            </>
          ) : null}
        </div>

        {/* 超过 90 分钟的 Q020 疲劳预警 */}
        {session?.is_overtime && (
          <Tooltip title="依据 Q020 疲劳规约：单次训练超 90 分钟后神经注意力显著衰退，建议控制单次时长">
            <Tag color="error" style={{ borderRadius: '4px', fontWeight: 500 }}>
              ⚠ 训练已超 90m (Q020疲劳预警)
            </Tag>
          </Tooltip>
        )}
      </Space>

      {/* 右侧：密度切换 + 刷新 + 导出 */}
      <Space size="small">
        <Segmented
          value={density}
          onChange={onDensityChange}
          options={[
            {
              value: 'card',
              label: (
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <AppstoreOutlined />
                  <span>卡片流</span>
                </div>
              ),
            },
            {
              value: 'compact',
              label: (
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <BarsOutlined />
                  <span>紧凑表</span>
                </div>
              ),
            },
          ]}
        />

        <Button
          icon={<ReloadOutlined spin={isRefreshing} />}
          onClick={onRefresh}
          loading={isRefreshing}
        >
          刷新
        </Button>

        <Button
          type="primary"
          icon={<DownloadOutlined />}
          onClick={onExport}
          loading={isExporting}
        >
          导出 Playlist
        </Button>
      </Space>
    </div>
  )
}
