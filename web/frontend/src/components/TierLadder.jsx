import React from 'react'
import { Tooltip } from 'antd'

const TIER_NAMES = ['Lemming', 'Hare', 'Ermine', 'Puffin', 'Fox', 'Wolf', 'Panther', 'Cheetah', 'Lion']

export default function TierLadder({ targets, achIdx, currentScore, style }) {
  if (!targets || !Array.isArray(targets) || targets.length === 0) {
    return null
  }

  const minVal = targets[0]
  const maxVal = targets[targets.length - 1]
  const range = maxVal - minVal || 1

  // 当前分在阶梯轴上的相对百分比 (0% ~ 100%)
  let currentPct = null
  if (typeof currentScore === 'number') {
    if (currentScore <= minVal) currentPct = 0
    else if (currentScore >= maxVal) currentPct = 100
    else currentPct = ((currentScore - minVal) / range) * 100
  }

  return (
    <div style={{ position: 'relative', width: '100%', minWidth: '160px', maxWidth: '240px', padding: '6px 0', ...style }}>
      {/* 阶梯轴横线 */}
      <div
        style={{
          height: '3px',
          background: '#e8e8e8',
          borderRadius: '2px',
          position: 'relative',
          top: '4px',
        }}
      />

      {/* 9 档节点 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', position: 'relative', top: '-1px' }}>
        {targets.map((tgt, idx) => {
          const isPassed = achIdx !== null && idx <= achIdx
          const isNext = achIdx !== null && idx === achIdx + 1
          const name = TIER_NAMES[idx] || `T${idx + 1}`

          let dotBg = '#bfbfbf'
          let dotBorder = 'none'
          let dotSize = 7

          if (isPassed) {
            dotBg = '#52c41a'
          } else if (isNext) {
            dotBg = '#1677ff'
            dotBorder = '2px solid #91caff'
            dotSize = 9
          }

          return (
            <Tooltip key={idx} title={`${name} 档位线: ${tgt}`}>
              <div
                style={{
                  width: `${dotSize}px`,
                  height: `${dotSize}px`,
                  borderRadius: '50%',
                  background: dotBg,
                  border: dotBorder,
                  cursor: 'pointer',
                  transform: 'translateY(-2px)',
                }}
              />
            </Tooltip>
          )
        })}
      </div>

      {/* 当前分数游标标记 */}
      {currentPct !== null && (
        <Tooltip title={`当前得分: ${currentScore}`}>
          <div
            style={{
              position: 'absolute',
              left: `${currentPct}%`,
              top: '-6px',
              transform: 'translateX(-50%)',
              width: 0,
              height: 0,
              borderLeft: '4px solid transparent',
              borderRight: '4px solid transparent',
              borderTop: '6px solid #1677ff',
              pointerEvents: 'auto',
              cursor: 'pointer',
            }}
          />
        </Tooltip>
      )}
    </div>
  )
}
