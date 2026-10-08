import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Card, Row, Col, Statistic, Select, Button, Spin, message,
  Modal, Form, InputNumber, Table, Tag, Space, Tooltip, Divider
} from 'antd'
import {
  ReloadOutlined, CheckCircleOutlined, CalendarOutlined,
  FireOutlined, TrophyOutlined, PlusOutlined, BulbOutlined,
  ArrowLeftOutlined
} from '@ant-design/icons'
import { useQueryClient } from '@tanstack/react-query'
import { useVdimToday, useVdimDay, useVdimOverview, useVdimPlaylists } from '../api/hooks'
import { createVdimCheckin, createVdimScore } from '../api/client'
import dayjs from 'dayjs'

const { Option } = Select

// 状态颜色映射
const STATUS_COLOR = {
  '已完成': 'green',
  '进行中': 'blue',
  '未开始': 'default',
}

// 档位颜色
const RANK_COLOR = {
  'Lemming': '#8B4513',
  'Hare': '#D2691E',
  'Ermine': '#CD853F',
  'Penguin': '#4682B4',
  'Fox': '#FF8C00',
  'Wolf': '#2F4F4F',
  'Tiger': '#FF6347',
  'Astra': '#9370DB',
}

export default function VdimDashboard() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // 获取今日信息（用于默认选中）
  const { data: todayData } = useVdimToday()

  // 当前选中的周期和训练日
  const [cycle, setCycle] = useState(1)
  const [day, setDay] = useState('Day1')

  // 当 todayData 加载完成后，设置默认值
  useMemo(() => {
    if (todayData && todayData.cycle && todayData.day) {
      setCycle(todayData.cycle)
      setDay(todayData.day)
    }
  }, [todayData])

  // 获取概览数据
  const { data: overview, isLoading: overviewLoading } = useVdimOverview()

  // 获取当前训练日数据
  const { data: dayData, isLoading: dayLoading, refetch: refetchDay } = useVdimDay(cycle, day)

  // 获取 playlist 配置（用于周期和日的选项）
  const { data: playlists } = useVdimPlaylists()

  // 补录分数弹窗
  const [scoreModalVisible, setScoreModalVisible] = useState(false)
  const [scoreForm] = Form.useForm()
  const [selectedScenario, setSelectedScenario] = useState(null)

  // 打卡
  const handleCheckin = async () => {
    try {
      const date = dayjs().format('YYYY-MM-DD')
      await createVdimCheckin(date, '')
      message.success('打卡成功！继续加油 💪')
      queryClient.invalidateQueries(['vdimOverview'])
      queryClient.invalidateQueries(['vdimToday'])
      refetchDay()
    } catch (error) {
      message.error(error.message || '打卡失败')
    }
  }

  // 打开补录分数弹窗
  const handleOpenScoreModal = (scenario) => {
    setSelectedScenario(scenario)
    scoreForm.setFieldsValue({
      scenario: scenario.scenario,
      score: scenario.latest_score || undefined,
    })
    setScoreModalVisible(true)
  }

  // 提交补录分数
  const handleSubmitScore = async () => {
    try {
      const values = await scoreForm.validateFields()
      await createVdimScore({
        cycle: cycle,
        day: day,
        scenario: values.scenario,
        score: values.score,
        date: dayjs().format('YYYY-MM-DD'),
        source: 'manual',
      })
      message.success('分数保存成功！')
      setScoreModalVisible(false)
      scoreForm.resetFields()
      refetchDay()
      queryClient.invalidateQueries(['vdimOverview'])
    } catch (error) {
      message.error(error.message || '保存失败')
    }
  }

  // 刷新
  const handleRefresh = () => {
    refetchDay()
    queryClient.invalidateQueries(['vdimOverview'])
    queryClient.invalidateQueries(['vdimToday'])
    message.success('已刷新')
  }

  // 基准场景表格列
  const benchmarkColumns = [
    {
      title: '场景',
      dataIndex: 'scenario',
      key: 'scenario',
      width: 280,
      render: (text) => (
        <Tooltip title={text}>
          <span style={{ cursor: 'pointer', color: '#1677ff' }}>{text}</span>
        </Tooltip>
      ),
    },
    {
      title: '最新分数',
      dataIndex: 'latest_score',
      key: 'latest_score',
      width: 100,
      render: (val) => val ? val.toFixed(1) : '-',
    },
    {
      title: '最佳分数',
      dataIndex: 'best_score',
      key: 'best_score',
      width: 100,
      render: (val) => val ? val.toFixed(1) : '-',
    },
    {
      title: '次数',
      dataIndex: 'train_count',
      key: 'train_count',
      width: 60,
    },
    {
      title: '当前档位',
      dataIndex: 'current_rank',
      key: 'current_rank',
      width: 100,
      render: (rank) => rank ? (
        <Tag color={RANK_COLOR[rank] || 'default'}>{rank}</Tag>
      ) : '-',
    },
    {
      title: '目标档位',
      dataIndex: 'target_rank',
      key: 'target_rank',
      width: 100,
      render: (rank) => rank ? (
        <Tag color={RANK_COLOR[rank] || 'default'}>{rank}</Tag>
      ) : '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status) => (
        <Tag color={STATUS_COLOR[status] || 'default'}>{status}</Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          icon={<PlusOutlined />}
          onClick={() => handleOpenScoreModal(record)}
        >
          补录
        </Button>
      ),
    },
  ]

  // 训练场景表格列
  const trainingColumns = [
    {
      title: '场景',
      dataIndex: 'scenario',
      key: 'scenario',
      width: 320,
      render: (text) => (
        <Tooltip title={text}>
          <span style={{ cursor: 'pointer', color: '#1677ff' }}>{text}</span>
        </Tooltip>
      ),
    },
    {
      title: '最新分数',
      dataIndex: 'latest_score',
      key: 'latest_score',
      width: 120,
      render: (val) => val ? val.toFixed(1) : '-',
    },
    {
      title: '最佳分数',
      dataIndex: 'best_score',
      key: 'best_score',
      width: 120,
      render: (val) => val ? val.toFixed(1) : '-',
    },
    {
      title: '次数',
      dataIndex: 'train_count',
      key: 'train_count',
      width: 80,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => (
        <Tag color={STATUS_COLOR[status] || 'default'}>{status}</Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          icon={<PlusOutlined />}
          onClick={() => handleOpenScoreModal(record)}
        >
          补录
        </Button>
      ),
    },
  ]

  const isToday = todayData && todayData.cycle === cycle && todayData.day === day
  const isRestDay = dayData?.is_rest_day

  return (
    <div>
      {/* 顶部操作栏 */}
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/daylist/Day3')}>
            返回练枪
          </Button>
          <Button icon={<BulbOutlined />} onClick={() => navigate('/reflection')}>
            感悟记录
          </Button>
          <Button icon={<TrophyOutlined />} onClick={() => navigate('/benchmark')}>
            基准总览
          </Button>
        </Space>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={handleRefresh}>刷新</Button>
        </Space>
      </div>

      {/* 概览卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日训练"
              value={todayData?.theme_label || '-'}
              prefix={<CalendarOutlined style={{ color: '#1677ff' }} />}
              valueStyle={{ fontSize: 20 }}
            />
            <div style={{ marginTop: 8, color: '#888', fontSize: 13 }}>
              第{todayData?.cycle || '-'}周 · {todayData?.day || '-'}
              {todayData?.checked_in && <Tag color="green" style={{ marginLeft: 8 }}>已打卡</Tag>}
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="连续打卡"
              value={overview?.streak_days || 0}
              suffix="天"
              prefix={<FireOutlined style={{ color: '#ff4d4f' }} />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="本周完成"
              value={overview?.week_done || 0}
              suffix={`/ ${overview?.week_total || 6}`}
              prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
            />
            <div style={{ marginTop: 8, color: '#888', fontSize: 13 }}>
              完成率 {overview?.week_percent || 0}%
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Gold Complete"
              value={overview?.gold_complete || 0}
              suffix={`/ ${overview?.gold_total || 12}`}
              prefix={<TrophyOutlined style={{ color: '#faad14' }} />}
            />
            <div style={{ marginTop: 8, color: '#888', fontSize: 13 }}>
              进度 {overview?.gold_percent || 0}%
            </div>
          </Card>
        </Col>
      </Row>

      {/* 周期和训练日选择器 */}
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <span style={{ fontWeight: 'bold' }}>周期：</span>
          <Select
            value={cycle}
            onChange={setCycle}
            style={{ width: 120 }}
          >
            {[1, 2, 3, 4, 5, 6, 7, 8].map(c => (
              <Option key={c} value={c}>第{c}周</Option>
            ))}
          </Select>

          <span style={{ fontWeight: 'bold', marginLeft: 16 }}>训练日：</span>
          <Select
            value={day}
            onChange={setDay}
            style={{ width: 200 }}
          >
            {playlists?.days?.map(d => (
              <Option key={d.day} value={d.day}>
                {d.day} - {d.theme_name}
              </Option>
            ))}
            <Option value="Day7">Day7 - 休息</Option>
          </Select>

          {isToday && (
            <Tag color="blue" style={{ marginLeft: 16 }}>今天</Tag>
          )}

          <div style={{ flex: 1 }} />

          {isToday && !dayData?.checked_in && !isRestDay && (
            <Button
              type="primary"
              icon={<CheckCircleOutlined />}
              onClick={handleCheckin}
            >
              今日打卡
            </Button>
          )}
          {dayData?.checked_in && (
            <Button type="primary" disabled icon={<CheckCircleOutlined />}>
              已打卡
            </Button>
          )}
        </Space>
      </Card>

      {/* 训练日详情 */}
      <Spin spinning={dayLoading}>
        {isRestDay ? (
          <Card>
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <div style={{ fontSize: 48, marginBottom: 16 }}>😴</div>
              <h2>今天是休息日</h2>
              <p style={{ color: '#888' }}>好好休息，明天继续加油！</p>
            </div>
          </Card>
        ) : (
          <>
            {/* 基准场景 */}
            <Card
              title={
                <Space>
                  <TrophyOutlined style={{ color: '#faad14' }} />
                  <span>基准场景</span>
                  <Tag color="gold">有档位对比</Tag>
                </Space>
              }
              style={{ marginBottom: 16 }}
            >
              <Table
                dataSource={dayData?.benchmark_scenarios || []}
                columns={benchmarkColumns}
                rowKey="scenario"
                size="small"
                pagination={false}
              />
            </Card>

            {/* 训练场景 */}
            <Card
              title={
                <Space>
                  <span>训练场景</span>
                  <Tag>专项训练</Tag>
                </Space>
              }
            >
              <Table
                dataSource={dayData?.training_scenarios || []}
                columns={trainingColumns}
                rowKey="scenario"
                size="small"
                pagination={false}
              />
            </Card>
          </>
        )}
      </Spin>

      {/* 补录分数弹窗 */}
      <Modal
        title="补录分数"
        open={scoreModalVisible}
        onCancel={() => setScoreModalVisible(false)}
        onOk={handleSubmitScore}
        okText="保存"
        cancelText="取消"
      >
        <Form form={scoreForm} layout="vertical">
          <Form.Item
            name="scenario"
            label="场景"
          >
            <InputNumber
              style={{ width: '100%' }}
              disabled
              formatter={value => value}
            />
          </Form.Item>
          <Form.Item
            name="score"
            label="分数"
            rules={[{ required: true, message: '请输入分数' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              min={0}
              placeholder="请输入分数"
            />
          </Form.Item>
          <div style={{ color: '#888', fontSize: 12 }}>
            第{cycle}周 · {day} · {selectedScenario?.scenario}
          </div>
        </Form>
      </Modal>
    </div>
  )
}
