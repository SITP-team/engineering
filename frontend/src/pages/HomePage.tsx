import { useState } from 'react'
import { Card, Row, Col, Button, Input, Form, message, Steps, Typography } from 'antd'
import { SendOutlined, EyeOutlined, CodeOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { generateGraphFromText } from '../services/api'

const { TextArea } = Input
const { Title, Paragraph } = Typography
const { Step } = Steps

const HomePage = () => {
  const [form] = Form.useForm()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)

  const handleSubmit = async (values: { description: string }) => {
    setLoading(true)
    try {
      const result = await generateGraphFromText(values.description)
      if (result.success) {
        message.success('生产线模型生成成功！')
        // 存储数据到本地状态或全局状态
        localStorage.setItem('graphData', JSON.stringify(result.data))
        setCurrentStep(1)
        navigate('/visualization')
      } else {
        message.error(result.message || '生成失败，请重试')
      }
    } catch (error) {
      message.error('请求失败，请检查网络连接')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const steps = [
    {
      title: '输入描述',
      description: '用自然语言描述生产线',
      icon: <SendOutlined />,
    },
    {
      title: '可视化确认',
      description: '查看并调整有向图',
      icon: <EyeOutlined />,
    },
    {
      title: '代码生成',
      description: '生成Plant Simulation代码',
      icon: <CodeOutlined />,
    },
  ]

  return (
    <div className="home-page">
      <Row gutter={[24, 24]}>
        <Col span={24}>
          <Card>
            <Title level={2}>🚀 欢迎使用 Plant Simulation 自动化建模工具</Title>
            <Paragraph>
              本工具通过自然语言描述自动生成生产线有向图模型，并转换为Plant Simulation代码。
              只需简单描述您的生产线，系统将自动完成建模过程。
            </Paragraph>
          </Card>
        </Col>

        <Col span={24}>
          <Card title="建模流程">
            <Steps current={currentStep} items={steps} />
          </Card>
        </Col>

        <Col xs={24} lg={16}>
          <Card title="📝 生产线描述输入">
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSubmit}
              initialValues={{
                description: '源节点每10分钟生成一个产品，加工工位处理时间5分钟，缓冲区容量10，传送器长度2米速度1米/秒',
              }}
            >
              <Form.Item
                name="description"
                label="请输入生产线描述"
                rules={[{ required: true, message: '请输入生产线描述' }]}
              >
                <TextArea
                  rows={6}
                  placeholder="例如：源节点每10分钟生成一个产品，加工工位处理时间5分钟，缓冲区容量10，传送器长度2米速度1米/秒，物料终结节点接收成品..."
                  maxLength={1000}
                  showCount
                />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  icon={<SendOutlined />}
                  size="large"
                >
                  生成生产线模型
                </Button>
                <Button
                  style={{ marginLeft: 16 }}
                  onClick={() => {
                    form.setFieldsValue({
                      description: '源节点每10分钟生成一个产品，加工工位处理时间5分钟，缓冲区容量10，传送器长度2米速度1米/秒，物料终结节点接收成品',
                    })
                  }}
                >
                  使用示例
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card title="💡 使用提示">
            <Paragraph strong>描述建议：</Paragraph>
            <ul>
              <li>明确节点类型：源、工位、缓冲区、传送器、物料终结</li>
              <li>指定时间参数：间隔时间、处理时间、故障间隔等</li>
              <li>描述连接关系：节点之间的流向</li>
              <li>包含容量信息：缓冲区容量、传送器容量</li>
            </ul>
            <Paragraph strong>示例：</Paragraph>
            <pre style={{ background: '#f6f8fa', padding: 12, borderRadius: 6 }}>
              源节点每15分钟生成产品
              加工工位处理时间8分钟
              缓冲区容量5
              传送器长度3米，速度0.5米/秒
              物料终结节点接收成品
            </pre>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default HomePage