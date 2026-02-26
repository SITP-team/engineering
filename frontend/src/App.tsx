import { ConfigProvider, Layout, theme } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import { BrowserRouter as Router } from 'react-router-dom'
import AppRoutes from './routes'
import './App.css'

const { Header, Content, Footer } = Layout

function App() {
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 6,
        },
      }}
    >
      <Router>
        <Layout className="app-layout">
          <Header className="app-header">
            <div className="header-content">
              <h1 className="app-title">🏭 Plant Simulation 自动化建模工具</h1>
              <p className="app-subtitle">通过自然语言描述自动生成生产线模拟模型</p>
            </div>
          </Header>
          <Content className="app-content">
            <AppRoutes />
          </Content>
          <Footer className="app-footer">
            Plant Simulation 自动化建模工具 ©2026 - 工程智能团队
          </Footer>
        </Layout>
      </Router>
    </ConfigProvider>
  )
}

export default App