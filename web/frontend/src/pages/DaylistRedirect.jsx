import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Spin } from 'antd'
import { useDaylists } from '../api/hooks'

/**
 * 默认落地页：跳到「最新」的清单。
 *
 * 以前路由把 /daylist/Day3 写死在 App.jsx 里，导致点「今日清单」永远打开
 * Day3（2026-09-21 的历史清单），再叠加日期选择器默认「今天」，
 * 页面看起来就是一片空白——这是「web 端没有正常显示」的主要来源之一。
 */
export default function DaylistRedirect() {
  const navigate = useNavigate()
  const { data: daylists, isLoading } = useDaylists()

  useEffect(() => {
    if (!daylists || daylists.length === 0) return
    // 后端已按清单序号倒序返回，取第一条即最新
    navigate(`/daylist/${daylists[0].daylist}`, { replace: true })
  }, [daylists, navigate])

  if (isLoading) {
    return <Spin size="large" style={{ display: 'block', marginTop: '100px' }} />
  }

  if (!daylists || daylists.length === 0) {
    return (
      <div style={{ padding: '60px', textAlign: 'center', color: '#999' }}>
        还没有任何清单。先跑一次 <code>python daylist_sync.py</code> 把清单写进库。
      </div>
    )
  }

  return <Spin size="large" style={{ display: 'block', marginTop: '100px' }} />
}
