import { useState, useEffect } from 'react'
import { Card, Row, Col, Button, Space, message, Descriptions, Tag, Divider } from 'antd'
import { ArrowLeftOutlined, CheckOutlined, EditOutlined, CodeOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import ProductionLineGraph from '../components/visualization/ProductionLineGraph'
import { GraphData, Node } from '../types'
import { apiService } from '../services/api_simple'

const VisualizationPage = () => {
  const navigate = useNavigate()
  const [graphData, setGraphData] = useState<GraphData | null>(null)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [loading, setLoading] = useState(false)

  // 从本地存储加载数据
  useEffect(() => {
    const savedData = localStorage.getItem('graphData')
    if (savedData) {
      try {
        const parsedData = JSON.parse(savedData)
        setGraphData(parsedData)
      } catch (error) {
        message.error('加载数据失败')
        console.error(error)
      }
    } else {
      message.warning('没有找到生产线数据，请先输入描述生成模型')
      navigate('/')
    }
  }, [navigate])

  const handleNodeClick = (node: Node) => {
    setSelectedNode(node)
  }

  const handleConfirm = async () => {
    if (!graphData) {
      message.error('没有可用的图数据')
      return
    }
    
    setLoading(true)
    
    try {
      // 调用真实API生成代码
      const response = await apiService.confirmAndGenerateCode(graphData)
      
      if (response.success && response.data) {
        // 保存生成的代码到localStorage，供CodeGenerationPage使用
        localStorage.setItem('generatedCode', JSON.stringify({
          modelCode: response.data.modelCode,
          dataCode: response.data.dataCode,
          timestamp: new Date().toISOString()
        }))
        
        message.success('模型确认成功！代码已生成。')
        navigate('/code-generation')
      } else {
        message.error(response.message || '生成代码失败')
      }
    } catch (error) {
      console.error('生成代码时出错:', error)
      message.error('生成代码时发生错误，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = () => {
    message.info('编辑功能开发中...')
  }

  const handleBack = () => {
    navigate('/')
  }

  if (!graphData) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <p>加载中...</p>
          <Button onClick={handleBack} icon={<ArrowLeftOutlined />}>
            返回首页
          </Button>
        </div>
      </Card>
    )
  }

  // 统计信息
  const nodeCount = graphData.nodes.length
  const edgeCount = graphData.edges.length
  const nodeTypes = graphData.nodes.reduce((acc: Record<string, number>, node) => {
    acc[node.type] = (acc[node.type] || 0) + 1
    return acc
  }, {})

  return (
    <div className="visualization-page">
      <Row gutter={[24, 24]}>
        <Col span={24}>
          <Card
            title="📊 生产线可视化确认"
            extra={
              <Space>
                <Button icon={<ArrowLeftOutlined />} onClick={handleBack}>
                  返回
                </Button>
                <Button icon={<EditOutlined />} onClick={handleEdit}>
                  编辑模型
                </Button>
                <Button
                  type="primary"
                  icon={<CheckOutlined />}
                  loading={loading}
                  onClick={handleConfirm}
                >
                  确认并生成代码
                </Button>
              </Space>
            }
          >
            <p>
              请检查生成的生产线有向图模型是否正确。点击节点查看详细信息，确认无误后点击"确认并生成代码"。
            </p>
          </Card>
        </Col>

        <Col xs={24} lg={16}>
          <ProductionLineGraph
            data={graphData}
            width={800}
            height={600}
            onNodeClick={handleNodeClick}
            editable={true}
          />
        </Col>

        <Col xs={24} lg={8}>
          <Row gutter={[24, 24]}>
            <Col span={24}>
              <Card title="📈 模型统计">
                <Descriptions column={1} size="small">
                  <Descriptions.Item label="节点总数">{nodeCount}</Descriptions.Item>
                  <Descriptions.Item label="边总数">{edgeCount}</Descriptions.Item>
                  <Descriptions.Item label="节点类型分布">
                    <Space wrap>
                      {Object.entries(nodeTypes).map(([type, count]) => (
                        <Tag key={type} color="blue">
                          {type}: {count}
                        </Tag>
                      ))}
                    </Space>
                  </Descriptions.Item>
                </Descriptions>
              </Card>
            </Col>

            <Col span={24}>
              <Card title="🔍 选中节点详情">
                {selectedNode ? (
                  <Descriptions column={1} size="small" bordered>
                    <Descriptions.Item label="节点名称">
                      <strong>{selectedNode.name}</strong>
                    </Descriptions.Item>
                    <Descriptions.Item label="节点类型">
                      <Tag color="blue">{selectedNode.type}</Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="属性数量">
                      {Object.keys(selectedNode.data).length}
                    </Descriptions.Item>
                    <Descriptions.Item label="主要属性">
                      <div style={{ maxHeight: '200px', overflow: 'auto' }}>
                        <pre style={{ margin: 0, fontSize: '12px' }}>
                          {JSON.stringify(selectedNode.data, null, 2)}
                        </pre>
                      </div>
                    </Descriptions.Item>
                  </Descriptions>
                ) : (
                  <div style={{ textAlign: 'center', padding: '20px 0', color: '#999' }}>
                    点击图中的节点查看详情
                  </div>
                )}
              </Card>
            </Col>

            <Col span={24}>
              <Card title="💡 操作指南">
                <ul style={{ margin: 0, paddingLeft: 20 }}>
                  <li>点击节点查看详细信息</li>
                  <li>拖拽节点调整布局位置</li>
                  <li>检查节点类型和属性是否正确</li>
                  <li>确认连接关系是否符合预期</li>
                  <li>点击"确认并生成代码"进入下一步</li>
                </ul>
                <Divider />
                <Button
                  type="primary"
                  block
                  icon={<CodeOutlined />}
                  onClick={handleConfirm}
                  loading={loading}
                >
                  确认并生成Plant Simulation代码
                </Button>
              </Card>
            </Col>
          </Row>
        </Col>
      </Row>
    </div>
  )
}

export default VisualizationPage