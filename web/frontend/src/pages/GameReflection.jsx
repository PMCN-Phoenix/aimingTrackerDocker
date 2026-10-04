import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Card, Row, Col, Statistic, Tag, Button, Space, Typography,
  Empty, Modal, Form, Input, Select, DatePicker, message, Popconfirm
} from 'antd'
import {
  PlusOutlined, DeleteOutlined, EditOutlined,
  CalendarOutlined, FireOutlined, BookOutlined, AppstoreOutlined
} from '@ant-design/icons'
import dayjs from 'dayjs'
import {
  getGameReflections, getGameReflectionStats, createGameReflection,
  updateGameReflection, deleteGameReflection, getWarmupItems,
  THEME_CONFIG, GAME_CONFIG
} from '../api/gameReflection'

const { Title, Text, Paragraph } = Typography
const { TextArea } = Input
const { Option } = Select

export default function GameReflection() {
  const queryClient = useQueryClient()
  const [selectedTheme, setSelectedTheme] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [expandedWarmup, setExpandedWarmup] = useState(null)
  const [form] = Form.useForm()

  // 获取统计数据
  const { data: statsData } = useQuery({
    queryKey: ['gameReflectionStats'],
    queryFn: getGameReflectionStats,
  })
  const stats = statsData?.data || {}

  // 获取热身项目列表
  const { data: warmupData } = useQuery({
    queryKey: ['warmupItems'],
    queryFn: getWarmupItems,
  })
  const warmupItems = warmupData?.data || []

  // 获取感悟列表
  const { data: listData, isLoading } = useQuery({
    queryKey: ['gameReflections', selectedTheme],
    queryFn: () => getGameReflections({ theme: selectedTheme, limit: 100 }),
  })
  const reflections = listData?.data?.items || []

  // 创建/更新 mutation
  const createMutation = useMutation({
    mutationFn: (payload) => editingId
      ? updateGameReflection(editingId, payload)
      : createGameReflection(payload),
    onSuccess: () => {
      message.success(editingId ? '更新成功' : '创建成功')
      setModalOpen(false)
      setEditingId(null)
      form.resetFields()
      queryClient.invalidateQueries(['gameReflections'])
      queryClient.invalidateQueries(['gameReflectionStats'])
    },
    onError: (error) => {
      message.error(error.response?.data?.message || '操作失败')
    },
  })

  // 删除 mutation
  const deleteMutation = useMutation({
    mutationFn: deleteGameReflection,
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries(['gameReflections'])
      queryClient.invalidateQueries(['gameReflectionStats'])
    },
    onError: (error) => {
      message.error(error.response?.data?.message || '删除失败')
    },
  })

  const handleOpenCreate = () => {
    setEditingId(null)
    form.resetFields()
    form.setFieldsValue({
      date: dayjs(),
      theme: 'aim',
      game: 'valorant',
      tags: [],
    })
    setModalOpen(true)
  }

  const handleOpenEdit = (reflection) => {
    setEditingId(reflection.id)
    form.setFieldsValue({
      ...reflection,
      date: reflection.date ? dayjs(reflection.date) : null,
      tags: reflection.tags || [],
    })
    setModalOpen(true)
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      const payload = {
        ...values,
        date: values.date.format('YYYY-MM-DD'),
        tags: values.tags || [],
      }
      createMutation.mutate(payload)
    } catch (error) {
      console.error('表单验证失败:', error)
    }
  }

  return (
    <div>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={3} style={{ margin: 0 }}>📝 游戏感悟</Title>
          <Text type="secondary">记录游戏中的心得体会、技巧感悟和成长思考</Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCreate}>
          新增感悟
        </Button>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="感悟总数"
              value={stats.total_count || 0}
              prefix={<BookOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日新增"
              value={stats.today_count || 0}
              prefix={<CalendarOutlined />}
              valueStyle={{ color: '#3b82f6' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="连续记录"
              value={stats.consecutive_days || 0}
              suffix="天"
              prefix={<FireOutlined />}
              valueStyle={{ color: '#ef4444' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="覆盖主题"
              value={stats.theme_count || 0}
              suffix="类"
              prefix={<AppstoreOutlined />}
              valueStyle={{ color: '#10b981' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 热身项目区域 */}
      {warmupItems.length > 0 && (
        <Card
          title={<span>🔥 热身项目</span>}
          style={{ marginBottom: 24 }}
          extra={<Text type="secondary">共 {warmupItems.length} 个项目</Text>}
        >
          <Row gutter={[16, 16]}>
            {warmupItems.map((item) => (
              <Col span={12} key={item.id}>
                <Card
                  size="small"
                  hoverable
                  onClick={() => setExpandedWarmup(expandedWarmup === item.id ? null : item.id)}
                  style={{
                    borderColor: expandedWarmup === item.id ? '#ef4444' : undefined,
                    cursor: 'pointer',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <Text strong style={{ fontSize: 15 }}>{item.name}</Text>
                      {item.description && (
                        <div>
                          <Text type="secondary" style={{ fontSize: 12 }}>{item.description}</Text>
                        </div>
                      )}
                    </div>
                    <Space>
                      <Tag color="orange">{item.type === 'tracking' ? '跟枪' : item.type === 'reaction' ? '反应' : item.type}</Tag>
                      <Tag color="red">{item.reflections?.length || 0} 条感悟</Tag>
                    </Space>
                  </div>
                  {expandedWarmup === item.id && item.reflections?.length > 0 && (
                    <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid #f0f0f0' }}>
                      {item.reflections.map((ref, idx) => (
                        <div key={ref.id || idx} style={{ marginBottom: idx < item.reflections.length - 1 ? 12 : 0 }}>
                          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
                            <Text strong style={{ fontSize: 14, color: '#ef4444' }}>{ref.title}</Text>
                            <Text type="secondary" style={{ fontSize: 12, marginLeft: 8 }}>📅 {ref.date}</Text>
                          </div>
                          <Paragraph style={{ marginBottom: 4, whiteSpace: 'pre-wrap', fontSize: 13 }}>
                            {ref.content}
                          </Paragraph>
                          <Space wrap size={4}>
                            {(ref.tags || []).map((tag, tagIdx) => (
                              <Tag key={tagIdx} color="orange" style={{ fontSize: 11 }}>{tag}</Tag>
                            ))}
                          </Space>
                        </div>
                      ))}
                    </div>
                  )}
                  {expandedWarmup === item.id && (!item.reflections || item.reflections.length === 0) && (
                    <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid #f0f0f0' }}>
                      <Text type="secondary">暂无感悟记录</Text>
                    </div>
                  )}
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {/* 主题筛选 */}
      <Card style={{ marginBottom: 24 }}>
        <Space wrap>
          <Tag
            color={selectedTheme === null ? 'blue' : 'default'}
            style={{ cursor: 'pointer', fontSize: 14, padding: '4px 12px' }}
            onClick={() => setSelectedTheme(null)}
          >
            全部
          </Tag>
          {Object.entries(THEME_CONFIG).map(([key, config]) => (
            <Tag
              key={key}
              color={selectedTheme === key ? config.color : 'default'}
              style={{
                cursor: 'pointer',
                fontSize: 14,
                padding: '4px 12px',
                borderColor: selectedTheme === key ? config.color : undefined,
              }}
              onClick={() => setSelectedTheme(selectedTheme === key ? null : key)}
            >
              {config.icon} {config.name}
              {stats.theme_distribution?.[key] ? ` (${stats.theme_distribution[key]})` : ''}
            </Tag>
          ))}
        </Space>
      </Card>

      {/* 感悟列表 */}
      {isLoading ? (
        <Card>
          <Empty description="加载中..." />
        </Card>
      ) : reflections.length === 0 ? (
        <Card>
          <Empty
            description="还没有感悟记录"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          >
            <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCreate}>
              写下第一条感悟
            </Button>
          </Empty>
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          {reflections.map((reflection) => {
            const themeConfig = THEME_CONFIG[reflection.theme] || THEME_CONFIG.mindset
            return (
              <Col span={12} key={reflection.id}>
                <Card
                  hoverable
                  actions={[
                    <EditOutlined key="edit" onClick={() => handleOpenEdit(reflection)} />,
                    <Popconfirm
                      key="delete"
                      title="确定删除这条感悟吗？"
                      onConfirm={() => deleteMutation.mutate(reflection.id)}
                      okText="删除"
                      cancelText="取消"
                    >
                      <DeleteOutlined />
                    </Popconfirm>,
                  ]}
                >
                  <Card.Meta
                    title={
                      <Space>
                        <span style={{ fontSize: 18 }}>{themeConfig.icon}</span>
                        <span>{reflection.title}</span>
                      </Space>
                    }
                    description={
                      <Space direction="vertical" size={8} style={{ width: '100%' }}>
                        <Space wrap>
                          <Tag color={themeConfig.color}>{themeConfig.name}</Tag>
                          <Tag>{GAME_CONFIG[reflection.game]?.name || reflection.game}</Tag>
                          {reflection.mode && <Tag>{reflection.mode}</Tag>}
                          {reflection.map_name && <Tag>🗺️ {reflection.map_name}</Tag>}
                          {reflection.agent_name && <Tag>🎭 {reflection.agent_name}</Tag>}
                          {reflection.warmup_item && <Tag color="orange">🔥 {reflection.warmup_item}</Tag>}
                        </Space>
                        <Paragraph
                          ellipsis={{ rows: 3, expandable: true, symbol: '展开' }}
                          style={{ marginBottom: 0, whiteSpace: 'pre-wrap' }}
                        >
                          {reflection.content}
                        </Paragraph>
                        <Space wrap>
                          {(reflection.tags || []).map((tag, idx) => (
                            <Tag key={idx} color="blue">{tag}</Tag>
                          ))}
                        </Space>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          📅 {reflection.date} | ID: {reflection.id}
                        </Text>
                      </Space>
                    }
                  />
                </Card>
              </Col>
            )
          })}
        </Row>
      )}

      {/* 新增/编辑弹窗 */}
      <Modal
        title={editingId ? '编辑感悟' : '新增感悟'}
        open={modalOpen}
        onOk={handleSubmit}
        onCancel={() => {
          setModalOpen(false)
          setEditingId(null)
          form.resetFields()
        }}
        confirmLoading={createMutation.isPending}
        width={700}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="title"
            label="标题"
            rules={[{ required: true, message: '请输入标题' }]}
          >
            <Input placeholder="简短概括这条感悟" maxLength={100} showCount />
          </Form.Item>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="theme"
                label="主题"
                rules={[{ required: true, message: '请选择主题' }]}
              >
                <Select>
                  {Object.entries(THEME_CONFIG).map(([key, config]) => (
                    <Option key={key} value={key}>
                      {config.icon} {config.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="game"
                label="游戏"
                rules={[{ required: true, message: '请选择游戏' }]}
              >
                <Select>
                  {Object.entries(GAME_CONFIG).map(([key, config]) => (
                    <Option key={key} value={key}>
                      {config.icon} {config.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="date"
                label="日期"
                rules={[{ required: true, message: '请选择日期' }]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="mode" label="模式">
                <Input placeholder="如：排位、死斗、匹配" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="map_name" label="地图">
                <Input placeholder="如：Ascent、Haven" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="agent_name" label="英雄/角色">
                <Input placeholder="如：Jett、Phoenix" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="warmup_item" label="热身项目（仅热身主题填写）">
            <Input placeholder="如：靶场平移机器人跟踪定位" />
          </Form.Item>

          <Form.Item
            name="content"
            label="感悟内容"
            rules={[{ required: true, message: '请输入感悟内容' }]}
          >
            <TextArea
              rows={6}
              placeholder="详细记录你的心得体会、技巧感悟或成长思考..."
              maxLength={2000}
              showCount
            />
          </Form.Item>

          <Form.Item name="tags" label="标签">
            <Select
              mode="tags"
              placeholder="输入标签后按回车，如：#预瞄、#急停"
              tokenSeparators={[',', ' ']}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
