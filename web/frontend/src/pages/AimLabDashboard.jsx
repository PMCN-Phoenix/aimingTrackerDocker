import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Table, Modal, Spin } from 'antd'
import { getAimlabTasks, getAimlabTaskHistory } from '../api/client'
import HistoryChart from '../components/HistoryChart'

export default function AimLabDashboard() {
  const [selectedTask, setSelectedTask] = useState(null)
  const [popupVisible, setPopupVisible] = useState(false)

  // 获取任务列表
  const { data: tasks, isLoading } = useQuery({
    queryKey: ['aimlabTasks'],
    queryFn: getAimlabTasks,
  })

  // 获取选中任务的历史
  const { data: history, isLoading: historyLoading } = useQuery({
    queryKey: ['aimlabHistory', selectedTask],
    queryFn: () => getAimlabTaskHistory(selectedTask, 30),
    enabled: popupVisible && !!selectedTask,
  })

  // 表格列定义
  const columns = [
    {
      title: '任务名',
      dataIndex: 'task',
      key: 'task',
      render: (text) => (
        <a onClick={() => {
          setSelectedTask(text)
          setPopupVisible(true)
        }}>
          {text}
        </a>
      ),
    },
    {
      title: '最佳得分',
      dataIndex: 'best_score',
      key: 'best_score',
      render: (score) => score ? score.toFixed(2) : '-',
    },
    {
      title: '最佳命中率',
      dataIndex: 'best_accuracy',
      key: 'best_accuracy',
      render: (acc) => acc ? `${acc}%` : '-',
    },
  ]

  return (
    <div>
      <h1 style={{ marginBottom: '24px' }}>Aim Lab 训练记录</h1>

      {isLoading ? (
        <Spin />
      ) : (
        <Table
          dataSource={tasks || []}
          columns={columns}
          rowKey="task"
          pagination={false}
        />
      )}

      {/* 任务详情弹窗 */}
      <Modal
        title={selectedTask}
        open={popupVisible}
        onCancel={() => setPopupVisible(false)}
        footer={null}
        width={700}
      >
        {historyLoading ? (
          <Spin />
        ) : (
          <div>
            <h3>历史趋势（最近30天）</h3>
            <HistoryChart data={history || []} loading={historyLoading} />
          </div>
        )}
      </Modal>
    </div>
  )
}
