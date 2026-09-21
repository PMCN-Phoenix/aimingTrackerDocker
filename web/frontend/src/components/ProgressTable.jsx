import { Table, Tag, Progress } from 'antd'

export default function ProgressTable({ data, loading, onScenarioClick }) {
  // 状态标签颜色
  const getStatusColor = (status) => {
    switch (status) {
      case '已完成': return 'green'
      case '进行中': return 'orange'
      default: return 'default'
    }
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
      title: '要求轮数',
      dataIndex: 'required_rounds',
      key: 'required_rounds',
      width: 100,
    },
    {
      title: '已打轮数',
      dataIndex: 'done_rounds',
      key: 'done_rounds',
      width: 100,
    },
    {
      title: '进度',
      key: 'progress',
      render: (_, record) => {
        const percent = record.required_rounds > 0 
          ? Math.round((record.done_rounds / record.required_rounds) * 100) 
          : 0
        return <Progress percent={Math.min(percent, 100)} size="small" />
      },
      width: 120,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => <Tag color={getStatusColor(status)}>{status}</Tag>,
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
