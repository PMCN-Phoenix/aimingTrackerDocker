import React, { createContext, useContext, useState, useEffect } from 'react'
import { THEME_CONFIGS, DEFAULT_THEME } from './themeConfig'

const ThemeContext = createContext({
  themeKey: DEFAULT_THEME,
  setThemeKey: () => {},
  currentTheme: THEME_CONFIGS[DEFAULT_THEME],
  isDark: false,
})

export function ThemeProvider({ children }) {
  const [themeKey, setThemeKey] = useState(() => {
    const saved = localStorage.getItem('aimTrackerTheme')
    return THEME_CONFIGS[saved] ? saved : DEFAULT_THEME
  })

  const currentTheme = THEME_CONFIGS[themeKey] || THEME_CONFIGS[DEFAULT_THEME]
  const isDark = currentTheme.isDark

  const handleSetTheme = (newKey) => {
    if (THEME_CONFIGS[newKey]) {
      setThemeKey(newKey)
      localStorage.setItem('aimTrackerTheme', newKey)
    }
  }

  useEffect(() => {
    // 同步 body 背景色与字体颜色
    document.body.style.backgroundColor = currentTheme.bodyBg
    if (isDark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [currentTheme, isDark])

  return (
    <ThemeContext.Provider
      value={{
        themeKey,
        setThemeKey: handleSetTheme,
        currentTheme,
        isDark,
      }}
    >
      {children}
    </ThemeContext.Provider>
  )
}

export function useAppTheme() {
  return useContext(ThemeContext)
}
