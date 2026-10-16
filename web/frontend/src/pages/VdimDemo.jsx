import { useState } from 'react'
import { Select, Button, DatePicker, Table, Tag, Progress, Row, Col, Card, Divider } from 'antd'
import {
  ReloadOutlined, CheckCircleOutlined, ImportOutlined, EditOutlined,
  FileTextOutlined, LinkOutlined, FireOutlined, TrophyOutlined, CalendarOutlined,
  CopyOutlined, RocketOutlined
} from '@ant-design/icons'
import dayjs from 'dayjs'

const { RangePicker } = DatePicker

// 模拟数据 - 基准场景
const benchmarkScenarios = [
  { key: '1', order: 1, scenario: 'Controlsphere', category: 'Control Tracking', sub: 'Wrist', score: null, rank: 'Hare', nextRank: 'Ermine', gap: 461, status: '未开始' },
  { key: '2', order: 2, scenario: 'Smoothsphere', category: 'Control Tracking', sub: 'Arm', score: 9372, rank: 'Penguin', nextRank: 'Fox', gap: 628, status: '已完成' },
]

// 模拟数据 - 训练场景
const trainingScenarios = [
  { key: '1', order: 1, scenario: 'Revolving Tracking Slow', score: null, best: null, count: 0, status: '未开始' },
  { key: '2', order: 2, scenario: 'Centering II 180 no strafes easier', score: null, best: null, count: 0, status: '未开始' },
  { key: '3', order: 3, scenario: 'Smooth Thin Strafes Raspberry Easy', score: null, best: null, count: 0, status: '未开始' },
  { key: '4', order: 4, scenario: 'tamTargetSwitch Control', score: null, best: null, count: 0, status: '未开始' },
  { key: '5', order: 5, scenario: 'tamTargetSwitch Smooth', score: null, best: null, count: 0, status: '未开始' },
  { key: '6', order: 6, scenario: 'VT Smoothbot Novice', score: null, best: null, count: 0, status: '未开始' },
  { key: '7', order: 7, scenario: 'e1se Glider 30s Normal', score: null, best: null, count: 0, status: '未开始' },
  { key: '8', order: 8, scenario: 'B360TI Sparky', score: null, best: null, count: 0, status: '未开始' },
  { key: '9', order: 9, scenario: 'vertical smoothness training popcorn', score: null, best: null, count: 0, status: '未开始' },
  { key: '10', order: 10, scenario: 'PGTI Voltaic Easy 100% Bigger', score: null, best: null, count: 0, status: '未开始' },
  { key: '11', order: 11, scenario: 'VT PreciseOrb Intermediate 20% Slower', score: null, best: null, count: 0, status: '未开始' },
  { key: '12', order: 12, scenario: 'PGTI Voltaic Easy UFO', score: null, best: null, count: 0, status: '未开始' },
  { key: '13', order: 13, scenario: 'VT PreciseOrb Intermediate Small', score: null, best: null, count: 0, status: '未开始' },
  { key: '14', order: 14, scenario: 'VT PreciseOrb Novice', score: null, best: null, count: 0, status: '未开始' },
]

// 周期选项
const cycleOptions = [
  { value: 1, label: '第1周 (10/09 - 10/15)' },
  { value: 2, label: '第2周 (10/16 - 10/22)' },
  { value: 3, label: '第3周 (10/23 - 10/29)' },
  { value: 4, label: '第4周 (10/30 - 11/05)' },
]

// 训练日选项
const dayOptions = [
  { value: 'Day1', label: 'Day1 · 平滑跟枪' },
  { value: 'Day2', label: 'Day2 · 反应跟枪' },
  { value: 'Day3', label: 'Day3 · 速度转火' },
  { value: 'Day4', label: 'Day4 · 移动瞄准' },
  { value: 'Day5', label: 'Day5 · 动态点击' },
  { value: 'Day6', label: 'Day6 · 静态点击' },
  { value: 'Day7', label: 'Day7 · 休息' },
]

// 档位颜色
const rankColors = {
  'Lemming': 'default',
  'Hare': 'orange',
  'Ermine': 'gold',
  'Penguin': 'blue',
  'Fox': 'purple',
}

export default function VdimDemo() {
  const [selectedCycle, setSelectedCycle] = useState(1)
  const [selectedDay, setSelectedDay] = useState('Day1')
  const [dateRange, setDateRange] = useState([dayjs(), dayjs()])

  // 基准场景表格列
  const benchmarkColumns = [
    { title: '顺序', dataIndex: 'order', key: 'order', width: 60 },
    {
      title: '场景名', dataIndex: 'scenario', key: 'scenario',
      render: (text) => <a>{text}</a>
    },
    { title: '分类', dataIndex: 'category', key: 'category', width: 140 },
    { title: '子类', dataIndex: 'sub', key: 'sub', width: 100 },
    {
      title: '最新分数', dataIndex: 'score', key: 'score', width: 100,
      render: (v) => v || <span style={{ color: '#bfbfbf' }}>—</span>
    },
    {
      title: '档位', dataIndex: 'rank', key: 'rank', width: 80,
      render: (v) => <Tag color={rankColors[v]}>{v}</Tag>
    },
    { title: '下一档位', dataIndex: 'nextRank', key: 'nextRank', width: 80 },
    {
      title: '差距', dataIndex: 'gap', key: 'gap', width: 80,
      render: (v) => <span style={{ color: '#fa8c16' }}>+{v}</span>
    },
    {
      title: '状态', dataIndex: 'status', key: 'status', width: 80,
      render: (v) => <Tag color={v === '已完成' ? 'green' : 'default'}>{v}</Tag>
    },
  ]

  // 训练场景表格列
  const trainingColumns = [
    { title: '顺序', dataIndex: 'order', key: 'order', width: 60 },
    {
      title: '场景名', dataIndex: 'scenario', key: 'scenario',
      render: (text) => <a>{text}</a>
    },
    {
      title: '最新分数', dataIndex: 'score', key: 'score', width: 100,
      render: (v) => v || <span style={{ color: '#bfbfbf' }}>—</span>
    },
    {
      title: '历史最高', dataIndex: 'best', key: 'best', width: 100,
      render: (v) => v || <span style={{ color: '#bfbfbf' }}>—</span>
    },
    { title: '训练次数', dataIndex: 'count', key: 'count', width: 80 },
    {
      title: '状态', dataIndex: 'status', key: 'status', width: 80,
      render: (v) => <Tag color={v === '已完成' ? 'green' : 'default'}>{v}</Tag>
    },
  ]

  return (
    <div>
      {/* 过滤器栏 */}
      <div style={{ marginBottom: '24px', display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
        <Select
          value={selectedCycle}
          onChange={setSelectedCycle}
          style={{ width: 220 }}
          options={cycleOptions}
          suffixIcon={<CalendarOutlined />}
          placeholder="选择周期"
        />
        <Select
          value={selectedDay}
          onChange={setSelectedDay}
          style={{ width: 200 }}
          options={dayOptions}
          placeholder="选择训练日"
        />
        <RangePicker value={dateRange} onChange={setDateRange} />
        <Button type="primary" icon={<ReloadOutlined />}>刷新</Button>
        <div style={{ marginLeft: 'auto', color: 'rgba(0,0,0,0.45)', fontSize: '13px' }}>
          当前：第{selectedCycle}周 · {selectedDay} · 平滑跟枪
        </div>
      </div>

      {/* 概览统计卡片 - 4个（用基础div，不用Statistic） */}
      <Row gutter={16} style={{ marginBottom: '16px' }}>
        <Col span={6}>
          <Card>
            <div style={{ color: 'rgba(0,0,0,0.45)', fontSize: 14, marginBottom: 8 }}>
              <FireOutlined style={{ marginRight: 4 }} /> 今天练什么
            </div>
            <div style={{ fontSize: 18, fontWeight: 600, color: 'rgba(0,0,0,0.88)' }}>
              Day1 · 平滑跟枪
            </div>
            <div style={{ marginTop: 8, fontSize: 12, color: 'rgba(0,0,0,0.45)' }}>
              分享码：<code style={{ background: '#f5f5f5', padding: '2px 6px', borderRadius: 4, fontSize: 11 }}>KovaaKsStrikingAfkBm</code>
              <Button type="link" size="small" style={{ padding: '0 4px', fontSize: 12 }} icon={<CopyOutlined />}>复制</Button>
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <div style={{ color: 'rgba(0,0,0,0.45)', fontSize: 14, marginBottom: 8 }}>连续打卡</div>
            <div style={{ fontSize: 24, fontWeight: 600, color: '#fa8c16' }}>🔥 0 天</div>
            <div style={{ marginTop: 4, fontSize: 12, color: 'rgba(0,0,0,0.45)' }}>今天还没练 · 第1周</div>
            <Progress percent={0} size="small" style={{ marginTop: 8 }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <div style={{ color: 'rgba(0,0,0,0.45)', fontSize: 14, marginBottom: 8 }}>本周完成率</div>
            <div style={{ fontSize: 24, fontWeight: 600, color: '#1677ff' }}>0/6</div>
            <div style={{ marginTop: 4, fontSize: 12, color: 'rgba(0,0,0,0.45)' }}>0% · 6 天训练 + 1 天休息</div>
            <Progress percent={0} size="small" style={{ marginTop: 8 }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <div style={{ color: 'rgba(0,0,0,0.45)', fontSize: 14, marginBottom: 8 }}>
              <TrophyOutlined style={{ marginRight: 4 }} /> Gold Complete
            </div>
            <div style={{ fontSize: 24, fontWeight: 600, color: '#d4b106' }}>10/12</div>
            <div style={{ marginTop: 4, fontSize: 12, color: 'rgba(0,0,0,0.45)' }}>83% · 差 Wrist, Reading</div>
            <Progress percent={83} size="small" strokeColor="#d4b106" style={{ marginTop: 8 }} />
          </Card>
        </Col>
      </Row>

      {/* 训练日详情卡片 */}
      <Card style={{ marginBottom: 16 }}>
        <Row justify="space-between" align="top">
          <Col>
            <h2 style={{ margin: '0 0 8px', fontSize: 20 }}>🎯 Day1：平滑跟枪 (Smooth Tracking)</h2>
            <p style={{ margin: 0, color: 'rgba(0,0,0,0.65)', fontSize: 14 }}>
              你的最弱主题，Wrist 子类整体 Hare，Whisphere 是唯一的 Lemming。重点提升手腕控制和平滑跟枪能力。
            </p>
          </Col>
          <Col style={{ textAlign: 'right', fontSize: 13, color: 'rgba(0,0,0,0.45)' }}>
            <div>推荐 FOV：<span style={{ color: 'rgba(0,0,0,0.88)' }}>103</span></div>
            <div>推荐灵敏度：<span style={{ color: 'rgba(0,0,0,0.88)' }}>20 - 50cm/360</span></div>
            <div>场景数：<span style={{ color: 'rgba(0,0,0,0.88)' }}>16 个（2基准 + 14训练）</span></div>
          </Col>
        </Row>
        <Divider style={{ margin: '16px 0' }} />
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <span style={{ fontSize: 13, color: 'rgba(0,0,0,0.45)' }}>分享码：</span>
          <code style={{ background: '#f5f5f5', padding: '4px 12px', borderRadius: 6, fontSize: 13, color: '#52c41a' }}>KovaaKsStrikingAfkBm</code>
          <Button type="primary" size="small" icon={<CopyOutlined />}>复制分享码</Button>
          <Button size="small" icon={<RocketOutlined />}>在 Kovaak's 中打开</Button>
          <Tag color="blue">Novice 级别</Tag>
          <Tag color="purple">LG56 版</Tag>
        </div>
      </Card>

      {/* 操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <Button type="primary" icon={<CheckCircleOutlined />} size="large">今天练了！打卡</Button>
          <Button icon={<ImportOutlined />} size="large">从 stats 导入分数</Button>
          <Button icon={<EditOutlined />} size="large">手动补录分数</Button>
          <Button icon={<FileTextOutlined />} size="large">写训练感悟</Button>
          <div style={{ marginLeft: 'auto', fontSize: 12, color: 'rgba(0,0,0,0.45)' }}>
            💡 练完后点"从 stats 导入"自动识别；补录按训练日 Day 归类，不按实际日期
          </div>
        </div>
      </Card>

      {/* 基准场景表格 */}
      <div style={{ fontSize: 16, fontWeight: 600, margin: '24px 0 16px', display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ display: 'inline-block', width: 3, height: 16, background: '#d4b106', borderRadius: 2 }}></span>
        基准场景（有档位对比）
        <Tag color="default">2 个</Tag>
        <span style={{ fontSize: 12, color: 'rgba(0,0,0,0.45)', fontWeight: 'normal' }}>和 Viscose 基准共用档位线，点击场景名查看详情</span>
      </div>
      <Table columns={benchmarkColumns} dataSource={benchmarkScenarios} pagination={false} size="middle" />

      {/* 训练场景表格 */}
      <div style={{ fontSize: 16, fontWeight: 600, margin: '24px 0 16px', display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ display: 'inline-block', width: 3, height: 16, background: '#1677ff', borderRadius: 2 }}></span>
        训练场景（只有分数，无档位）
        <Tag color="default">14 个</Tag>
        <span style={{ fontSize: 12, color: 'rgba(0,0,0,0.45)', fontWeight: 'normal' }}>纯练动作的基础场景，不对比档位，只记录分数和进步</span>
      </div>
      <Table columns={trainingColumns} dataSource={trainingScenarios} pagination={false} size="middle" />

      {/* 和现有页面的链接 */}
      <Card style={{ marginTop: 24 }} title={<span><LinkOutlined style={{ marginRight: 8 }} />相关页面跳转</span>}>
        <Row gutter={16}>
          <Col span={8}>
            <Card size="small" hoverable>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>📊 Viscose 基准总览</div>
              <div style={{ fontSize: 12, color: 'rgba(0,0,0,0.45)', marginBottom: 8 }}>查看完整基准测试结果、档位分布、12子类进度</div>
              <Button type="link" style={{ padding: 0, fontSize: 12 }}>前往基准总览 →</Button>
            </Card>
          </Col>
          <Col span={8}>
            <Card size="small" hoverable>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>📝 游戏感悟</div>
              <div style={{ fontSize: 12, color: 'rgba(0,0,0,0.45)', marginBottom: 8 }}>查看所有训练感悟（VDIM + Viscose + 游戏），按场景和日期筛选</div>
              <Button type="link" style={{ padding: 0, fontSize: 12 }}>前往感悟页面 →</Button>
            </Card>
          </Col>
          <Col span={8}>
            <Card size="small" hoverable>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>📋 Viscose 今日清单</div>
              <div style={{ fontSize: 12, color: 'rgba(0,0,0,0.45)', marginBottom: 8 }}>查看定制的弱项攻坚清单，和 VDIM 系统训练互补</div>
              <Button type="link" style={{ padding: 0, fontSize: 12 }}>前往今日清单 →</Button>
            </Card>
          </Col>
        </Row>
      </Card>

      {/* 第二版预留 */}
      <div style={{ marginTop: 24, padding: 20, background: '#fafafa', borderRadius: 8, border: '1px dashed #d9d9d9' }}>
        <div style={{ fontWeight: 600, color: 'rgba(0,0,0,0.45)', marginBottom: 12 }}>📈 进度追踪区（第二版实现）</div>
        <Row gutter={16}>
          <Col span={8}>
            <div style={{ textAlign: 'center', padding: 16, background: '#fff', borderRadius: 6 }}>
              <div style={{ fontSize: 24, marginBottom: 8 }}>📈</div>
              <div style={{ fontSize: 13, color: 'rgba(0,0,0,0.45)' }}>6 大主题进步曲线</div>
            </div>
          </Col>
          <Col span={8}>
            <div style={{ textAlign: 'center', padding: 16, background: '#fff', borderRadius: 6 }}>
              <div style={{ fontSize: 24, marginBottom: 8 }}>🏆</div>
              <div style={{ fontSize: 13, color: 'rgba(0,0,0,0.45)' }}>Gold Complete 可视化</div>
            </div>
          </Col>
          <Col span={8}>
            <div style={{ textAlign: 'center', padding: 16, background: '#fff', borderRadius: 6 }}>
              <div style={{ fontSize: 24, marginBottom: 8 }}>📊</div>
              <div style={{ fontSize: 13, color: 'rgba(0,0,0,0.45)' }}>基准测试对比（起点→第2次→第4次）</div>
            </div>
          </Col>
        </Row>
      </div>

      <div style={{ textAlign: 'center', color: 'rgba(0,0,0,0.25)', fontSize: 12, padding: '24px 0' }}>
        VDIM 训练记录页面 Demo · 临时预览版 · 数据为模拟数据
      </div>
    </div>
  )
}
