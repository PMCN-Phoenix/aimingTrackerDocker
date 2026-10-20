import { useState } from 'react'
import { Card, Button, Dropdown, theme } from 'antd'
import { DownOutlined, UpOutlined, MoreOutlined, EditOutlined, ExportOutlined, DeleteOutlined, ClockCircleOutlined } from '@ant-design/icons'
import DaylistRow from './DaylistRow'
import dayjs from 'dayjs'
import { useAppTheme } from '../theme/ThemeContext'

export default function ExtraDaylistCard({
  extraData,
  onScenarioClick,
  onEdit,
  onExport,
  onDelete,
}) {
  const { token } = theme.useToken()
  const { isDark } = useAppTheme()
  const [collapsed, setCollapsed] = useState(false)

  if (!extraData) return null

  const { daylist, name, label, parent_daylist, created_at, rows = [], rounds_total = 0 } = extraData

  // 计算完成轮数
  const doneRounds = rows.reduce((sum, row) => sum + (row.done_rounds || 0), 0)
  const reqTotal = rounds_total || rows.reduce((s, r) => s + (r.required_rounds || 0), 0)
  const allDone = rows.length > 0 && doneRounds >= reqTotal

  // 状态颜色
  const statusColor = allDone ? '#52c41a' : doneRounds > 0 ? '#faad14' : token.colorTextSecondary
  const statusText = allDone ? '已完成' : doneRounds > 0 ? '进行中' : '未开始'

  // 加练日期标签
  const extraDateLabel = parent_daylist ? `${parent_daylist} 加练` : '加练'

  // 操作菜单 items
  const menuItems = [
    { key: 'edit', icon: <EditOutlined />, label: '编辑清单', onClick: onEdit },
    { key: 'export', icon: <ExportOutlined />, label: '导出 Playlist', onClick: onExport },
    { type: 'divider' },
    { key: 'delete', icon: <DeleteOutlined />, label: '删除清单', danger: true, onClick: onDelete },
  ]

  return (
    <Card
      size="small"
      style={{
        marginBottom: '16px',
        borderLeft: '4px solid #b388ff',
        background: token.colorBgContainer,
        borderRadius: '8px',
        borderColor: token.colorBorderSecondary,
      }}
      styles={{ body: { padding: 0 } }}
    >
      {/* 卡片头部 */}
      <div
        style={{
          padding: '12px 16px',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
        }}
        onClick={() => setCollapsed(!collapsed)}
      >
        <span style={{ fontSize: '18px' }}>📋</span>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{
              fontSize: '11px',
              fontWeight: 600,
              color: isDark ? '#c084fc' : '#7c3aed',
              background: isDark ? 'rgba(124, 58, 237, 0.25)' : '#ede9fe',
              padding: '2px 8px',
              borderRadius: '4px',
            }}>
              {extraDateLabel}
            </span>
            <span style={{ fontWeight: 600, fontSize: '15px', color: token.colorText }}>
              {name || label || daylist}
            </span>
          </div>
          <div style={{ fontSize: '12px', color: token.colorTextSecondary, marginTop: '2px' }}>
            <ClockCircleOutlined style={{ marginRight: '4px' }} />
            创建于 {created_at ? dayjs.unix(created_at).format('MM-DD HH:mm') : '未知'}
            <span style={{ margin: '0 8px' }}>·</span>
            {rows.length} 个场景
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '14px', fontWeight: 600, color: statusColor, fontFamily: 'monospace' }}>
            {doneRounds}/{reqTotal}
            <span style={{ marginLeft: '8px', fontSize: '12px' }}>{statusText}</span>
          </span>
          <Dropdown menu={{ items: menuItems }} trigger={['click']}>
            <Button
              type="text"
              icon={<MoreOutlined />}
              onClick={(e) => e.stopPropagation()}
            />
          </Dropdown>
          {collapsed ? <DownOutlined style={{ color: token.colorTextSecondary }} /> : <UpOutlined style={{ color: token.colorTextSecondary }} />}
        </div>
      </div>

      {/* 卡片内容 */}
      {!collapsed && (
        <div style={{ padding: '12px 16px 8px', borderTop: '1px solid #f0f0f0', background: '#fff' }}>
          {rows.map((row) => (
            <DaylistRow
              key={row.scenario}
              row={row}
              mode="compact"
              onClick={onScenarioClick}
            />
          ))}
        </div>
      )}
    </Card>
  )
}
