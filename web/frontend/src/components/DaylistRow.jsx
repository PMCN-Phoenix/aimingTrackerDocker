import React from 'react'
import { Tag, Tooltip, Progress, theme } from 'antd'
import TierLadder from './TierLadder'
import { useAppTheme } from '../theme/ThemeContext'

const LIGHT_ROLE_COLORS = {
  '主项': { color: '#1677ff', bg: '#e6f4ff', border: '#91caff' },
  '主攻': { color: '#1677ff', bg: '#e6f4ff', border: '#91caff' },
  '卡口': { color: '#fa8c16', bg: '#fff7e6', border: '#ffd591' },
  '热身': { color: '#52c41a', bg: '#f6ffed', border: '#b7eb8f' },
  '巩固': { color: '#722ed1', bg: '#f9f0ff', border: '#d3adf7' },
}

const DARK_ROLE_COLORS = {
  '主项': { color: '#69b1ff', bg: 'rgba(22, 119, 255, 0.18)', border: 'rgba(22, 119, 255, 0.4)' },
  '主攻': { color: '#69b1ff', bg: 'rgba(22, 119, 255, 0.18)', border: 'rgba(22, 119, 255, 0.4)' },
  '卡口': { color: '#ffc069', bg: 'rgba(250, 140, 22, 0.18)', border: 'rgba(250, 140, 22, 0.4)' },
  '热身': { color: '#95de64', bg: 'rgba(82, 196, 26, 0.18)', border: 'rgba(82, 196, 26, 0.4)' },
  '巩固': { color: '#d3adf7', bg: 'rgba(114, 46, 209, 0.18)', border: 'rgba(114, 46, 209, 0.4)' },
}

const LIGHT_STATUS_CONFIG = {
  '已完成': { color: '#52c41a', bg: '#f6ffed', border: '#b7eb8f' },
  '进行中': { color: '#fa8c16', bg: '#fff7e6', border: '#ffd591' },
  '未开始': { color: '#8c8c8c', bg: '#f5f5f5', border: '#d9d9d9' },
}

const DARK_STATUS_CONFIG = {
  '已完成': { color: '#95de64', bg: 'rgba(82, 196, 26, 0.18)', border: 'rgba(82, 196, 26, 0.4)' },
  '进行中': { color: '#ffc069', bg: 'rgba(250, 140, 22, 0.18)', border: 'rgba(250, 140, 22, 0.4)' },
  '未开始': { color: '#8c8c8c', bg: 'rgba(255, 255, 255, 0.05)', border: 'rgba(255, 255, 255, 0.15)' },
}

export default function DaylistRow({ row, mode = 'card', onClick }) {
  const { token } = theme.useToken()
  const { isDark } = useAppTheme()

  const {
    order,
    scenario,
    role,
    required_rounds = 0,
    done_rounds = 0,
    status = '未开始',
    today_score,
    bench,
    round_stats,
  } = row

  const roleColors = isDark ? DARK_ROLE_COLORS : LIGHT_ROLE_COLORS
  const statusColors = isDark ? DARK_STATUS_CONFIG : LIGHT_STATUS_CONFIG

  const roleStyle = roleColors[role] || {
    color: token.colorTextSecondary,
    bg: isDark ? 'rgba(255,255,255,0.06)' : '#f5f5f5',
    border: token.colorBorderSecondary,
  }
  const statusStyle = statusColors[status] || statusColors['未开始']

  const hasScore = today_score && typeof today_score.score === 'number'
  const hasBench = bench && typeof bench.nextLine === 'number'
  const roundPct = required_rounds > 0 ? Math.min(100, Math.round((done_rounds / required_rounds) * 100)) : 100
  const isOverRounds = done_rounds > required_rounds

  const dropPct = round_stats?.drop_pct
  const isDecayed = typeof dropPct === 'number' && dropPct <= -15

  // ================= 紧凑表模式 =================
  if (mode === 'compact') {
    return (
      <div
        onClick={() => onClick && onClick(scenario)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '8px 14px',
          background: token.colorBgContainer,
          borderBottom: `1px solid ${token.colorBorderSecondary}`,
          cursor: 'pointer',
          transition: 'background 0.2s',
          fontSize: '13px',
        }}
        onMouseEnter={(e) => (e.currentTarget.style.background = token.colorFillAlter)}
        onMouseLeave={(e) => (e.currentTarget.style.background = token.colorBgContainer)}
      >
        {/* 序号 */}
        <span style={{ width: '24px', color: token.colorTextSecondary, fontWeight: 600, fontFamily: 'monospace' }}>
          {order}
        </span>

        {/* 角色 */}
        <span
          style={{
            width: '42px',
            textAlign: 'center',
            fontSize: '11px',
            padding: '1px 4px',
            borderRadius: '4px',
            color: roleStyle.color,
            background: roleStyle.bg,
            border: `1px solid ${roleStyle.border}`,
          }}
        >
          {role || '—'}
        </span>

        {/* 场景名 */}
        <div
          style={{
            flex: 1,
            fontWeight: 600,
            fontFamily: 'monospace',
            color: token.colorText,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {scenario}
        </div>

        {/* 轮数 */}
        <div style={{ width: '90px', fontFamily: 'monospace', textAlign: 'right' }}>
          <span style={{ color: done_rounds >= required_rounds ? '#52c41a' : '#fa8c16', fontWeight: 600 }}>
            {done_rounds}
          </span>
          <span style={{ color: token.colorTextSecondary }}>/{required_rounds} 轮</span>
        </div>

        {/* 成绩与目标 */}
        <div style={{ width: '150px', textAlign: 'right', fontFamily: 'monospace' }}>
          {hasScore ? (
            <span style={{ fontWeight: 600, color: token.colorText }}>{today_score.score}</span>
          ) : (
            <span style={{ color: token.colorTextSecondary }}>—</span>
          )}
          <span style={{ color: token.colorTextSecondary, margin: '0 4px' }}>/</span>
          {hasBench ? (
            <span style={{ color: token.colorTextSecondary }}>{bench.nextLine}</span>
          ) : (
            <span style={{ color: token.colorTextSecondary, fontSize: '12px' }}>无基准</span>
          )}
        </div>

        {/* 命中率 */}
        <div style={{ width: '70px', textAlign: 'right', fontFamily: 'monospace', color: token.colorTextSecondary }}>
          {today_score?.accuracy ? `${today_score.accuracy}%` : '—'}
        </div>

        {/* 衰减 */}
        <div style={{ width: '85px', textAlign: 'right' }}>
          {isDecayed ? (
            <span style={{ color: '#ff4d4f', fontWeight: dropPct <= -30 ? 700 : 500, fontSize: '12px' }}>
              ⚠ {dropPct}%
            </span>
          ) : (
            <span style={{ color: token.colorTextSecondary, fontSize: '12px' }}>—</span>
          )}
        </div>

        {/* 状态 */}
        <div style={{ width: '60px', textAlign: 'center' }}>
          <span
            style={{
              fontSize: '11px',
              padding: '1px 6px',
              borderRadius: '4px',
              color: statusStyle.color,
              background: statusStyle.bg,
              border: `1px solid ${statusStyle.border}`,
            }}
          >
            {status}
          </span>
        </div>
      </div>
    )
  }

  // ================= 卡片流模式 (默认) =================
  return (
    <div
      onClick={() => onClick && onClick(scenario)}
      style={{
        background: token.colorBgContainer,
        borderRadius: '10px',
        border: `1px solid ${token.colorBorderSecondary}`,
        padding: '12px 16px',
        marginBottom: '10px',
        cursor: 'pointer',
        boxShadow: isDark ? '0 2px 8px rgba(0,0,0,0.2)' : '0 1px 3px rgba(0,0,0,0.02)',
        transition: 'all 0.2s',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = isDark ? '0 4px 16px rgba(0,0,0,0.4)' : '0 4px 12px rgba(0,0,0,0.06)'
        e.currentTarget.style.borderColor = token.colorPrimary
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = isDark ? '0 2px 8px rgba(0,0,0,0.2)' : '0 1px 3px rgba(0,0,0,0.02)'
        e.currentTarget.style.borderColor = token.colorBorderSecondary
      }}
    >
      {/* 顶部标题栏：序号 + 角色 + 场景名 + 衰减预警 + 状态 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0 }}>
          <span
            style={{
              width: '22px',
              height: '22px',
              borderRadius: '50%',
              background: isDark ? 'rgba(255,255,255,0.08)' : '#f0f2f5',
              color: token.colorTextSecondary,
              fontSize: '12px',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontFamily: 'monospace',
              flexShrink: 0,
            }}
          >
            {order}
          </span>

          {role && (
            <span
              style={{
                fontSize: '11px',
                padding: '1px 6px',
                borderRadius: '4px',
                color: roleStyle.color,
                background: roleStyle.bg,
                border: `1px solid ${roleStyle.border}`,
                fontWeight: 500,
                flexShrink: 0,
              }}
            >
              {role}
            </span>
          )}

          <span
            style={{
              fontSize: '14px',
              fontWeight: 600,
              fontFamily: 'monospace',
              color: token.colorText,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {scenario}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
          {/* 衰减标记 */}
          {isDecayed && (
            <Tooltip title={`当日最高 ${round_stats.best} → 末轮 ${round_stats.last}，衰减幅度 ${dropPct}%`}>
              <Tag
                color="error"
                style={{
                  marginRight: 0,
                  borderRadius: '4px',
                  fontWeight: dropPct <= -30 ? 700 : 500,
                }}
              >
                ⚠ 衰减 {dropPct}%
              </Tag>
            </Tooltip>
          )}

          {/* 状态 Chip */}
          <span
            style={{
              fontSize: '12px',
              padding: '2px 8px',
              borderRadius: '4px',
              color: statusStyle.color,
              background: statusStyle.bg,
              border: `1px solid ${statusStyle.border}`,
              fontWeight: 500,
            }}
          >
            {status}
          </span>
        </div>
      </div>

      {/* 双轨并排区：左侧轮数轨 + 右侧分数轨 */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.35fr', gap: '20px', alignItems: 'center' }}>
        {/* 左轨：轮数进度 */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '12px', color: token.colorTextSecondary, width: '28px', flexShrink: 0 }}>轮数</span>
          <div style={{ flex: 1, minWidth: '80px' }}>
            <Progress
              percent={roundPct}
              showInfo={false}
              size={['100%', 6]}
              strokeColor={done_rounds >= required_rounds ? '#52c41a' : '#fa8c16'}
              railColor={isDark ? 'rgba(255,255,255,0.08)' : '#f0f0f0'}
            />
          </div>
          <div style={{ fontSize: '13px', fontFamily: 'monospace', flexShrink: 0, minWidth: '65px', textAlign: 'right' }}>
            <span style={{ fontWeight: 700, color: done_rounds >= required_rounds ? '#52c41a' : '#fa8c16' }}>
              {done_rounds}
            </span>
            <span style={{ color: token.colorTextSecondary }}>/{required_rounds}</span>
            {isOverRounds && (
              <span style={{ color: '#52c41a', fontWeight: 600, marginLeft: '3px', fontSize: '11px' }}>
                +{done_rounds - required_rounds}
              </span>
            )}
          </div>
        </div>

        {/* 右轨：分数与基准 */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', justifyContent: 'flex-end' }}>
          <span style={{ fontSize: '12px', color: token.colorTextSecondary, flexShrink: 0 }}>分数</span>

          {/* 阶梯梯子（若有基准数据） */}
          {hasBench && bench.targets && (
            <TierLadder
              targets={bench.targets}
              achIdx={bench.achIdx}
              currentScore={today_score?.score}
              style={{ flex: 1, margin: '0 4px' }}
            />
          )}

          {/* 分数 / 下一档线 */}
          <div style={{ fontSize: '13px', fontFamily: 'monospace', textAlign: 'right', flexShrink: 0 }}>
            {hasScore ? (
              <span style={{ fontWeight: 700, color: token.colorText }}>{today_score.score}</span>
            ) : (
              <span style={{ color: token.colorTextSecondary }}>—</span>
            )}
            <span style={{ color: token.colorTextSecondary, margin: '0 4px' }}>/</span>
            {hasBench ? (
              <Tooltip title={bench.rank ? `下一档: ${bench.rank}` : '下一档基准线'}>
                <span style={{ color: token.colorTextSecondary, fontWeight: 500 }}>{bench.nextLine}</span>
              </Tooltip>
            ) : (
              <Tag
                style={{
                  marginRight: 0,
                  color: token.colorTextSecondary,
                  background: isDark ? 'rgba(255,255,255,0.05)' : '#f5f5f5',
                  borderColor: token.colorBorderSecondary,
                  fontSize: '11px',
                }}
              >
                无基准
              </Tag>
            )}
          </div>

          {/* 命中率 */}
          <div style={{ width: '80px', textAlign: 'right', fontSize: '12px', color: token.colorTextSecondary, fontFamily: 'monospace', flexShrink: 0 }}>
            {today_score?.accuracy ? `命中 ${today_score.accuracy}%` : '命中 —'}
          </div>

          {/* 末轮得分展示 */}
          {round_stats?.last && (
            <div style={{ fontSize: '11px', color: token.colorTextSecondary, fontFamily: 'monospace', flexShrink: 0 }}>
              末轮 {round_stats.last}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
