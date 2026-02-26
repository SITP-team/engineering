#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plant Simulation 自动化建模工具 - API服务器
连接前端React应用和Python后端
"""

import json
import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 导入实际算法模块
USE_REAL_ALGORITHM = False
api_integration = None

# 模拟数据 - 用于降级方案
SAMPLE_GRAPH_DATA = {
    "nodes": [
        {
            "name": "源节点",
            "type": "源",
            "data": {
                "time": {
                    "interval_time": "0:0:10:0",
                    "start_time": "0:0:0:0",
                    "stop_time": "1:0:0:0",
                },
            },
        },
        {
            "name": "加工工位",
            "type": "工位",
            "data": {
                "time": {
                    "processing_time": {
                        "distribution_pattern": "normal",
                        "parameters": {
                            "mean": 200,
                            "sigma": 900,
                        },
                    },
                },
                "failure": {
                    "failure_name": "failure1",
                    "interval_time": "0:0:33:20",
                    "duration_time": "0:0:3:20",
                },
            },
        },
        {
            "name": "缓冲区",
            "type": "缓冲区",
            "data": {
                "capacity": 10,
            },
        },
        {
            "name": "传送器",
            "type": "传送器",
            "data": {
                "capacity": 2,
                "length": 2,
                "width": 0.5,
                "speed": 1,
            },
        },
        {
            "name": "物料终结",
            "type": "物料终结",
            "data": {},
        },
    ],
    "edges": [
        {"from": "源节点", "to": "缓冲区"},
        {"from": "缓冲区", "to": "加工工位"},
        {"from": "加工工位", "to": "传送器"},
        {"from": "传送器", "to": "物料终结"},
    ],
}

try:
    from src.core.api_integration import api_integration as imported_api_integration
    api_integration = imported_api_integration
    USE_REAL_ALGORITHM = True
    print("[INFO] 成功导入实际算法模块")
except ImportError as e:
    print(f"[WARN] 无法导入实际算法模块: {e}")
    import traceback
    traceback.print_exc()
    print("[WARN] 将使用模拟数据作为降级方案")
except Exception as e:
    print(f"[WARN] 导入实际算法模块时发生错误: {e}")
    import traceback
    traceback.print_exc()
    print("[WARN] 将使用模拟数据作为降级方案")
    
    # 模拟数据 - 用于降级方案
    SAMPLE_GRAPH_DATA = {
        "nodes": [
            {
                "name": "源节点",
                "type": "源",
                "data": {
                    "time": {
                        "interval_time": "0:0:10:0",
                    "start_time": "0:0:0:0",
                    "stop_time": "1:0:0:0"
                }
            }
        },
        {
            "name": "加工工位",
            "type": "工位",
            "data": {
                "time": {
                    "processing_time": {
                        "distribution_pattern": "normal",
                        "parameters": {
                            "mean": 200,
                            "sigma": 900
                        }
                    }
                },
                "failure": {
                    "failure_name": "failure1",
                    "interval_time": "0:0:33:20",
                    "duration_time": "0:0:3:20"
                }
            }
        },
        {
            "name": "缓冲区",
            "type": "缓冲区",
            "data": {
                "capacity": 10
            }
        },
        {
            "name": "传送器",
            "type": "传送器",
            "data": {
                "capacity": 2,
                "length": 2,
                "width": 0.5,
                "speed": 1
            }
        },
        {
            "name": "物料终结",
            "type": "物料终结",
            "data": {}
        }
    ],
    "edges": [
        {"from": "源节点", "to": "缓冲区"},
        {"from": "缓冲区", "to": "加工工位"},
        {"from": "加工工位", "to": "传送器"},
        {"from": "传送器", "to": "物料终结"}
    ]
}

# Plant Simulation 代码模板
PLANT_SIMULATION_CODE = {
    "modelCode": """-- Plant Simulation 模型建立代码
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
end""",
    "dataCode": """-- Plant Simulation 数据写入代码
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
end"""
}

@app.route('/')
def index():
    """API服务器状态"""
    return jsonify({
        "status": "running",
        "name": "Plant Simulation API Server",
        "version": "1.0.0",
        "endpoints": {
            "/api/generate": "POST - 从文本生成图数据",
            "/api/confirm": "POST - 确认图数据并生成代码",
            "/api/examples": "GET - 获取示例描述",
            "/api/health": "GET - 健康检查"
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({"status": "healthy", "timestamp": time.time()})

@app.route('/api/examples', methods=['GET'])
def get_examples():
    """获取示例生产线描述"""
    examples = [
        "源节点每10分钟生成一个产品，加工工位处理时间5分钟，缓冲区容量10，传送器长度2米速度1米/秒",
        "生产线包含3个加工工位，每个工位处理时间8分钟，缓冲区容量5，传送器连接各工位",
        "复杂生产线：源节点每15分钟生成产品，经过缓冲区(容量8)到加工工位(处理时间10分钟，有故障)，最后到物料终结",
        "汽车装配线：车身焊接工位(12分钟)，喷漆工位(15分钟)，装配工位(20分钟)，缓冲区容量各为3",
    ]
    return jsonify({
        "success": True,
        "message": "获取示例成功",
        "data": examples
    })

@app.route('/api/generate', methods=['POST'])
def generate_graph():
    """从文本生成图数据"""
    try:
        data = request.get_json()
        if not data or 'description' not in data:
            return jsonify({
                "success": False,
                "message": "缺少描述文本"
            }), 400
        
        description = data['description']
        print(f"收到生成请求: {description[:100]}...")
        
        # 调用实际的Python后端处理
        if USE_REAL_ALGORITHM and api_integration:
            print("[INFO] 使用实际算法处理...")
            result = api_integration.generate_graph_from_text(description)
            
            if result["success"]:
                return jsonify({
                    "success": True,
                    "message": result["message"],
                    "data": result["data"]
                })
            else:
                return jsonify({
                    "success": False,
                    "message": result["message"]
                }), 500
        else:
            # 降级方案：返回模拟数据
            print("[WARN] 使用模拟数据（实际算法不可用）")
            time.sleep(1)  # 模拟处理延迟
            
            return jsonify({
                "success": True,
                "message": "图数据生成成功（模拟数据）",
                "data": SAMPLE_GRAPH_DATA
            })
        
    except Exception as e:
        print(f"生成图数据错误: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"生成图数据失败: {str(e)}"
        }), 500

@app.route('/api/confirm', methods=['POST'])
def confirm_and_generate():
    """确认图数据并生成Plant Simulation代码"""
    try:
        data = request.get_json()
        if not data or 'graphData' not in data:
            return jsonify({
                "success": False,
                "message": "缺少图数据"
            }), 400
        
        graph_data = data['graphData']
        print(f"收到确认请求，节点数: {len(graph_data.get('nodes', []))}")
        
        # 这里可以调用实际的Python后端生成代码
        # 暂时返回模拟代码
        
        # 模拟处理延迟
        time.sleep(1.5)
        
        return jsonify({
            "success": True,
            "message": "代码生成成功",
            "data": PLANT_SIMULATION_CODE
        })
        
    except Exception as e:
        print(f"生成代码错误: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"生成代码失败: {str(e)}"
        }), 500

@app.route('/api/validate', methods=['POST'])
def validate_graph():
    """验证图数据有效性"""
    try:
        data = request.get_json()
        if not data or 'graphData' not in data:
            return jsonify({
                "success": False,
                "message": "缺少图数据"
            }), 400
        
        graph_data = data['graphData']
        issues = []
        
        # 简单验证
        if not graph_data.get('nodes'):
            issues.append("图数据中没有节点")
        
        if not graph_data.get('edges'):
            issues.append("图数据中没有边")
        
        # 检查节点名称唯一性
        node_names = [node.get('name', '') for node in graph_data.get('nodes', [])]
        duplicate_names = [name for name in node_names if node_names.count(name) > 1]
        if duplicate_names:
            issues.append(f"存在重复的节点名称: {', '.join(set(duplicate_names))}")
        
        return jsonify({
            "success": True,
            "message": "验证完成",
            "data": {
                "isValid": len(issues) == 0,
                "issues": issues
            }
        })
        
    except Exception as e:
        print(f"验证图数据错误: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"验证图数据失败: {str(e)}"
        }), 500

def start_api_server(port=5000):
    """启动API服务器"""
    print("启动 Plant Simulation API 服务器...")
    print(f"监听端口: {port}")
    print(f"前端地址: http://localhost:3000")
    print(f"API地址: http://localhost:{port}")
    print("可用端点:")
    print("   GET  /api/health     - 健康检查")
    print("   GET  /api/examples   - 获取示例")
    print("   POST /api/generate   - 生成图数据")
    print("   POST /api/confirm    - 生成代码")
    print("   POST /api/validate   - 验证图数据")
    
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    start_api_server(5000)