import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button, message, Modal, Form, Input, InputNumber, Skeleton, Empty, Collapse, theme } from 'antd'
import { PlusOutlined, DownOutlined, UpOutlined, FireOutlined } from '@ant-design/icons'
import { useDaylists, useDaylistProgress, useDaylistExtras } from '../api/hooks'
import { createExtraDaylist, deleteExtraDaylist, exportPlaylist } from '../api/client'
import ContextBar from '../components/ContextBar'
import SummaryStrip from '../components/SummaryStrip'
import MultiDimComparisonChart from '../components/MultiDimComparisonChart'
import DaylistRow from '../components/DaylistRow'
import ScenarioDrawer from '../components/ScenarioDrawer'
import ExtraDaylistCard from '../components/ExtraDaylistCard'
import { useAppTheme } from '../theme/ThemeContext'

export default function DaylistDashboard() {
  const { token } = theme.useToken()
  const { isDark } = useAppTheme()
  const { daylistId } = useParams()
  const navigate = useNavigate()

  // 密度偏好，持久化存入 localStorage
  const [density, setDensity] = useState(() => {
    return localStorage.getItem('daylistDensity') || 'card'
  })

  // 多维对比图显隐状态
  const [showMultiDim, setShowMultiDim] = useState(true)

  // 场景抽屉状态
  const [selectedScenario, setSelectedScenario] = useState(null)
  const [selectedRow, setSelectedRow] = useState(null)
  const [drawerOpen, setDrawerOpen] = useState(false)

  // 加练折叠状态（默认折叠）
  const [extrasOpen, setExtrasOpen] = useState(false)
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [form] = Form.useForm()

  // 获取清单列表
  const { data: daylists, isLoading: daylistsLoading } = useDaylists()

  // 获取当前清单的进度数据（含 round_stats 与 session）
  const {
    data: progressData,
    isLoading: progressLoading,
    isFetching: progressFetching,
    refetch,
  } = useDaylistProgress(daylistId)

  // 获取加练清单列表
  const {
    data: extrasData,
    isLoading: extrasLoading,
    refetch: refetchExtras,
  } = useDaylistExtras(daylistId)

  // 切换清单
  const handleDaylistChange = (value) => {
    navigate(`/daylist/${value}`)
  }

  // 切换展示密度
  const handleDensityChange = (value) => {
    setDensity(value)
    localStorage.setItem('daylistDensity', value)
  }

  // 点击场景打开抽屉
  const handleScenarioClick = (scenarioName) => {
    const row = progressData?.rows?.find((r) => r.scenario === scenarioName)
    setSelectedScenario(scenarioName)
    setSelectedRow(row || null)
    setDrawerOpen(true)
  }

  // 关闭抽屉
  const handleDrawerClose = () => {
    setDrawerOpen(false)
    setSelectedScenario(null)
    setSelectedRow(null)
  }

  // 导出主清单 Playlist 到 Kovaak's
  const handleExportMain = async () => {
    try {
      setExporting(true)
      const result = await exportPlaylist(daylistId)
      if (result.copied_to_kovaaks) {
        message.success(`已导出到 Kovaak's：${result.filename}`)
      } else {
        message.success(`已生成 playlist：${result.temp_path}`)
      }
    } catch (error) {
      message.error(error.message || '导出失败')
    } finally {
      setExporting(false)
    }
  }

  // 创建加练清单
  const handleCreateExtra = async () => {
    try {
      const values = await form.validateFields()
      const items = [
        {
          scenario: values.scenario,
          role: values.role || '主攻',
          rounds: values.rounds || 4,
          order: 1,
        },
      ]
      await createExtraDaylist({
        parent_daylist: daylistId,
        name: values.name,
        exec_dates: progressData?.exec_dates || progressData?.run_date || '',
        items: items,
      })
      message.success('加练清单创建成功！')
      setCreateModalVisible(false)
      form.resetFields()
      setExtrasOpen(true)
      refetchExtras()
    } catch (error) {
      message.error(error.message || '创建失败')
    }
  }

  // 删除加练清单
  const handleDeleteExtra = async (extraId) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个加练清单吗？（成绩数据不会被删除）',
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteExtraDaylist(extraId)
          message.success('删除成功！')
          refetchExtras()
        } catch (error) {
          message.error(error.message || '删除失败')
        }
      },
    })
  }

  // 导出加练清单到 Kovaak's
  const handleExportExtra = async (extraData) => {
    try {
      const result = await exportPlaylist(extraData.daylist, extraData.name)
      if (result.copied_to_kovaaks) {
        message.success(`已导出到 Kovaak's：${result.filename}`)
      } else {
        message.success(`已生成 playlist：${result.temp_path}`)
      }
    } catch (error) {
      message.error(error.message || '导出失败')
    }
  }

  const rows = progressData?.rows || []
  const extrasCount = extrasData?.length || 0

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', paddingBottom: '40px' }}>
      {/* ① 顶部上下文条 */}
      <ContextBar
        daylistId={daylistId}
        daylists={daylists || []}
        onDaylistChange={handleDaylistChange}
        runDate={progressData?.run_date || progressData?.exec_dates}
        session={progressData?.session}
        density={density}
        onDensityChange={handleDensityChange}
        showMultiDim={showMultiDim}
        onToggleMultiDim={() => setShowMultiDim(!showMultiDim)}
        onRefresh={() => {
          refetch()
          refetchExtras()
        }}
        onExport={handleExportMain}
        isRefreshing={progressFetching}
        isExporting={exporting}
      />

      {/* 骨架屏加载态，避免切换整页闪白 */}
      {progressLoading || daylistsLoading ? (
        <div style={{ background: '#fff', padding: '24px', borderRadius: '10px' }}>
          <Skeleton active paragraph={{ rows: 6 }} />
        </div>
      ) : (
        <>
          {/* ② 汇总卡条（4格） */}
          <SummaryStrip rows={rows} roundsTotal={progressData?.rounds_total} />

          {/* ②.5 能力多维对比分析图（当前 vs 历史 vs 目标） */}
          {showMultiDim && <MultiDimComparisonChart rows={rows} />}

          {/* ③ 清单主体 */}
          <div style={{ marginBottom: '28px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 700, color: token.colorText }}>
                📋 今日清单 · {progressData?.label || daylistId}
                <span style={{ fontSize: '13px', color: token.colorTextSecondary, fontWeight: 500, marginLeft: '8px' }}>
                  ({rows.length} 个训练场景)
                </span>
              </h3>
            </div>

            {/* 紧凑表模式下的表头 */}
            {density === 'compact' && rows.length > 0 && (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '8px 14px',
                  background: token.colorFillAlter,
                  borderRadius: '6px 6px 0 0',
                  border: `1px solid ${token.colorBorderSecondary}`,
                  borderBottom: 'none',
                  fontSize: '12px',
                  color: token.colorTextSecondary,
                  fontWeight: 600,
                }}
              >
                <span style={{ width: '24px' }}>#</span>
                <span style={{ width: '42px', textAlign: 'center' }}>角色</span>
                <span style={{ flex: 1 }}>场景名称</span>
                <span style={{ width: '90px', textAlign: 'right' }}>训练轮数</span>
                <span style={{ width: '150px', textAlign: 'right' }}>最佳 / 下一档线</span>
                <span style={{ width: '70px', textAlign: 'right' }}>命中率</span>
                <span style={{ width: '85px', textAlign: 'right' }}>后段衰减</span>
                <span style={{ width: '60px', textAlign: 'center' }}>状态</span>
              </div>
            )}

            {/* 场景列表渲染 */}
            {rows.length > 0 ? (
              <div style={density === 'compact' ? { border: `1px solid ${token.colorBorderSecondary}`, borderRadius: '0 0 6px 6px', overflow: 'hidden' } : {}}>
                {rows.map((row) => (
                  <DaylistRow
                    key={row.scenario}
                    row={row}
                    mode={density}
                    onClick={handleScenarioClick}
                  />
                ))}
              </div>
            ) : (
              <div style={{ background: token.colorBgContainer, padding: '40px', borderRadius: '10px', textAlign: 'center', border: `1px solid ${token.colorBorderSecondary}` }}>
                <Empty description="该清单尚未录入场景行，请检查 Viscose基准 游玩清单配置" />
              </div>
            )}
          </div>

          {/* ④ 加练清单区域（移至主表后，默认折叠） */}
          <div
            style={{
              background: token.colorBgContainer,
              borderRadius: '10px',
              border: `1px solid ${token.colorBorderSecondary}`,
              padding: '16px 20px',
              marginBottom: '28px',
              boxShadow: isDark ? '0 2px 8px rgba(0,0,0,0.2)' : '0 1px 3px rgba(0,0,0,0.02)',
              transition: 'background 0.3s, border-color 0.3s',
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                cursor: 'pointer',
              }}
              onClick={() => setExtrasOpen(!extrasOpen)}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FireOutlined style={{ color: '#a855f7', fontSize: '18px' }} />
                <span style={{ fontSize: '15px', fontWeight: 700, color: isDark ? '#c084fc' : '#722ed1' }}>
                  加练清单（{extrasCount} 个）
                </span>
                <span style={{ fontSize: '12px', color: token.colorTextSecondary }}>
                  {extrasOpen ? '点击收起' : '点击展开查看或新增加练'}
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Button
                  size="small"
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={(e) => {
                    e.stopPropagation()
                    setCreateModalVisible(true)
                  }}
                  style={{ background: '#722ed1', borderColor: '#722ed1' }}
                >
                  新增加练
                </Button>
                {extrasOpen ? <UpOutlined style={{ color: token.colorTextSecondary }} /> : <DownOutlined style={{ color: token.colorTextSecondary }} />}
              </div>
            </div>

            {/* 加练卡片列表 */}
            {extrasOpen && (
              <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: `1px solid ${token.colorBorderSecondary}` }}>
                {extrasLoading ? (
                  <Skeleton active paragraph={{ rows: 2 }} />
                ) : extrasData && extrasData.length > 0 ? (
                  extrasData.map((extra) => (
                    <ExtraDaylistCard
                      key={extra.daylist}
                      extraData={extra}
                      onScenarioClick={handleScenarioClick}
                      onEdit={() => message.info('编辑功能开发中...')}
                      onExport={() => handleExportExtra(extra)}
                      onDelete={() => handleDeleteExtra(extra.daylist)}
                    />
                  ))
                ) : (
                  <div
                    style={{
                      padding: '30px',
                      textAlign: 'center',
                      background: isDark ? 'rgba(255,255,255,0.02)' : '#fafafa',
                      border: `1px dashed ${token.colorBorderSecondary}`,
                      borderRadius: '8px',
                      color: token.colorTextSecondary,
                      fontSize: '13px',
                    }}
                  >
                    暂无加练清单，点击右上角「新增加练」创建针对性训练
                  </div>
                )}
              </div>
            )}
          </div>

          {/* ⑤ 底部状态指示 */}
          <div style={{ textAlign: 'center', color: token.colorTextSecondary, fontSize: '12px', marginTop: '16px' }}>
            数据源来自 InfluxDB · kovaak_score 权威流水 · 自动适配首末轮疲劳衰减度量
          </div>
        </>
      )}

      {/* 场景详情右侧抽屉 */}
      <ScenarioDrawer
        scenario={selectedScenario}
        open={drawerOpen}
        onClose={handleDrawerClose}
        daylist={daylistId}
        startTs={progressData?.start_ts || 0}
        endTs={progressData?.end_ts || 0}
        rowBench={selectedRow?.bench}
        roundStats={selectedRow?.round_stats}
      />

      {/* 创建加练清单弹窗 */}
      <Modal
        title="新增加练清单"
        open={createModalVisible}
        onOk={handleCreateExtra}
        onCancel={() => setCreateModalVisible(false)}
        okText="创建"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="加练名称"
            rules={[{ required: true, message: '请输入加练名称' }]}
          >
            <Input placeholder="例如：Popcorn 专项加练" />
          </Form.Item>
          <Form.Item
            name="scenario"
            label="场景名"
            rules={[{ required: true, message: '请输入场景名' }]}
          >
            <Input placeholder="例如：Popcorn MV Easier" />
          </Form.Item>
          <Form.Item
            name="role"
            label="角色"
            initialValue="主攻"
          >
            <Input placeholder="主攻 / 巩固 / 热身 / 卡口" />
          </Form.Item>
          <Form.Item
            name="rounds"
            label="轮数"
            initialValue={4}
            rules={[{ required: true, message: '请输入轮数' }]}
          >
            <InputNumber min={1} max={100} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
