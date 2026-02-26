import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { Card, Button, Modal, Descriptions, Tag, Space } from 'antd'
import { EditOutlined, SaveOutlined, EyeOutlined } from '@ant-design/icons'
import { GraphData, Node, NODE_STYLES, NodeType } from '../../types'

interface ProductionLineGraphProps {
  data: GraphData
  width?: number
  height?: number
  onNodeClick?: (node: Node) => void
  editable?: boolean
}

const ProductionLineGraph: React.FC<ProductionLineGraphProps> = ({
  data,
  width = 800,
  height = 600,
  onNodeClick,
  editable = false,
}) => {
  const svgRef = useRef<SVGSVGElement>(null)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [graphData, setGraphData] = useState<GraphData>(data)

  // 初始化D3图形
  useEffect(() => {
    if (!svgRef.current || !graphData.nodes.length) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const g = svg.append('g')

    // 创建力导向图模拟
    const simulation = d3
      .forceSimulation(graphData.nodes as any)
      .force(
        'link',
        d3
          .forceLink(graphData.edges)
          .id((d: any) => d.name)
          .distance(100)
      )
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(60))

    // 绘制边
    const link = g
      .append('g')
      .selectAll('line')
      .data(graphData.edges)
      .enter()
      .append('line')
      .attr('stroke', '#999')
      .attr('stroke-width', 2)
      .attr('stroke-opacity', 0.6)
      .attr('marker-end', 'url(#arrowhead)')

    // 绘制节点
    const node = g
      .append('g')
      .selectAll('g')
      .data(graphData.nodes)
      .enter()
      .append('g')
      .call(
        d3
          .drag<any, any>()
          .on('start', dragstarted)
          .on('drag', dragged)
          .on('end', dragended)
      )
      .on('click', (event, d) => {
        setSelectedNode(d)
        if (onNodeClick) onNodeClick(d)
        setIsModalVisible(true)
      })

    // 添加节点形状
    node
      .append('circle')
      .attr('r', 30)
      .attr('fill', (d: Node) => NODE_STYLES[d.type].color)
      .attr('stroke', '#333')
      .attr('stroke-width', 2)

    // 添加节点标签
    node
      .append('text')
      .text((d: Node) => d.name)
      .attr('text-anchor', 'middle')
      .attr('dy', '.35em')
      .attr('fill', 'white')
      .attr('font-weight', 'bold')
      .attr('font-size', '12px')

    // 添加节点类型标签
    node
      .append('text')
      .text((d: Node) => d.type)
      .attr('text-anchor', 'middle')
      .attr('dy', '2.5em')
      .attr('fill', '#666')
      .attr('font-size', '10px')

    // 添加箭头标记
    svg
      .append('defs')
      .append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 35)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#999')

    // 更新位置函数
    function ticked() {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y)

      node.attr('transform', (d: any) => `translate(${d.x},${d.y})`)
    }

    // 拖拽函数
    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart()
      d.fx = d.x
      d.fy = d.y
    }

    function dragged(event: any, d: any) {
      d.fx = event.x
      d.fy = event.y
    }

    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0)
      d.fx = null
      d.fy = null
    }

    simulation.on('tick', ticked)

    // 清理函数
    return () => {
      simulation.stop()
    }
  }, [graphData, width, height, onNodeClick])

  // 处理节点属性更新
  const handleNodeUpdate = (updatedNode: Node) => {
    const updatedNodes = graphData.nodes.map((node) =>
      node.name === updatedNode.name ? updatedNode : node
    )
    setGraphData({ ...graphData, nodes: updatedNodes })
  }

  // 渲染节点属性详情
  const renderNodeDetails = (node: Node) => {
    const { name, type, data } = node
    const style = NODE_STYLES[type]

    return (
      <Descriptions
        title={
          <Space>
            <div
              style={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                backgroundColor: style.color,
                display: 'inline-block',
                marginRight: 8,
              }}
            />
            <span>{name}</span>
            <Tag color={style.color}>{type}</Tag>
          </Space>
        }
        bordered
        column={1}
        size="small"
      >
        <Descriptions.Item label="节点名称">{name}</Descriptions.Item>
        <Descriptions.Item label="节点类型">{type}</Descriptions.Item>

        {data.capacity && (
          <Descriptions.Item label="容量">{data.capacity}</Descriptions.Item>
        )}

        {data.time && (
          <Descriptions.Item label="时间参数">
            <pre style={{ margin: 0, fontSize: '12px' }}>
              {JSON.stringify(data.time, null, 2)}
            </pre>
          </Descriptions.Item>
        )}

        {data.failure && (
          <Descriptions.Item label="故障参数">
            <pre style={{ margin: 0, fontSize: '12px' }}>
              {JSON.stringify(data.failure, null, 2)}
            </pre>
          </Descriptions.Item>
        )}

        {Object.keys(data).length > 0 && (
          <Descriptions.Item label="完整数据">
            <pre style={{ margin: 0, fontSize: '10px', maxHeight: '200px', overflow: 'auto' }}>
              {JSON.stringify(data, null, 2)}
            </pre>
          </Descriptions.Item>
        )}
      </Descriptions>
    )
  }

  return (
    <Card
      title="📊 生产线有向图可视化"
      extra={
        <Space>
          {editable && (
            <Button icon={<EditOutlined />} size="small">
              编辑模式
            </Button>
          )}
          <Button icon={<SaveOutlined />} size="small">
            保存布局
          </Button>
          <Button
            icon={<EyeOutlined />}
            size="small"
            onClick={() => setIsModalVisible(true)}
            disabled={!selectedNode}
          >
            查看选中节点
          </Button>
        </Space>
      }
    >
      <div style={{ overflow: 'auto', border: '1px solid #f0f0f0', borderRadius: 8 }}>
        <svg ref={svgRef} width={width} height={height} />
      </div>

      <div style={{ marginTop: 16 }}>
        <Space wrap>
          {Object.entries(NODE_STYLES).map(([type, style]) => (
            <div key={type} style={{ display: 'flex', alignItems: 'center', marginRight: 16 }}>
              <div
                style={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  backgroundColor: style.color,
                  marginRight: 8,
                }}
              />
              <span style={{ fontSize: '12px' }}>{type}</span>
            </div>
          ))}
        </Space>
      </div>

      <Modal
        title="节点属性详情"
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setIsModalVisible(false)}>
            关闭
          </Button>,
          editable && (
            <Button key="edit" type="primary" icon={<EditOutlined />}>
              编辑属性
            </Button>
          ),
        ]}
        width={600}
      >
        {selectedNode ? (
          renderNodeDetails(selectedNode)
        ) : (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            请点击图中的节点查看属性
          </div>
        )}
      </Modal>
    </Card>
  )
}

export default ProductionLineGraph