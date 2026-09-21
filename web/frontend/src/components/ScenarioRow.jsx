import RankCells from './RankCells'

export default function ScenarioRow({ scenario, onClick }) {
  const { scenario: name, score, pct, rank, nextLine } = scenario

  // 进度条颜色
  const getProgressColor = (percent) => {
    if (percent >= 95) return '#52c41a' // 绿
    if (percent >= 85) return '#faad14' // 橙
    return '#ff4d4f' // 红
  }

  return (
    <div style={{ 
      display: 'flex', 
      alignItems: 'center', 
      padding: '8px 0',
      borderBottom: '1px solid #f0f0f0'
    }}>
      {/* 场景名 */}
      <div style={{ width: '300px', marginRight: '24px' }}>
        <a onClick={onClick}>{name}</a>
      </div>

      {/* SCORE */}
      <div style={{ width: '80px', marginRight: '24px' }}>
        {score || '-'}
      </div>

      {/* 进度条 */}
      <div style={{ width: '120px', marginRight: '24px' }}>
        <div style={{ 
          width: '100%', 
          height: '8px', 
          backgroundColor: '#f0f0f0',
          borderRadius: '4px',
          overflow: 'hidden'
        }}>
          <div style={{ 
            width: `${Math.min(pct || 0, 100)}%`, 
            height: '100%',
            backgroundColor: getProgressColor(pct || 0)
          }}></div>
        </div>
        <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
          {pct || 0}%
        </div>
      </div>

      {/* 9 档格子 */}
      <RankCells currentRank={rank || 0} />
    </div>
  )
}
