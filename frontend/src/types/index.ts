// 生产线节点类型
export type NodeType = '源' | '工位' | '缓冲区' | '传送器' | '物料终结' | 'unknown'

// 时间参数接口
export interface TimeParameter {
  distribution_pattern?: string
  parameters?: Record<string, number>
  interval_time?: string | TimeParameter
  start_time?: string
  stop_time?: string
  processing_time?: string | TimeParameter
  duration_time?: string | TimeParameter
}

// 故障参数接口
export interface FailureParameter {
  failure_name: string
  interval_time: string | TimeParameter
  duration_time: string | TimeParameter
}

// 生产状态接口
export interface ProductionStatus {
  qualified: number
  unqualified: number
}

// 生产目的地接口
export interface ProductionDestination {
  qualified: string
  unqualified: string
}

// 节点数据接口
export interface NodeData {
  time?: TimeParameter
  failure?: FailureParameter
  production_status?: ProductionStatus
  production_destination?: ProductionDestination
  capacity?: number | string
  length?: number | string
  width?: number | string
  speed?: number | string
  [key: string]: any
}

// 节点接口
export interface Node {
  name: string
  type: NodeType
  data: NodeData
}

// 边接口
export interface Edge {
  from: string
  to: string
}

// 图数据结构接口
export interface GraphData {
  nodes: Node[]
  edges: Edge[]
}

// API响应接口
export interface ApiResponse<T = any> {
  success: boolean
  message: string
  data?: T
}

// 可视化节点样式
export interface NodeStyle {
  color: string
  shape: string
  size?: number
}

// 节点样式映射
export const NODE_STYLES: Record<NodeType, NodeStyle> = {
  '源': { color: '#4CAF50', shape: 'circle' },
  '缓冲区': { color: '#FFEB3B', shape: 'box' },
  '工位': { color: '#2196F3', shape: 'diamond' },
  '传送器': { color: '#9C27B0', shape: 'triangle' },
  '物料终结': { color: '#F44336', shape: 'ellipse' },
  'unknown': { color: '#9E9E9E', shape: 'circle' }
}