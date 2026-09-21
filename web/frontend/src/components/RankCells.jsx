export default function RankCells({ currentRank }) {
  // 9 个档位（从低到高）
  const ranks = [1, 2, 3, 4, 5, 6, 7, 8, 9]

  // 格子颜色
  const getCellColor = (rank) => {
    if (rank < currentRank) return '#C0DD97' // 已达档 - 绿
    if (rank === currentRank) return '#B5D4F4' // 下一档 - 蓝
    return '#e8e8e8' // 未达 - 灰
  }

  return (
    <div style={{ display: 'flex', gap: '4px' }}>
      {ranks.map((rank) => (
        <div
          key={rank}
          style={{
            width: '24px',
            height: '24px',
            backgroundColor: getCellColor(rank),
            borderRadius: '2px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '10px',
            color: '#666'
          }}
          title={`档位 ${rank}`}
        >
          {rank}
        </div>
      ))}
    </div>
  )
}
