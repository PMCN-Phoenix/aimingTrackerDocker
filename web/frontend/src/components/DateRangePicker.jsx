import { DatePicker, Space } from 'antd'
import dayjs from 'dayjs'

const { RangePicker } = DatePicker

export default function DateRangePicker({ value, onChange }) {
  // 快捷选项
  const shortcuts = [
    {
      label: '今天',
      value: [dayjs(), dayjs()],
    },
    {
      label: '昨天',
      value: [dayjs().subtract(1, 'day'), dayjs().subtract(1, 'day')],
    },
    {
      label: '最近7天',
      value: [dayjs().subtract(6, 'day'), dayjs()],
    },
    {
      label: '最近30天',
      value: [dayjs().subtract(29, 'day'), dayjs()],
    },
  ]

  return (
    <Space direction="vertical" size={12}>
      <RangePicker 
        value={value} 
        onChange={onChange}
        presets={shortcuts}
      />
    </Space>
  )
}
