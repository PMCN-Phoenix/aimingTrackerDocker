import { useState } from 'react'
import { Card, Button, Dropdown, Menu, Tooltip } from 'antd'
import { DownOutlined, UpOutlined, MoreOutlined, EditOutlined, ExportOutlined, DeleteOutlined, ClockCircleOutlined } from '@ant-design/icons'
import ProgressTable from './ProgressTable'
import dayjs from 'dayjs'

export default function ExtraDaylistCard({
  extraData,
  onScenarioClick,
  onEdit,
  onExport,
  onDelete,
}) {
  const [collapsed, setCollapsed] = useState(false)

  if (!extraData) return null

  const { daylist, name, label, parent_daylist, created_at, rows = [], rounds_total = 0 } = extraData

  // 计算完成轮数
  const doneRounds = rows.reduce((sum, row) => sum + (row.done_rounds || 0), 0)
  const allDone = rows.length > 0 && rows.every(row => row.done_rounds >= row.required_rounds)

  // 状态颜色
  const statusColor = allDone ? '#52c41a' : doneRounds > 0 ? '#faad14' : '#8c8c8c'
  const statusText = allDone ? '已完成' : doneRounds > 0 ? '进行中' : '未开始'

  // 加练日期标签
  const extraDateLabel = parent_daylist ? `${parent_daylist} 加练` : '加练'

  // 操作菜单
  const menu = (
    <Menu>
      <Menu.Item key="edit" icon={<EditOutlined />} onClick={onEdit}>
        编辑清单
      </Menu.Item>
      <Menu.Item key="export" icon={<ExportOutlined />} onClick={onExport}>
        导出 Playlist
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="delete" icon={<DeleteOutlined />} danger onClick={onDelete}>
        删除清单
      </Menu.Item>
    </Menu>
  )

  return (
    <Card
      size="small"
      style={{
        marginBottom: '16px',
        borderLeft: '4px solid #b388ff',
        background: '#fafafa',
      }}
      bodyStyle={{ padding: 0 }}
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
              color: '#7c3aed',
              background: '#ede9fe',
              padding: '2px 8px',
              borderRadius: '4px',
            }}>
              {extraDateLabel}
            </span>
            <span style={{ fontWeight: 600, fontSize: '15px', color: '#333' }}>
              {name || label || daylist}
            </span>
          </div>
          <div style={{ fontSize: '12px', color: '#888', marginTop: '2px' }}>
            <ClockCircleOutlined style={{ marginRight: '4px' }} />
            创建于 {created_at ? dayjs.unix(created_at).format('MM-DD HH:mm') : '未知'}
            <span style={{ margin: '0 8px' }}>·</span>
            {rows.length} 个场景
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '14px', fontWeight: 600, color: statusColor }}>
            {doneRounds}/{rounds_total || rows.reduce((s, r) => s + r.required_rounds, 0)}
            <span style={{ marginLeft: '8px', fontSize: '12px' }}>{statusText}</span>
          </span>
          <Dropdown overlay={menu} trigger={['click']}>
            <Button
              type="text"
              icon={<MoreOutlined />}
              onClick={(e) => e.stopPropagation()}
            />
          </Dropdown>
          {collapsed ? <DownOutlined style={{ color: '#888' }} /> : <UpOutlined style={{ color: '#888' }} />}
        </div>
      </div>

      {/* 卡片内容 */}
      {!collapsed && (
        <div style={{ padding: '8px 16px 16px', borderTop: '1px solid #eee' }}>
          <ProgressTable
            data={rows}
            onScenarioClick={onScenarioClick}
            compact={true}
          />
        </div>
      )}
    </Card>
  )
}
