import { useState, useEffect } from 'react'
import { Card, Row, Col, Button, Space, message, Tabs, Typography, Alert, Descriptions } from 'antd'
import { DownloadOutlined, CopyOutlined, CheckOutlined, HomeOutlined, EyeOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { confirmAndGenerateCode } from '../services/api'

const { Title, Paragraph, Text } = Typography
const { TabPane } = Tabs

interface GeneratedCode {
  modelCode: string
  dataCode: string
}

const CodeGenerationPage = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [generatedCode, setGeneratedCode] = useState<GeneratedCode | null>(null)
  const [activeTab, setActiveTab] = useState('model')

  // 生成代码
  useEffect(() => {
    const generateCode = async () => {
      setLoading(true)
      try {
        const savedData = localStorage.getItem('graphData')
        if (!savedData) {
          message.error('没有找到生产线数据')
          navigate('/')
          return
        }

        const graphData = JSON.parse(savedData)
        const result = await confirmAndGenerateCode(graphData)

        if (result.success && result.data) {
          setGeneratedCode(result.data)
          message.success('代码生成成功！')
        } else {
          message.error(result.message || '代码生成失败')
        }
      } catch (error) {
        console.error('生成代码失败:', error)
        message.error('生成代码失败')
      } finally {
        setLoading(false)
      }
    }

    generateCode()
  }, [navigate])

  // 复制代码到剪贴板
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
      .then(() => {
        message.success('代码已复制到剪贴板')
      })
      .catch((err) => {
        console.error('复制失败:', err)
        message.error('复制失败')
      })
  }

  // 下载代码文件
  const downloadCode = (filename: string, content: string) => {
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    message.success(`文件 ${filename} 下载成功`)
  }

  // 处理返回首页
  const handleBackToHome = () => {
    navigate('/')
  }

  // 处理查看可视化
  const handleViewVisualization = () => {
    navigate('/visualization')
  }

  if (loading) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <Title level={3}>正在生成 Plant Simulation 代码...</Title>
          <Paragraph>请稍候，系统正在根据您的生产线模型生成代码</Paragraph>
        </div>
      </Card>
    )
  }

  if (!generatedCode) {
    return (
      <Card>
        <Alert
          message="代码生成失败"
          description="无法生成 Plant Simulation 代码，请返回重新生成模型"
          type="error"
          showIcon
          action={
            <Space>
              <Button onClick={handleBackToHome} icon={<HomeOutlined />}>
                返回首页
              </Button>
              <Button onClick={handleViewVisualization} icon={<EyeOutlined />}>
                查看可视化
              </Button>
            </Space>
          }
        />
      </Card>
    )
  }

  return (
    <div className="code-generation-page">
      <Row gutter={[24, 24]}>
        <Col span={24}>
          <Card
            title="🚀 Plant Simulation 代码生成"
            extra={
              <Space>
                <Button icon={<EyeOutlined />} onClick={handleViewVisualization}>
                  查看可视化
                </Button>
                <Button icon={<HomeOutlined />} onClick={handleBackToHome}>
                  返回首页
                </Button>
              </Space>
            }
          >
            <Alert
              message="代码生成完成"
              description="Plant Simulation 代码已成功生成，您可以将代码复制到 Plant Simulation 软件中运行。"
              type="success"
              showIcon
              style={{ marginBottom: 24 }}
            />

            <Descriptions bordered column={2} size="small">
              <Descriptions.Item label="模型建立代码行数">
                {generatedCode.modelCode.split('\n').length} 行
              </Descriptions.Item>
              <Descriptions.Item label="数据写入代码行数">
                {generatedCode.dataCode.split('\n').length} 行
              </Descriptions.Item>
              <Descriptions.Item label="生成时间">{new Date().toLocaleString()}</Descriptions.Item>
              <Descriptions.Item label="状态">
                <Text type="success">✓ 已生成</Text>
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        <Col span={24}>
          <Card title="📝 生成的代码">
            <Tabs activeKey={activeTab} onChange={setActiveTab}>
              <TabPane tab="模型建立代码" key="model">
                <div style={{ position: 'relative' }}>
                  <div style={{ position: 'absolute', top: 16, right: 16, zIndex: 1 }}>
                    <Space>
                      <Button
                        size="small"
                        icon={<CopyOutlined />}
                        onClick={() => copyToClipboard(generatedCode.modelCode)}
                      >
                        复制代码
                      </Button>
                      <Button
                        size="small"
                        icon={<DownloadOutlined />}
                        onClick={() => downloadCode('plant_simulation_model.txt', generatedCode.modelCode)}
                      >
                        下载文件
                      </Button>
                    </Space>
                  </div>
                  <pre
                    style={{
                      background: '#f6f8fa',
                      padding: 24,
                      borderRadius: 8,
                      fontSize: '14px',
                      lineHeight: 1.6,
                      margin: 0,
                      maxHeight: '500px',
                      overflow: 'auto',
                    }}
                  >
                    <code>{generatedCode.modelCode}</code>
                  </pre>
                </div>
              </TabPane>

              <TabPane tab="数据写入代码" key="data">
                <div style={{ position: 'relative' }}>
                  <div style={{ position: 'absolute', top: 16, right: 16, zIndex: 1 }}>
                    <Space>
                      <Button
                        size="small"
                        icon={<CopyOutlined />}
                        onClick={() => copyToClipboard(generatedCode.dataCode)}
                      >
                        复制代码
                      </Button>
                      <Button
                        size="small"
                        icon={<DownloadOutlined />}
                        onClick={() => downloadCode('plant_simulation_data.txt', generatedCode.dataCode)}
                      >
                        下载文件
                      </Button>
                    </Space>
                  </div>
                  <pre
                    style={{
                      background: '#f6f8fa',
                      padding: 24,
                      borderRadius: 8,
                      fontSize: '14px',
                      lineHeight: 1.6,
                      margin: 0,
                      maxHeight: '500px',
                      overflow: 'auto',
                    }}
                  >
                    <code>{generatedCode.dataCode}</code>
                  </pre>
                </div>
              </TabPane>

              <TabPane tab="使用说明" key="instructions">
                <Alert
                  message="Plant Simulation 代码使用指南"
                  description={
                    <div>
                      <Paragraph strong>步骤 1: 导入模型建立代码</Paragraph>
                      <ol>
                        <li>打开 Plant Simulation 软件</li>
                        <li>创建一个新的 Frame</li>
                        <li>将"模型建立代码"复制到 Method 编辑器中</li>
                        <li>运行 Method 创建生产线模型</li>
                      </ol>

                      <Paragraph strong>步骤 2: 导入数据写入代码</Paragraph>
                      <ol>
                        <li>在同一个 Frame 中创建新的 Method</li>
                        <li>将"数据写入代码"复制到 Method 编辑器中</li>
                        <li>运行 Method 设置参数并开始仿真</li>
                      </ol>

                      <Paragraph strong>步骤 3: 运行仿真</Paragraph>
                      <ul>
                        <li>检查生成的模型结构是否正确</li>
                        <li>调整参数以满足实际需求</li>
                        <li>运行仿真并分析结果</li>
                      </ul>
                    </div>
                  }
                  type="info"
                  showIcon
                />
              </TabPane>
            </Tabs>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="📋 下一步操作">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button
                type="primary"
                block
                size="large"
                icon={<DownloadOutlined />}
                onClick={() => {
                  downloadCode('plant_simulation_full_code.txt', 
                    `-- 模型建立代码\n${generatedCode.modelCode}\n\n-- 数据写入代码\n${generatedCode.dataCode}`)
                }}
              >
                下载完整代码包
              </Button>

              <Button
                block
                size="large"
                icon={<CopyOutlined />}
                onClick={() => {
                  copyToClipboard(`-- 模型建立代码\n${generatedCode.modelCode}\n\n-- 数据写入代码\n${generatedCode.dataCode}`)
                }}
              >
                复制完整代码
              </Button>

              <Button
                block
                size="large"
                icon={<EyeOutlined />}
                onClick={handleViewVisualization}
              >
                返回查看可视化
              </Button>

              <Button
                block
                size="large"
                icon={<HomeOutlined />}
                onClick={handleBackToHome}
              >
                返回首页创建新模型
              </Button>
            </Space>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="💡 提示与建议">
            <Alert
              message="代码使用注意事项"
              description={
                <ul style={{ margin: 0, paddingLeft: 20 }}>
                  <li>生成的代码可能需要根据实际 Plant Simulation 版本进行调整</li>
                  <li>检查节点名称和参数是否符合您的需求</li>
                  <li>建议先在测试环境中运行代码</li>
                  <li>如有问题，可以返回修改生产线描述重新生成</li>
                  <li>保存好生成的代码文件以备后续使用</li>
                </ul>
              }
              type="warning"
              showIcon
            />
            <div style={{ marginTop: 16 }}>
              <Paragraph strong>技术支持:</Paragraph>
              <Paragraph>
                如果在使用过程中遇到问题，请检查：
                <br />• Plant Simulation 版本兼容性
                <br />• 代码语法是否正确
                <br />• 节点参数是否合理
              </Paragraph>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default CodeGenerationPage