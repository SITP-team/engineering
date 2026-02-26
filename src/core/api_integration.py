#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plant Simulation 自动化建模工具 - API集成模块
将核心算法封装为API可调用的函数
"""

import json
import sys
import os
import time
from typing import Dict, Any, Tuple, Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.api_utils import make_api_request
from src.utils.json_utils import extract_json_from_response
from src.utils.graph_preprocessor import convert_zero_capacity_conveyors_to_edges
from src.generation.simtalk_generator import json_to_simtalk
from src.visualization.visualize import ProductionLineVisualizer
from src.config.dynamic_prompt import DynamicPromptGenerator
from src.generation.standardization import standardize_text

# 可选导入plant_simulator，如果不可用则提供降级方案
try:
    from src.generation.plant_simulator import create_plant_simulation_model
    PLANT_SIMULATOR_AVAILABLE = True
except ImportError:
    PLANT_SIMULATOR_AVAILABLE = False
    print("[WARN] plant_simulator模块不可用，Plant Simulation模型创建功能将受限")


class PlantSimulationAPI:
    """Plant Simulation API集成类"""
    
    def __init__(self):
        self.conversation_history = []
        self.prompt_generator = DynamicPromptGenerator()
        
    def generate_graph_from_text(self, description: str) -> Dict[str, Any]:
        """
        从文本描述生成图数据
        
        Args:
            description: 生产线描述文本
            
        Returns:
            包含图数据的字典
        """
        try:
            # 安全打印，避免编码问题
            safe_desc = description[:100].encode('ascii', 'ignore').decode('ascii', 'ignore')
            print(f"[DEBUG] 开始处理文本描述: {safe_desc}...")
            
            # 文本标准化
            standardized_text = standardize_text(description)
            if standardized_text:
                print("[INFO] 文本标准化完成")
                processed_text = standardized_text
            else:
                print("[WARN] 标准化处理失败，使用原始文本")
                processed_text = description
            
            # 生成动态提示
            dynamic_prompt = self.prompt_generator.generate_dynamic_prompt(processed_text)
            
            # 构造请求消息
            messages = [{"role": "system", "content": dynamic_prompt}]
            messages.append({"role": "user", "content": processed_text})
            
            # 调用API生成图数据
            print("[INFO] 正在生成有向图数据结构...")
            result = make_api_request(messages)
            reply = result["choices"][0]["message"]["content"]
            
            # 提取JSON数据
            print("[INFO] 提取模型数据结构...")
            graph_data = extract_json_from_response(reply)
            
            if not graph_data:
                # 检查是否是询问而不是JSON
                if "?" in reply or "请" in reply or "需要" in reply or "缺少" in reply:
                    raise ValueError(f"需要补充信息: {reply}")
                else:
                    raise ValueError("无法从响应中提取有效的JSON数据")
            
            print("[INFO] 成功解析有向图数据结构！")
            
            # 处理并验证图数据
            print("[INFO] 处理并验证图数据结构...")
            is_valid, process_msg, processed_graph = (
                ProductionLineVisualizer.process_and_validate_graph_data(graph_data)
            )
            
            if not is_valid:
                raise ValueError(f"图数据结构无效: {process_msg}")
            
            # 安全打印处理消息
            safe_msg = process_msg.encode('ascii', 'ignore').decode('ascii', 'ignore')
            print(safe_msg)
            graph_data = processed_graph  # 使用处理后的图数据
            
            # 处理容量为0的传送器节点
            print("[INFO] 检查容量为0的传送器节点...")
            graph_data = convert_zero_capacity_conveyors_to_edges(graph_data)
            print("[INFO] 成功处理容量为0的传送器节点")
            
            return {
                "success": True,
                "message": "图数据生成成功",
                "data": graph_data
            }
            
        except Exception as e:
            # 安全处理错误消息
            try:
                error_msg = str(e)
            except:
                error_msg = "未知错误"
            
            # 确保错误消息不包含Unicode字符
            safe_error_msg = error_msg.encode('ascii', 'ignore').decode('ascii', 'ignore')
            print(f"[ERROR] 生成图数据过程中发生错误: {safe_error_msg}")
            return {
                "success": False,
                "message": f"生成图数据失败: {safe_error_msg}",
                "data": None
            }
    
    def confirm_and_generate_code(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        确认图数据并生成Plant Simulation代码
        
        Args:
            graph_data: 图数据
            
        Returns:
            包含生成代码的字典
        """
        try:
            print(f"[DEBUG] 开始生成代码，节点数: {len(graph_data.get('nodes', []))}")
            
            # 生成Plant Simulation代码
            print("[INFO] 正在生成Plant Simulation代码...")
            model_setup_code, data_writing_code = json_to_simtalk(graph_data)
            
            print("[INFO] 代码生成成功")
            
            return {
                "success": True,
                "message": "代码生成成功",
                "data": {
                    "modelCode": model_setup_code,
                    "dataCode": data_writing_code
                }
            }
            
        except Exception as e:
            print(f"[ERROR] 生成代码过程中发生错误: {str(e)}")
            return {
                "success": False,
                "message": f"生成代码失败: {str(e)}",
                "data": None
            }
    
    def create_plant_simulation_model(self, model_code: str, data_code: str) -> Dict[str, Any]:
        """
        创建Plant Simulation模型
        
        Args:
            model_code: 模型建立代码
            data_code: 数据写入代码
            
        Returns:
            操作结果
        """
        try:
            print("[INFO] 正在创建Plant Simulation模型...")
            
            if not PLANT_SIMULATOR_AVAILABLE:
                print("[WARN] Plant Simulation模块不可用，无法创建实际模型")
                print("[INFO] 生成的代码已保存，可以手动导入到Plant Simulation中")
                return {
                    "success": True,
                    "message": "Plant Simulation模块不可用，代码已生成但无法自动创建模型"
                }
            
            success = create_plant_simulation_model(model_code, data_code)
            
            if success:
                print("[INFO] 模型创建及数据处理成功！Plant Simulation即将启动...")
                return {
                    "success": True,
                    "message": "Plant Simulation模型创建成功"
                }
            else:
                print("[ERROR] 模型创建失败")
                return {
                    "success": False,
                    "message": "Plant Simulation模型创建失败"
                }
                
        except Exception as e:
            print(f"[ERROR] 创建模型过程中发生错误: {str(e)}")
            return {
                "success": False,
                "message": f"创建模型失败: {str(e)}"
            }
    
    def validate_graph_data(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证图数据有效性
        
        Args:
            graph_data: 图数据
            
        Returns:
            验证结果
        """
        try:
            issues = []
            
            # 基本验证
            if not graph_data.get('nodes'):
                issues.append("图数据中没有节点")
            
            if not graph_data.get('edges'):
                issues.append("图数据中没有边")
            
            # 检查节点名称唯一性
            node_names = [node.get('name', '') for node in graph_data.get('nodes', [])]
            duplicate_names = [name for name in node_names if node_names.count(name) > 1]
            if duplicate_names:
                issues.append(f"存在重复的节点名称: {', '.join(set(duplicate_names))}")
            
            # 检查边引用
            for edge in graph_data.get('edges', []):
                if edge.get('from') not in node_names:
                    issues.append(f"边引用了不存在的源节点: {edge.get('from')}")
                if edge.get('to') not in node_names:
                    issues.append(f"边引用了不存在的目标节点: {edge.get('to')}")
            
            return {
                "success": True,
                "message": "验证完成",
                "data": {
                    "isValid": len(issues) == 0,
                    "issues": issues
                }
            }
            
        except Exception as e:
            print(f"[ERROR] 验证图数据过程中发生错误: {str(e)}")
            return {
                "success": False,
                "message": f"验证图数据失败: {str(e)}",
                "data": {
                    "isValid": False,
                    "issues": [f"验证过程发生错误: {str(e)}"]
                }
            }


# 创建全局实例
api_integration = PlantSimulationAPI()