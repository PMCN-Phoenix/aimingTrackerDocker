export default function RankDistributionBar({ data, total }) {
  // 档位名称（从低到高）
  const ranks = ['Hare', 'Ermine', 'Lemming', 'Mink', 'Weasel', 'Fox', 'Panda', 'Penguin', 'Puffin']
  
  // 档位颜色
  const colors = [
    '#d9d9d9', // Hare - 灰
    '#bfbfbf', // Ermine - 深灰
    '#96616b', // Lemming - 棕
    '#6f4e7c', // Mink - 紫
    '#3d5a80', // Weasel - 蓝
    '#ee6c4d', // Fox - 橙
    '#e07a5f', // Panda - 红
    '#81b29a', // Penguin - 绿
    '#f2cc8f', // Puffin - 黄
  ]

  return (
    <div style={{ marginBottom: '24px' }}>
      <h3>档位分布（共 {total} 个场景）</h3>
      <div style={{ 
        display: 'flex', 
        height: '40px', 
        borderRadius: '4px', 
        overflow: 'hidden',
        border: '1px solid #e8e8e8'
      }}>
        {ranks.map((rank, index) => {
          const count = data[index + 1] || 0
          const percent = total > 0 ? (count / total) * 100 : 0
          if (percent === 0) return null
          return (
            <div
              key={rank}
              style={{
                width: `${percent}%`,
                backgroundColor: colors[index],
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '12px',
                fontWeight: 'bold'
              }}
              title={`${rank}: ${count} 个场景`}
            >
              {count > 0 && count}
            </div>
          )
        })}
      </div>
      <div style={{ display: 'flex', marginTop: '8px', fontSize: '12px', color: '#666' }}>
        {ranks.map((rank, index) => {
          const count = data[index + 1] || 0
          if (count === 0) return null
          return (
            <div key={rank} style={{ marginRight: '16px' }}>
              <span style={{ 
                display: 'inline-block', 
                width: '10px', 
                height: '10px', 
                backgroundColor: colors[index],
                borderRadius: '2px',
                marginRight: '4px'
              }}></span>
              {rank} ({count})
            </div>
          )
        })}
      </div>
    </div>
  )
}
