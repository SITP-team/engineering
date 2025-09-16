#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import win32com.client
import subprocess
import json
import re
import os
import pythoncom
from typing import Dict, Tuple
from src.generation.simtalk_generator import capacity_json_to_simtalk, json_to_simtalk
from src.config.path_config import (
    MODEL_FILE,
    SAVED_MODEL_FILE,
    DATA_OUTPUT_FILE,
    PLANT_SIM_PATHS,
    DEFAULT_PRODUCTION_LINE_FILE,
)


# 全局变量管理
class PlantSimState:
    """Plant Simulation状态管理类，封装全局变量"""

    _instance = None
    _plant_sim = None
    _model_loaded = False
    _model_path = ""
    _data_writing = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    @property
    def plant_sim(self):
        return self._plant_sim

    @plant_sim.setter
    def plant_sim(self, value):
        self._plant_sim = value

    @property
    def model_loaded(self):
        return self._model_loaded

    @model_loaded.setter
    def model_loaded(self, value):
        self._model_loaded = value

    @property
    def model_path(self):
        return self._model_path

    @model_path.setter
    def model_path(self, value):
        self._model_path = value

    @property
    def data_writing(self):
        return self._data_writing

    @data_writing.setter
    def data_writing(self, value):
        self._data_writing = value


def reset_and_increment() -> bool:
    """在Plant Simulation中执行SimTalk，启用重置时递增变量功能"""
    # 获取Plant Simulation状态实例（避免循环导入）
    from .plant_simulator01 import PlantSimState

    state = PlantSimState.get_instance()

    if not state.plant_sim:
        print("⚠️ Plant Simulation未初始化，无法执行重置递增操作")
        return False

    try:
        # SimTalk代码：启用事件控制器重置时递增随机数变量
        # 可根据实际需要调整变量名称和控制器路径
        simtalk_code = [
            f".模型.模型.事件控制器.IncrementRandomNumbersVariantOnReset := True;",
        ]
        state.plant_sim.ExecuteSimTalk("\n".join(simtalk_code))
        print("✅ 已启用重置时变量递增功能")
    except Exception as e:
        print(f"❌ 执行重置递增SimTalk失败: {str(e)}")
    return True


def init_plant_sim_instance(model_file: str = MODEL_FILE) -> bool:
    """初始化Plant Simulation实例并加载模型"""
    state = PlantSimState.get_instance()

    if state.plant_sim is not None and state.model_loaded:
        print("✅ Plant Simulation已启动，模型已加载，无需重复初始化")
        try:
            app = state.plant_sim.Application
            app.Visible = True
            app.WindowState = 1  # 最大化窗口
        except Exception as e:
            print(f"⚠️ 激活窗口失败: {str(e)}")
        return True

    try:
        pythoncom.CoInitialize()
        print("✅ COM环境初始化成功")

        # 尝试连接或启动Plant Simulation
        state.plant_sim = None
        plant_sim_app = None
        versions = [
            "Tecnomatix.PlantSimulation.RemoteControl.2404",
            "Tecnomatix.PlantSimulation.RemoteControl",
            "PlantSimulation.RemoteControl",
        ]

        # 尝试不同版本的RemoteControl
        for prog_id in versions:
            try:
                print(f"尝试连接 Plant Simulation: {prog_id}")
                state.plant_sim = win32com.client.Dispatch(prog_id)
                print(f"✅ 成功连接 Plant Simulation: {prog_id}")
                break
            except Exception as e:
                print(f"连接失败 {prog_id}: {str(e)}")

        # 如果RemoteControl连接失败，尝试通过Application启动
        if state.plant_sim is None:
            print("尝试通过COM应用程序启动Plant Simulation...")
            try:
                plant_sim_app = win32com.client.Dispatch(
                    "Tecnomatix.PlantSimulation.Application"
                )
                plant_sim_app.Visible = True
                state.plant_sim = plant_sim_app.RemoteControl
                print("✅ 成功通过COM应用程序启动Plant Simulation")
            except Exception as e:
                print(f"通过COM应用程序启动失败: {str(e)}")
                print("❌ 无法连接任何Plant Simulation版本，请尝试以下解决方案：")
                print("1. 确保Plant Simulation 2404已正确安装")
                print("2. 以管理员身份运行此脚本")
                print("3. 检查Plant Simulation的COM设置")
                return False

        # 验证RemoteControl实例有效性
        if not state.plant_sim:
            print("❌ 未获取到有效的RemoteControl实例")
            return False

        # 加载模型
        state.plant_sim.loadModel(model_file)
        state.model_path = model_file
        state.model_loaded = True
        print(f"✅ 模型已加载：{model_file}")

        # 启动Plant Simulation并打开模型
        found = False
        for path in PLANT_SIM_PATHS:
            if os.path.exists(path):
                try:
                    subprocess.Popen([path, SAVED_MODEL_FILE])
                    print(f"✅ 已启动 Plant Simulation 并打开模型: {path}")
                    found = True
                    break
                except Exception as e:
                    print(f"⚠️ 无法启动 {path}: {str(e)}")

        if not found:
            print("⚠️ 未找到 Plant Simulation 可执行文件")
            print(f"请手动打开模型文件: {SAVED_MODEL_FILE}")

        return True

    except Exception as e:
        print(f"❌ Plant Simulation初始化失败: {str(e)}")
        import traceback

        traceback.print_exc()
        pythoncom.CoUninitialize()
        return False


def add_production_line() -> bool:
    """动态添加生产线结构"""
    state = PlantSimState.get_instance()

    if not state.model_loaded:
        print("❌ 模型未加载，无法添加生产线")
        return False

    try:
        file_path = DEFAULT_PRODUCTION_LINE_FILE
        # 读取生产线配置文件
        with open(file_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        # 生成并执行SimTalk代码
        line_setup, data_writing = json_to_simtalk(json_data)
        state.plant_sim.ExecuteSimTalk(line_setup)
        state.data_writing = data_writing
        print("✅ 已动态添加生产线结构")
        return True
    except Exception as e:
        print(f"❌ 添加生产线失败: {str(e)}")
        return False


def modify_buffer_capacity(buffer_solution: Dict[str, int]) -> bool:
    """动态修改模型中的缓冲区容量"""
    state = PlantSimState.get_instance()

    if not state.model_loaded:
        print("❌ 模型未加载，无法修改缓冲区容量")
        return False

    try:
        # 构造缓冲区配置数据
        buffer_nodes = [
            {"name": buf_name, "type": "缓冲区", "data": {"capacity": capacity}}
            for buf_name, capacity in buffer_solution.items()
        ]

        json_data = {"nodes": buffer_nodes, "edges": []}  # 无需边信息

        # 生成并执行SimTalk代码
        model_setup, data_writing = capacity_json_to_simtalk(json_data)
        state.plant_sim.ExecuteSimTalk(model_setup)
        state.data_writing = data_writing
        print(f"✅ 已动态修改缓冲区容量：{buffer_solution}")

        # 保存模型
        state.plant_sim.SaveModel(SAVED_MODEL_FILE)
        print(f"✅ 模型已成功保存至：{SAVED_MODEL_FILE}")
        return True
    except Exception as e:
        print(f"❌ 修改缓冲区容量失败: {str(e)}")
        return False


def reset_simulation_results() -> bool:
    """重置仿真结果（清除上一次的统计数据）"""
    state = PlantSimState.get_instance()

    if not state.model_loaded:
        return False

    try:
        reset_code = ".模型.模型.事件控制器.reset;"
        state.plant_sim.ExecuteSimTalk(reset_code)
        print("✅ 已重置上一次仿真结果")
        return True
    except Exception as e:
        print(f"❌ 重置仿真结果失败: {str(e)}")
        return False


def run_simulation(end_time: str = "2592000") -> bool:
    """运行仿真并等待数据写入完成"""
    state = PlantSimState.get_instance()

    if not state.model_loaded:
        return False

    try:
        # 执行仿真
        simtalk_code = [
            f".模型.模型.事件控制器.end := {end_time};",
            ".模型.模型.事件控制器.startwithoutanimation;",
        ]
        state.plant_sim.ExecuteSimTalk("\n".join(simtalk_code))
        print(f"⏳ 正在运行仿真...")

        # 等待仿真完成并写入数据
        time.sleep(1)
        print("⏳ 正在写入仿真数据...")
        state.plant_sim.ExecuteSimTalk(state.data_writing)

        # 等待数据文件生成
        max_wait = 30
        wait_count = 0
        while wait_count < max_wait:
            if (
                os.path.exists(DATA_OUTPUT_FILE)
                and os.path.getsize(DATA_OUTPUT_FILE) > 0
            ):
                print("✅ 数据文件写入完成")
                break
            time.sleep(1)
            wait_count += 1
        else:
            print("⚠️ 数据文件写入超时，可能导致读取失败")

        # 保存模型
        state.plant_sim.SaveModel(SAVED_MODEL_FILE)
        print(f"✅ 模型已成功保存至：{SAVED_MODEL_FILE}")
        print("✅ 仿真完成")
        return True
    except Exception as e:
        print(f"❌ 仿真运行失败: {str(e)}")
        return False


def get_simulation_results() -> Tuple[bool, int]:
    """获取当前仿真结果（30天总吞吐量）"""
    state = PlantSimState.get_instance()

    if not state.model_loaded:
        return False, 0

    try:
        total_30d_throughput = None
        max_attempts = 5
        attempt = 0
        target_total_30d = 29000

        # 多次尝试读取数据文件
        while attempt < max_attempts and total_30d_throughput is None:
            if not os.path.exists(DATA_OUTPUT_FILE):
                print(
                    f"⚠️ 数据文件不存在，等待1秒后重试（{attempt + 1}/{max_attempts}）"
                )
                time.sleep(1)
                attempt += 1
                continue

            # 检查文件是否写完
            file_size = os.path.getsize(DATA_OUTPUT_FILE)
            time.sleep(0.5)
            if os.path.getsize(DATA_OUTPUT_FILE) != file_size:
                print(
                    f"⚠️ 数据文件正在写入，等待1秒后重试（{attempt + 1}/{max_attempts}）"
                )
                attempt += 1
                continue

            # 读取并解析文件
            try:
                with open(DATA_OUTPUT_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                print(
                    f"⚠️ 数据文件编码错误（非utf-8），重试（{attempt + 1}/{max_attempts}）"
                )
                attempt += 1
                continue

            if not content:
                print(f"⚠️ 数据文件为空，重试（{attempt + 1}/{max_attempts}）")
                attempt += 1
                continue

            # 提取总吞吐量
            with open(DATA_OUTPUT_FILE, encoding="utf_8_sig") as fp:
                for line in fp:
                    match = re.search(r"总吞吐量\s*(\d+)", line, re.IGNORECASE)
                    if match:
                        total_30d_throughput = int(match.group(1))
                        break
                else:
                    print(f"⚠️ 未找到总吞吐量，重试（{attempt + 1}/{max_attempts}）")
                    attempt += 1
                    time.sleep(1)

        # 验证结果是否达标
        is_qualified = (
            total_30d_throughput >= target_total_30d if total_30d_throughput else False
        )
        print(
            f"📊 仿真结果：30天总吞吐量={total_30d_throughput or 0:.0f}件（目标≥{target_total_30d:.0f}件），是否达标：{is_qualified}"
        )
        return is_qualified, total_30d_throughput or 0

    except Exception as e:
        print(f"❌ 获取仿真结果失败: {str(e)}")
        return False, 0


def create_plant_simulation_model(
    buffer_solution: Dict[str, int],
    end_time: str = "2592000",  # 30天的秒数
) -> Tuple[bool, int]:
    """对外统一接口：单次迭代的仿真流程"""
    if not reset_simulation_results():
        return False, 0

    time.sleep(1)

    if not modify_buffer_capacity(buffer_solution):
        return False, 0

    if not run_simulation(end_time):
        return False, 0

    return get_simulation_results()
