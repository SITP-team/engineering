import axios from 'axios'
import { GraphData, ApiResponse } from '../types'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

// API服务
export const apiService = {
  // 从文本生成图数据
  async generateGraphFromText(text: string): Promise<ApiResponse<GraphData>> {
    try {
      console.log('调用API生成图数据，输入文本:', text)
      
      // 调用真实API
      const response = await api.post('/generate', {
        description: text
      })
      
      // axios拦截器已经返回了data，所以response就是ApiResponse类型
      return response as ApiResponse<GraphData>
    } catch (error) {
      console.error('生成图数据失败:', error)
      
      // 如果API调用失败，返回模拟数据作为降级方案
      console.log('API调用失败，使用模拟数据')
      const mockData: GraphData = {
        nodes: [
          {
            name: '源节点',
            type: '源',
            data: {
              time: {
                interval_time: '0:0:10:0',
                start_time: '0:0:0:0',
                stop_time: '1:0:0:0',
              },
            },
          },
          {
            name: '加工工位',
            type: '工位',
            data: {
              time: {
                processing_time: {
                  distribution_pattern: 'normal',
                  parameters: {
                    mean: 200,
                    sigma: 900,
                  },
                },
              },
              failure: {
                failure_name: 'failure1',
                interval_time: '0:0:33:20',
                duration_time: '0:0:3:20',
              },
            },
          },
          {
            name: '缓冲区',
            type: '缓冲区',
            data: {
              capacity: 10,
            },
          },
          {
            name: '传送器',
            type: '传送器',
            data: {
              capacity: 2,
              length: 2,
              width: 0.5,
              speed: 1,
            },
          },
          {
            name: '物料终结',
            type: '物料终结',
            data: {},
          },
        ],
        edges: [
          { from: '源节点', to: '缓冲区' },
          { from: '缓冲区', to: '加工工位' },
          { from: '加工工位', to: '传送器' },
          { from: '传送器', to: '物料终结' },
        ],
      }

      return {
        success: true,
        message: '图数据生成成功（模拟数据）',
        data: mockData,
      }
    }
  },

  // 确认图数据并生成代码
  async confirmAndGenerateCode(graphData: GraphData): Promise<ApiResponse<{ modelCode: string; dataCode: string }>> {
    try {
      console.log('调用API确认图数据并生成代码，节点数:', graphData.nodes.length)
      
      // 调用真实API
      const response = await api.post('/confirm', {
        graphData: graphData
      })
      
      return response
    } catch (error) {
      console.error('生成代码失败:', error)
      
      // 如果API调用失败，返回模拟代码作为降级方案
      console.log('API调用失败，使用模拟代码')
      const mockModelCode = `-- Plant Simulation 模型建立代码
is
do
  -- 创建源节点
  .Models.Frame.createSource("源节点")
  .Models.Frame.Source.interval_time := "0:0:10:0"
  .Models.Frame.Source.start_time := "0:0:0:0"
  .Models.Frame.Source.stop_time := "1:0:0:0"
  
  -- 创建加工工位
  .Models.Frame.createSingleProc("加工工位")
  .Models.Frame.SingleProc.procTime := "0:0:5:0"
  
  -- 创建缓冲区
  .Models.Frame.createBuffer("缓冲区")
  .Models.Frame.Buffer.capacity := 10
  
  -- 创建传送器
  .Models.Frame.createLine("传送器")
  .Models.Frame.Line.length := 2
  .Models.Frame.Line.width := 0.5
  .Models.Frame.Line.speed := 1
  
  -- 创建物料终结
  .Models.Frame.createDrain("物料终结")
  
  -- 连接节点
  .Models.Frame.connect("源节点", "out", "缓冲区", "in")
  .Models.Frame.connect("缓冲区", "out", "加工工位", "in")
  .Models.Frame.connect("加工工位", "out", "传送器", "in")
  .Models.Frame.connect("传送器", "out", "物料终结", "in")
end`

      const mockDataCode = `-- Plant Simulation 数据写入代码
is
do
  -- 设置加工工位故障参数
  .Models.Frame.SingleProc.failure.active := true
  .Models.Frame.SingleProc.failure.interval_time := "0:0:33:20"
  .Models.Frame.SingleProc.failure.duration_time := "0:0:3:20"
  
  -- 设置处理时间分布
  .Models.Frame.SingleProc.procTime := "normal(200, 900)"
  
  -- 设置传送器参数
  .Models.Frame.Line.capacity := 2
  
  -- 设置仿真参数
  .Models.Frame.reset
  .Models.Frame.simulate(3600) -- 仿真1小时
end`

      return {
        success: true,
        message: '代码生成成功（模拟代码）',
        data: {
          modelCode: mockModelCode,
          dataCode: mockDataCode,
        },
      }
    }
  },

  // 获取默认示例
  async getDefaultExamples(): Promise<ApiResponse<string[]>> {
    try {
      const examples = [
        '源节点每10分钟生成一个产品，加工工位处理时间5分钟，缓冲区容量10，传送器长度2米速度1米/秒',
        '生产线包含3个加工工位，每个工位处理时间8分钟，缓冲区容量5，传送器连接各工位',
        '复杂生产线：源节点每15分钟生成产品，经过缓冲区(容量8)到加工工位(处理时间10分钟，有故障)，最后到物料终结',
        '汽车装配线：车身焊接工位(12分钟)，喷漆工位(15分钟)，装配工位(20分钟)，缓冲区容量各为3',
      ]

      return {
        success: true,
        message: '获取示例成功',
        data: examples,
      }
    } catch (error) {
      console.error('获取示例失败:', error)
      return {
        success: false,
        message: '获取示例失败',
      }
    }
  },

  // 验证图数据
  async validateGraphData(graphData: GraphData): Promise<ApiResponse<{ isValid: boolean; issues: string[] }>> {
    try {
      // 简单验证
      const issues: string[] = []
      
      if (!graphData.nodes.length) {
        issues.push('图数据中没有节点')
      }
      
      if (!graphData.edges.length) {
        issues.push('图数据中没有边')
      }
      
      // 检查节点名称唯一性
      const nodeNames = graphData.nodes.map(node => node.name)
      const duplicateNames = nodeNames.filter((name, index) => nodeNames.indexOf(name) !== index)
      if (duplicateNames.length) {
        issues.push(`存在重复的节点名称: ${duplicateNames.join(', ')}`)
      }
      
      // 检查边引用
      for (const edge of graphData.edges) {
        if (!nodeNames.includes(edge.from)) {
          issues.push(`边引用了不存在的源节点: ${edge.from}`)
        }
        if (!nodeNames.includes(edge.to)) {
          issues.push(`边引用了不存在的目标节点: ${edge.to}`)
        }
      }

      return {
        success: true,
        message: issues.length ? '验证发现问题' : '验证通过',
        data: {
          isValid: issues.length === 0,
          issues,
        },
      }
    } catch (error) {
      console.error('验证图数据失败:', error)
      return {
        success: false,
        message: '验证图数据失败',
        data: {
          isValid: false,
          issues: ['验证过程发生错误'],
        },
      }
    }
  },
}

// 导出函数别名
export const generateGraphFromText = apiService.generateGraphFromText
export const confirmAndGenerateCode = apiService.confirmAndGenerateCode
export const getDefaultExamples = apiService.getDefaultExamples
export const validateGraphData = apiService.validateGraphData

export default apiService