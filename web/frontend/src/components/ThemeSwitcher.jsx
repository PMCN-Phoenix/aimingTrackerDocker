import React from 'react'
import { Dropdown, Button } from 'antd'
import { BgColorsOutlined, CheckOutlined } from '@ant-design/icons'
import { useAppTheme } from '../theme/ThemeContext'
import { THEME_CONFIGS } from '../theme/themeConfig'

export default function ThemeSwitcher() {
  const { themeKey, setThemeKey, currentTheme } = useAppTheme()

  const items = Object.values(THEME_CONFIGS).map((item) => ({
    key: item.key,
    label: (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', minWidth: '150px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span
            style={{
              display: 'inline-block',
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              backgroundColor: item.badgeColor,
              boxShadow: `0 0 6px ${item.badgeColor}`,
            }}
          />
          <span>{item.name}</span>
        </div>
        {themeKey === item.key && <CheckOutlined style={{ color: item.badgeColor, fontSize: '12px' }} />}
      </div>
    ),
    onClick: () => setThemeKey(item.key),
  }))

  return (
    <Dropdown menu={{ items }} placement="bottomRight" trigger={['click']}>
      <Button
        type="text"
        icon={<BgColorsOutlined style={{ color: currentTheme.token.colorPrimary }} />}
        style={{
          color: currentTheme.isDark ? '#e6e6e6' : '#ffffff',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          border: `1px solid ${currentTheme.isDark ? '#30363d' : 'rgba(255,255,255,0.2)'}`,
          borderRadius: '6px',
          background: currentTheme.isDark ? 'rgba(255,255,255,0.05)' : 'rgba(255,255,255,0.1)',
        }}
      >
        <span
          style={{
            display: 'inline-block',
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: currentTheme.badgeColor,
            boxShadow: `0 0 5px ${currentTheme.badgeColor}`,
          }}
        />
        <span style={{ fontSize: '13px' }}>{currentTheme.name.split(' ')[1]}</span>
      </Button>
    </Dropdown>
  )
}
