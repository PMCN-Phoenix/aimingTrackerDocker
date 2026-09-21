import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ConfigProvider, Layout, Menu } from 'antd'
import DaylistDashboard from './pages/DaylistDashboard'
import BenchmarkDashboard from './pages/BenchmarkDashboard'
import AimLabDashboard from './pages/AimLabDashboard'
import './App.css'

const { Header, Content } = Layout

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 60 * 1000, // 1分钟
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider theme={{
        token: {
          colorPrimary: '#1677ff',
        },
      }}>
        <Router>
          <Layout style={{ minHeight: '100vh' }}>
            <Header style={{ 
              display: 'flex', 
              alignItems: 'center',
              padding: '0 24px'
            }}>
              <div style={{ 
                color: 'white', 
                fontSize: '18px', 
                fontWeight: 'bold',
                marginRight: '48px'
              }}>
                🎯 练枪看板
              </div>
              <Menu
                theme="dark"
                mode="horizontal"
                defaultSelectedKeys={['daylist']}
                style={{ flex: 1 }}
                items={[
                  { key: 'daylist', label: <Link to="/daylist/Day3">今日清单</Link> },
                  { key: 'benchmark', label: <Link to="/benchmark">基准总览</Link> },
                  { key: 'aimlab', label: <Link to="/aimlab">Aim Lab</Link> },
                ]}
              />
            </Header>
            <Content style={{ padding: '24px', maxWidth: '1400px', width: '100%', margin: '0 auto' }}>
              <Routes>
                <Route path="/" element={<Navigate to="/daylist/Day3" replace />} />
                <Route path="/daylist/:daylistId" element={<DaylistDashboard />} />
                <Route path="/benchmark" element={<BenchmarkDashboard />} />
                <Route path="/aimlab" element={<AimLabDashboard />} />
              </Routes>
            </Content>
          </Layout>
        </Router>
      </ConfigProvider>
    </QueryClientProvider>
  )
}

export default App
