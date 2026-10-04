import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Select, Button, Spin, message, Modal, Form, Input, InputNumber } from 'antd'
import { ReloadOutlined, PlusOutlined } from '@ant-design/icons'
import { useDaylists, useDaylistProgress, useDaylistExtras } from '../api/hooks'
import { createExtraDaylist, deleteExtraDaylist, exportPlaylist } from '../api/client'
import ProgressTable from '../components/ProgressTable'
import ComparisonTable from '../components/ComparisonTable'
import ScenarioPopup from '../components/ScenarioPopup'
import ExtraDaylistCard from '../components/ExtraDaylistCard'
import DateRangePicker from '../components/DateRangePicker'
import dayjs from 'dayjs'

export default function DaylistDashboard() {
  const { daylistId } = useParams()
  const navigate = useNavigate()
  const [selectedScenario, setSelectedScenario] = useState(null)
  const [popupVisible, setPopupVisible] = useState(false)
  const [dateRange, setDateRange] = useState([dayjs(), dayjs()])
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [form] = Form.useForm()

  // 获取清单列表
  const { data: daylists, isLoading: daylistsLoading } = useDaylists()

  // 获取当前清单的完成度数据
  const { data: progressData, isLoading: progressLoading, refetch } = useDaylistProgress(daylistId)

  // 获取加练清单列表
  const { data: extrasData, isLoading: extrasLoading, refetch: refetchExtras } = useDaylistExtras(daylistId)

  // 切换清单
  const handleDaylistChange = (value) => {
    navigate(`/daylist/${value}`)
  }

  // 切换日期范围
  const handleDateChange = (dates) => {
    setDateRange(dates)
  }

  // 点击场景名
  const handleScenarioClick = (scenario) => {
    setSelectedScenario(scenario)
    setPopupVisible(true)
  }

  // 关闭弹窗
  const handlePopupClose = () => {
    setPopupVisible(false)
    setSelectedScenario(null)
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
        }
      ]
      await createExtraDaylist({
        parent_daylist: daylistId,
        name: values.name,
        exec_dates: progressData?.exec_dates || dayjs().format('YYYY-MM-DD'),
        items: items,
      })
      message.success('加练清单创建成功！')
      setCreateModalVisible(false)
      form.resetFields()
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

  if (progressLoading || daylistsLoading) {
    return <Spin size="large" style={{ display: 'block', marginTop: '100px' }} />
  }

  return (
    <div>
      {/* 过滤器栏 */}
      <div style={{ marginBottom: '24px', display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
        <Select
          value={daylistId}
          onChange={handleDaylistChange}
          style={{ width: 200 }}
          options={daylists?.map(d => ({ value: d.daylist, label: `${d.daylist} - ${d.label}` })) || []}
        />
        <DateRangePicker value={dateRange} onChange={handleDateChange} />
        <Button
          type="primary"
          icon={<ReloadOutlined />}
          onClick={() => { refetch(); refetchExtras(); }}
        >
          刷新
        </Button>
      </div>

      {/* 完成度面板 */}
      <div style={{ marginBottom: '32px' }}>
        <h2>今日清单·完成度</h2>
        <ProgressTable
          data={progressData?.rows || []}
          loading={progressLoading}
          onScenarioClick={handleScenarioClick}
        />
      </div>

      {/* 加练清单区域 */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 style={{ margin: 0, color: '#722ed1' }}>🔥 加练清单（{extrasData?.length || 0} 个）</h2>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setCreateModalVisible(true)}
            style={{ background: '#722ed1', borderColor: '#722ed1' }}
          >
            新增加练
          </Button>
        </div>

        {extrasLoading ? (
          <Spin />
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
          <div style={{
            padding: '40px',
            textAlign: 'center',
            background: '#fafafa',
            border: '2px dashed #d9d9d9',
            borderRadius: '8px',
            color: '#999',
          }}>
            暂无加练清单，点击右上角"新增加练"按钮创建
          </div>
        )}
      </div>

      {/* 目标对比面板 */}
      <div style={{ marginBottom: '32px' }}>
        <h2>今日清单·目标对比</h2>
        <ComparisonTable
          data={progressData?.rows || []}
          loading={progressLoading}
          onScenarioClick={handleScenarioClick}
        />
      </div>

      {/* 场景详情弹窗 */}
      <ScenarioPopup
        scenario={selectedScenario}
        visible={popupVisible}
        onClose={handlePopupClose}
        daylist={daylistId}
        startTs={progressData?.start_ts || 0}
        endTs={progressData?.end_ts || 0}
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
            <Select
              options={[
                { value: '主攻', label: '主攻' },
                { value: '巩固', label: '巩固' },
                { value: '热身', label: '热身' },
                { value: '卡口', label: '卡口' },
              ]}
            />
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
        <div style={{ color: '#999', fontSize: '12px', marginTop: '8px' }}>
          注：当前版本只支持单场景加练，多场景编辑功能开发中...
        </div>
      </Modal>
    </div>
  )
}
