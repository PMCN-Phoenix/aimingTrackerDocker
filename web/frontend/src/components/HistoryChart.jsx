import ReactECharts from 'echarts-for-react'
import dayjs from 'dayjs'
import { theme } from 'antd'
import { useAppTheme } from '../theme/ThemeContext'

export default function HistoryChart({ data, nextLine, loading }) {
  const { token } = theme.useToken()
  const { isDark } = useAppTheme()

  if (loading) {
    return <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: token.colorTextSecondary }}>加载中...</div>
  }

  if (!data || data.length === 0) {
    return <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: token.colorTextSecondary }}>暂无历史数据</div>
  }

  // 准备图表数据（兼容 time 与 date 字段）
  const dates = data.map(item => item.date || (item.time ? dayjs(item.time).format('MM-DD HH:mm') : ''))
  const scores = data.map(item => item.score)

  // ECharts 配置
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const item = params[0]
        const dataItem = data[item.dataIndex]
        return `
          日期: ${item.axisValue}<br/>
          得分: ${item.value}<br/>
          命中率: ${dataItem?.accuracy ? dataItem.accuracy + '%' : '-'}
        `
      }
    },
    grid: {
      left: '10%',
      right: '5%',
      bottom: '15%',
      top: '10%'
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45,
        fontSize: 10,
        color: token.colorTextSecondary,
      },
      axisLine: { lineStyle: { color: token.colorBorderSecondary } },
    },
    yAxis: {
      type: 'value',
      name: '得分',
      nameTextStyle: { color: token.colorTextSecondary },
      axisLabel: { color: token.colorTextSecondary },
      splitLine: { lineStyle: { color: isDark ? 'rgba(255,255,255,0.06)' : '#f0f0f0' } },
    },
    series: [
      {
        name: '得分',
        type: 'line',
        data: scores,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { color: token.colorPrimary },
        itemStyle: { color: token.colorPrimary },
        markLine: nextLine ? {
          silent: true,
          lineStyle: {
            color: '#ff4d4f',
            type: 'dashed'
          },
          data: [{ yAxis: nextLine, label: { formatter: `下一档线: ${nextLine}` } }]
        } : undefined
      }
    ]
  }

  return (
    <ReactECharts
      option={option}
      theme={isDark ? 'dark' : undefined}
      style={{ height: '200px', width: '100%' }}
    />
  )
}
