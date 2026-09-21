import { Table, Progress, Tag } from 'antd'

export default function ComparisonTable({ data, loading, onScenarioClick }) {
  // 状态颜色
  const getAchievementColor = (percent) => {
    if (percent >= 100) return 'green'
    if (percent >= 70) return 'orange'
    return 'red'
  }

  // 表格列
  const columns = [
    {
      title: '顺序',
      dataIndex: 'order',
      key: 'order',
      width: 60,
    },
    {
      title: '场景名',
      dataIndex: 'scenario',
      key: 'scenario',
      render: (text) => (
        <a onClick={() => onScenarioClick(text)}>{text}</a>
      ),
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      width: 100,
    },
    {
      title: '目标分',
      key: 'target',
      render: (_, record) => record.bench?.nextLine || '-',
      width: 100,
    },
    {
      title: '现状',
      key: 'current',
      render: (_, record) => record.today_score?.score || '-',
      width: 100,
    },
    {
      title: '达成度',
      key: 'achievement',
      render: (_, record) => {
        const target = record.bench?.nextLine
        const current = record.today_score?.score
        if (!target || !current) return '-'
        const percent = Math.round((current / target) * 100)
        return (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Progress percent={percent} size="small" style={{ width: 80 }} />
            <Tag color={getAchievementColor(percent)}>{percent}%</Tag>
          </div>
        )
      },
      width: 150,
    },
    {
      title: '命中率',
      key: 'accuracy',
      render: (_, record) => record.today_score?.accuracy ? `${record.today_score.accuracy}%` : '-',
      width: 100,
    },
  ]

  return (
    <Table 
      columns={columns} 
      dataSource={data || []} 
      rowKey="scenario"
      pagination={false}
      size="middle"
      loading={loading}
    />
  )
}
