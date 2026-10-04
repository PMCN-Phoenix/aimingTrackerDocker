export default function RankCells({ currentRank }) {
  // 9 个档位（从低到高，按 evxl 动物顺序）
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

  const currentIdx = getRankIndex(currentRank)

  // 格子颜色
  const getCellColor = (rankIdx) => {
    if (rankIdx < currentIdx) return '#52c41a' // 已达档 - 绿
    if (rankIdx === currentIdx) return '#faad14' // 当前档 - 黄
    return '#e8e8e8' // 未达 - 灰
  }

  // 显示名字（用第一个字，太挤了）
  const getShortName = (name) => {
    if (name === 'Unranked') return 'U'
    return name.charAt(0)
  }

  return (
    <div style={{ display: 'flex', gap: '2px' }}>
      {rankNames.map((name, idx) => (
        <div
          key={name}
          style={{
            width: '28px',
            height: '28px',
            backgroundColor: getCellColor(idx),
            borderRadius: '2px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '10px',
            color: idx === currentIdx ? '#000' : '#666',
            fontWeight: idx === currentIdx ? 'bold' : 'normal'
          }}
          title={`${name} (${idx})`}
        >
          {getShortName(name)}
        </div>
      ))}
    </div>
  )
}
