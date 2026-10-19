import { useState, useMemo } from 'react'
import { Card, Segmented, Radio, Typography, Empty, Space, Tooltip } from 'antd'
import ReactECharts from 'echarts-for-react'
import {
  RadarChartOutlined,
  BarChartOutlined,
  AimOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons'

const { Text } = Typography

export default function MultiDimComparisonChart({ rows = [] }) {
  // 对比历史基准：'baseline' (历史初次) | 'pb' (历史最佳)
  const [historyBaselineType, setHistoryBaselineType] = useState('baseline')
  // 图表形态：'radar' (雷达图) | 'bar' (对比子弹柱状图)
  const [chartType, setChartType] = useState('radar')
  // 范围过滤：'all' (全部场景) | 'benchOnly' (仅有基准场景)
  const [filterMode, setFilterMode] = useState('all')

  // 筛选有效场景（至少当天有分或有基准线）
  const chartData = useMemo(() => {
    if (!rows || rows.length === 0) return []

    let filtered = rows.filter((r) => r.scenario)
    if (filterMode === 'benchOnly') {
      filtered = filtered.filter((r) => r.bench && typeof r.bench.nextLine === 'number')
    }

    return filtered.map((r) => {
      const scenarioName = r.scenario
      const currentScore = r.today_score?.score ?? null
      const targetScore = r.bench?.nextLine ?? null
      const historyStats = r.history_stats || null

      let histScore = null
      if (historyStats) {
        histScore = historyBaselineType === 'baseline' ? historyStats.baseline : historyStats.best
      } else if (r.round_stats?.first) {
        histScore = r.round_stats.first
      }

      // 归一化基准：以 target 为 100%，若无 target 则以当前或历史最高为 100%
      const baseTarget = targetScore || (currentScore && histScore ? Math.max(currentScore, histScore) : (currentScore || 100))
      
      const currentPct = currentScore && baseTarget ? Math.round((currentScore / baseTarget) * 1000) / 10 : 0
      const histPct = histScore && baseTarget ? Math.round((histScore / baseTarget) * 1000) / 10 : 0
      const targetPct = targetScore ? 100 : (baseTarget ? 100 : 0)

      return {
        scenario: scenarioName,
        shortName: scenarioName.length > 18 ? scenarioName.substring(0, 16) + '..' : scenarioName,
        role: r.role || '',
        currentScore,
        targetScore,
        histScore,
        baseTarget,
        currentPct,
        histPct,
        targetPct,
        hasBench: !!targetScore,
      }
    })
  }, [rows, historyBaselineType, filterMode])

  if (chartData.length < 3) {
    return (
      <Card style={{ marginBottom: '24px', borderRadius: '10px' }} size="small">
        <div style={{ textAlign: 'center', padding: '30px', color: '#8c8c8c' }}>
          <Empty description="当前清单有效场景少于 3 个，无法构成多维能力对比图" />
        </div>
      </Card>
    )
  }

  // ==================== 雷达图配置 ====================
  const radarOption = useMemo(() => {
    const indicators = chartData.map((d) => ({
      name: d.shortName,
      max: Math.max(120, ...chartData.map((x) => Math.max(x.currentPct, x.histPct, 100) + 10)),
    }))

    const targetSeriesData = chartData.map((d) => d.targetPct)
    const currentSeriesData = chartData.map((d) => d.currentPct)
    const historySeriesData = chartData.map((d) => d.histPct)

    return {
      tooltip: {
        trigger: 'item',
        formatter: (params) => {
          return `
            <div style="font-size:12px; line-height:1.6; min-width: 200px;">
              <b style="color: #262626;">多维能力对比剖析 (以目标能力为 100% 环)</b><br/>
              ${chartData.map((d, i) => `
                <div style="margin-top: 6px; padding: 4px 0; border-top: 1px solid #f0f0f0;">
                  <span style="font-weight:600;">${d.scenario}</span><br/>
                  <span style="color: #722ed1;">🎯 想要达到的能力: ${d.targetScore ?? '无基准(自适应)'} (${d.targetPct}%)</span><br/>
                  <span style="color: #52c41a;">🟢 当前训练记录: ${d.currentScore ?? '未打'} (${d.currentPct}%)</span><br/>
                  <span style="color: #fa8c16;">🟠 历史对比记录: ${d.histScore ?? '无记录'} (${d.histPct}%)</span>
                </div>
              `).join('')}
            </div>
          `
        },
      },
      legend: {
        data: ['🎯 想要达到的能力 (目标线 100%)', '🟢 当前训练记录 (Today)', '🟠 历史上某一次记录 (History)'],
        top: 0,
        textStyle: { fontSize: 12 },
      },
      radar: {
        indicator: indicators,
        radius: '65%',
        center: ['50%', '55%'],
        shape: 'polygon',
        splitNumber: 4,
        axisName: {
          color: '#595959',
          fontSize: 11,
          fontFamily: 'monospace',
          formatter: (value) => {
            return value
          },
        },
        splitLine: {
          lineStyle: {
            color: ['#e8e8e8', '#e8e8e8', '#91caff', '#e8e8e8'],
            width: 1,
            type: 'solid',
          },
        },
        splitArea: {
          show: true,
          areaStyle: {
            color: ['rgba(250,250,250,0.3)', 'rgba(240,240,240,0.3)'],
          },
        },
      },
      series: [
        {
          name: '能力多维对比',
          type: 'radar',
          data: [
            {
              value: targetSeriesData,
              name: '🎯 想要达到的能力 (目标线 100%)',
              symbol: 'circle',
              symbolSize: 4,
              lineStyle: {
                color: '#722ed1',
                width: 2,
                type: 'dashed',
              },
              itemStyle: { color: '#722ed1' },
              areaStyle: { color: 'rgba(114, 46, 209, 0.05)' },
            },
            {
              value: historySeriesData,
              name: '🟠 历史上某一次记录 (History)',
              symbol: 'rect',
              symbolSize: 4,
              lineStyle: {
                color: '#fa8c16',
                width: 2,
              },
              itemStyle: { color: '#fa8c16' },
              areaStyle: { color: 'rgba(250, 140, 22, 0.12)' },
            },
            {
              value: currentSeriesData,
              name: '🟢 当前训练记录 (Today)',
              symbol: 'circle',
              symbolSize: 6,
              lineStyle: {
                color: '#52c41a',
                width: 2.5,
              },
              itemStyle: { color: '#52c41a' },
              areaStyle: { color: 'rgba(82, 196, 26, 0.22)' },
            },
          ],
        },
      ],
    }
  }, [chartData])

  // ==================== 对比条形图配置 ====================
  const barOption = useMemo(() => {
    const categories = chartData.map((d) => d.shortName)
    const targetData = chartData.map((d) => d.targetScore || d.baseTarget)
    const currentData = chartData.map((d) => d.currentScore || 0)
    const histData = chartData.map((d) => d.histScore || 0)

    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: (params) => {
          const idx = params[0].dataIndex
          const item = chartData[idx]
          return `
            <div style="font-size:12px; line-height:1.6;">
              <b>${item.scenario}</b><br/>
              🎯 目标能力: <b>${item.targetScore ?? '无基准'}</b><br/>
              🟢 当前得分: <b>${item.currentScore ?? '—'}</b> (${item.currentPct}%)<br/>
              🟠 历史得分: <b>${item.histScore ?? '—'}</b> (${item.histPct}%)<br/>
              较历史增益: <b style="color: ${(item.currentScore || 0) >= (item.histScore || 0) ? '#52c41a' : '#ff4d4f'}">
                ${item.currentScore && item.histScore ? ((item.currentScore - item.histScore) > 0 ? '+' : '') + (item.currentScore - item.histScore).toFixed(1) : '—'}
              </b>
            </div>
          `
        },
      },
      legend: {
        data: ['🎯 目标能力 (Target)', '🟢 当前得分 (Current)', '🟠 历史得分 (History)'],
        top: 0,
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '10%',
        top: '15%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: categories,
        axisLabel: { rotate: 30, fontSize: 10, interval: 0 },
      },
      yAxis: {
        type: 'value',
        name: '分数',
      },
      series: [
        {
          name: '🎯 目标能力 (Target)',
          type: 'bar',
          data: targetData,
          itemStyle: { color: '#722ed1', opacity: 0.6 },
        },
        {
          name: '🟠 历史得分 (History)',
          type: 'bar',
          data: histData,
          itemStyle: { color: '#fa8c16', opacity: 0.8 },
        },
        {
          name: '🟢 当前得分 (Current)',
          type: 'bar',
          data: currentData,
          itemStyle: { color: '#52c41a' },
        },
      ],
    }
  }, [chartData])

  return (
    <Card
      id="multidim-chart-section"
      style={{
        marginBottom: '24px',
        borderRadius: '10px',
        border: '1px solid #f0f0f0',
        boxShadow: '0 2px 6px rgba(0,0,0,0.02)',
      }}
      styles={{ body: { padding: '16px 20px' } }}
    >
      {/* 头部控制栏 */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px',
          marginBottom: '16px',
          borderBottom: '1px solid #f5f5f5',
          paddingBottom: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <RadarChartOutlined style={{ color: '#1677ff', fontSize: '18px' }} />
          <span style={{ fontSize: '15px', fontWeight: 700, color: '#1f1f1f' }}>
            能力多维对比图
          </span>
          <Tooltip title="三层对比视角：外层虚线为目标能力（100%基准圆环），绿色为当日实测能力，橙色为历史参照点。凹陷处即为当期最需突破的能力短板。">
            <InfoCircleOutlined style={{ color: '#8c8c8c', cursor: 'pointer' }} />
          </Tooltip>
        </div>

        {/* 交互切换器 */}
        <Space size="middle" wrap>
          {/* 历史参照基准切换 */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Text type="secondary" style={{ fontSize: '12px' }}>历史对比基准:</Text>
            <Radio.Group
              size="small"
              value={historyBaselineType}
              onChange={(e) => setHistoryBaselineType(e.target.value)}
              optionType="button"
              buttonStyle="solid"
            >
              <Radio.Button value="baseline">历史初次 (Baseline)</Radio.Button>
              <Radio.Button value="pb">历史最佳 (PB)</Radio.Button>
            </Radio.Group>
          </div>

          {/* 范围过滤 */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Text type="secondary" style={{ fontSize: '12px' }}>场景筛选:</Text>
            <Radio.Group
              size="small"
              value={filterMode}
              onChange={(e) => setFilterMode(e.target.value)}
              optionType="button"
            >
              <Radio.Button value="all">全部场景 ({rows.length})</Radio.Button>
              <Radio.Button value="benchOnly">
                仅有基准 ({rows.filter((r) => r.bench?.nextLine).length})
              </Radio.Button>
            </Radio.Group>
          </div>

          {/* 图表形态 */}
          <Segmented
            size="small"
            value={chartType}
            onChange={setChartType}
            options={[
              { value: 'radar', icon: <RadarChartOutlined />, label: '多维雷达' },
              { value: 'bar', icon: <BarChartOutlined />, label: '对比条形' },
            ]}
          />
        </Space>
      </div>

      {/* 图表渲染区 */}
      <div style={{ width: '100%', height: chartType === 'radar' ? '380px' : '320px' }}>
        <ReactECharts
          option={chartType === 'radar' ? radarOption : barOption}
          style={{ width: '100%', height: '100%' }}
          notMerge={true}
        />
      </div>

      {/* 底部解读注脚 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#8c8c8c', marginTop: '8px' }}>
        <span>🎯 紫色虚线：想要达到的能力线（以官方基准下一档为 100% 环）</span>
        <span>🟢 绿色区域：当前训练记录（凸出=超标，凹陷=短板）</span>
        <span>🟠 橙色区域：{historyBaselineType === 'baseline' ? '历史初次训练基线' : '历史历史最高成绩(PB)'}</span>
      </div>
    </Card>
  )
}
