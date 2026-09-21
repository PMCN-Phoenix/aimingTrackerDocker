import ReactECharts from 'echarts-for-react'

export default function HistoryChart({ data, nextLine, loading }) {
  if (loading) {
    return <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>加载中...</div>
  }

  if (!data || data.length === 0) {
    return <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>暂无历史数据</div>
  }

  // 准备图表数据
  const dates = data.map(item => item.date)
  const scores = data.map(item => item.score)

  // ECharts 配置
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const item = params[0]
        const dataItem = data[item.dataIndex]
        return `
          日期: ${item.axisValue}<br/>
          得分: ${item.value}<br/>
          命中率: ${dataItem.accuracy ? dataItem.accuracy + '%' : '-'}
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
        fontSize: 10
      }
    },
    yAxis: {
      type: 'value',
      name: '得分'
    },
    series: [
      {
        name: '得分',
        type: 'line',
        data: scores,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
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
    <ReactECharts option={option} style={{ height: '200px', width: '100%' }} />
  )
}
