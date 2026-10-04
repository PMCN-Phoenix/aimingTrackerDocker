import ScenarioRow from './ScenarioRow'

// 9 个档位（从低到高）
const rankNames = [
  'Unranked',
  'Lemming',
  'Ermine',
  'Hare',
  'Penguin',
  'Puffin',
  'Fox',
  'Otter',
  'Lynx'
]

// 把 rank 字符串转成数字索引
const getRankIndex = (rank) => {
  if (typeof rank === 'number') return rank
  if (!rank) return 0
  const idx = rankNames.indexOf(rank)
  return idx >= 0 ? idx : 0
}

export default function SubcategoryRow({ subcategory, scenarios, onScenarioClick }) {
  // 计算子类平均进度
  const avgProgress = scenarios.length > 0
    ? Math.round(scenarios.reduce((sum, s) => sum + (s.pct || 0), 0) / scenarios.length)
    : 0

  // 计算子类平均档位
  const avgRankIdx = scenarios.length > 0
    ? Math.round(scenarios.reduce((sum, s) => sum + getRankIndex(s.rank), 0) / scenarios.length)
    : 0
  const avgRankName = rankNames[avgRankIdx]

  return (
    <div style={{ marginBottom: '24px' }}>
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        marginBottom: '12px',
        padding: '8px 12px',
        backgroundColor: '#f5f5f5',
        borderRadius: '4px'
      }}>
        <h3 style={{ margin: 0, marginRight: '16px' }}>{subcategory}</h3>
        <span style={{ marginRight: '16px', color: '#666' }}>
          平均档位: {avgRankName}
        </span>
        <span style={{ color: '#666' }}>
          平均进度: {avgProgress}%
        </span>
      </div>
      <div style={{ marginLeft: '24px' }}>
        {scenarios.map((scenario) => (
          <ScenarioRow
            key={scenario.scenario}
            scenario={scenario}
            onClick={() => onScenarioClick(scenario.scenario)}
          />
        ))}
      </div>
    </div>
  )
}
