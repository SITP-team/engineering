#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ..utils.time_utils import format_time_value


def build_model(json_data):
    """
    模型建立部分：实体创建、属性设置、连接、事件控制
    """
    nodes = json_data.get("nodes", [])
    edges = json_data.get("edges", [])

    model_setup = []
    x_pos = 50  # 初始x坐标
    y_pos = 200  # 统一y坐标
    material_end_y = 200  # 物料终结节点y坐标起始值
    conveyer_y = 250  # 传送器y坐标起始值

    # 提取源节点的时间属性（用于故障设置）
    source_start_time = "0:0:0:0"
    source_stop_time = "8:0:0:0"
    for node in nodes:
        if node["type"] == "源" and "data" in node and "time" in node["data"]:
            time_data = node["data"]["time"]
            if "start_time" in time_data:
                source_start_time = time_data["start_time"]
            if "stop_time" in time_data:
                source_stop_time = time_data["stop_time"]
            break

    # 1. 创建实体（按节点顺序）
    for node in nodes:
        node_type = node["type"]
        node_name = node["name"]
        if node_type == "源":
            model_setup.append(
                f'.物料流.源.createObject(.模型.模型, {x_pos}, {y_pos}, "{node_name}")'
            )
        elif node_type == "工位":
            model_setup.append(
                f'.物料流.工位.createObject(.模型.模型, {x_pos}, {y_pos}, "{node_name}")'
            )
        elif node_type == "缓冲区":
            model_setup.append(
                f'.物料流.缓冲区.createObject(.模型.模型, {x_pos}, {y_pos}, "{node_name}")'
            )
        elif node_type == "传送器":
            model_setup.append(
                f'.物料流.传送器.createObject(.模型.模型, {x_pos}, {conveyer_y}, "{node_name}")'
            )
            conveyer_y += 50  # 传送器节点y坐标递增
        elif node_type == "物料终结":
            model_setup.append(
                f'.物料流.物料终结.createObject(.模型.模型, 300, {material_end_y}, "{node_name}")'
            )
            material_end_y += 50  # 物料终结节点y坐标递增
        x_pos += 50  # 每个实体x坐标递增

    model_setup.append("")  # 空行分隔

    # 2. 设置实体属性
    for node in nodes:
        node_name = node["name"]
        node_type = node["type"]
        data = node.get("data", {})

        if node_type == "源" and "time" in data:
            time_data = data["time"]
            for time_type in ["interval_time", "start_time", "stop_time"]:
                if time_type in time_data:
                    time_value = time_data[time_type]
                    simtalk_property = time_type.replace("_time", "")

                    if (
                        isinstance(time_value, dict)
                        and "distribution_pattern" in time_value
                    ):
                        formatted_value = format_time_value(time_value)
                        model_setup.append(
                            f".模型.模型.{node_name}.{simtalk_property}.setParam({formatted_value})"
                        )
                    else:
                        model_setup.append(
                            f".模型.模型.{node_name}.{simtalk_property} := {time_value}"
                        )

        elif node_type == "工位":
            if "time" in data and "processing_time" in data["time"]:
                proc_time = data["time"]["processing_time"]
                if isinstance(proc_time, dict) and "distribution_pattern" in proc_time:
                    formatted_value = format_time_value(proc_time)
                    model_setup.append(
                        f".模型.模型.{node_name}.ProcTime.setParam({formatted_value})"
                    )
                else:
                    model_setup.append(
                        f".模型.模型.{node_name}.ProcTime := {proc_time}"
                    )

            if "failure" in data:
                failure_data = data["failure"]
                failure_name = failure_data.get("failure_name", "default_failure")
                failure_start = failure_data.get("start_time", source_start_time)
                failure_stop = failure_data.get("stop_time", source_stop_time)

                interval_time = failure_data.get("interval_time")
                if (
                    isinstance(interval_time, dict)
                    and "distribution_pattern" in interval_time
                ):
                    formatted = format_time_value(interval_time)
                    cleaned = formatted.replace('"', "")
                    interval_str = f'"{cleaned}"'
                else:
                    interval_str = str(interval_time)

                duration_time = failure_data.get("duration_time", "0:0:0:0")
                if (
                    isinstance(duration_time, dict)
                    and "distribution_pattern" in duration_time
                ):
                    formatted = format_time_value(duration_time)
                    cleaned = formatted.replace('"', "")
                    duration_str = f'"{cleaned}"'
                else:
                    duration_str = str(duration_time)

                model_setup.append(
                    f'.模型.模型.{node_name}.Failures.createFailure("{failure_name}", {interval_str}, {duration_str}, "SimulationTime", {failure_start}, {failure_stop}, false)'
                )
                model_setup.append(
                    f".模型.模型.{node_name}.Failures.{failure_name}.Active := true"
                )

            if "production_status" in data:
                qualified = int(data["production_status"]["qualified"] * 100)
                unqualified = int(data["production_status"]["unqualified"] * 100)
                model_setup.append(
                    f".模型.模型.{node_name}.exitstrategyblocking := true"
                )
                model_setup.append(
                    f'.模型.模型.{node_name}.exitstrategy := "percentage"'
                )
                model_setup.append(
                    f".模型.模型.{node_name}.exitstrategypercentagevalues := [{qualified}, {unqualified}]"
                )

        elif node_type == "缓冲区" and "capacity" in data:
            model_setup.append(f'.模型.模型.{node_name}.capacity := {data["capacity"]}')

        elif node_type == "传送器":
            if "capacity" in data:
                model_setup.append(
                    f'.模型.模型.{node_name}.capacity := {data["capacity"]}'
                )
            if "length" in data:
                model_setup.append(
                    f'.模型.模型.{node_name}.length := {data["length"]}m'
                )
            if "width" in data:
                model_setup.append(f'.模型.模型.{node_name}.width := {data["width"]}m')
            if "speed" in data:
                model_setup.append(f'.模型.模型.{node_name}.speed := {data["speed"]}')

        elif node_type == "物料终结":
            if "time" in data and "processing_time" in data["time"]:
                proc_time = data["time"]["processing_time"]
                if isinstance(proc_time, dict) and "distribution_pattern" in proc_time:
                    formatted_value = format_time_value(proc_time)
                    model_setup.append(
                        f".模型.模型.{node_name}.ProcTime.setParam({formatted_value})"
                    )
                else:
                    model_setup.append(
                        f".模型.模型.{node_name}.ProcTime := {proc_time}"
                    )

            if "failure" in data:
                failure_data = data["failure"]
                failure_name = failure_data.get("failure_name", "default_failure")
                failure_start = failure_data.get("start_time", source_start_time)
                failure_stop = failure_data.get("stop_time", source_stop_time)
                interval_time = failure_data.get("interval_time")
                if (
                    isinstance(interval_time, dict)
                    and "distribution_pattern" in interval_time
                ):
                    formatted = format_time_value(interval_time)
                    cleaned = formatted.replace('"', "")
                    interval_str = f'"{cleaned}"'
                else:
                    interval_str = str(interval_time)
                duration_time = failure_data.get("duration_time", "0:0:0:0")
                if (
                    isinstance(duration_time, dict)
                    and "distribution_pattern" in duration_time
                ):
                    formatted = format_time_value(duration_time)
                    cleaned = formatted.replace('"', "")
                    duration_str = f'"{cleaned}"'
                else:
                    duration_str = str(duration_time)
                model_setup.append(
                    f'.模型.模型.{node_name}.Failures.createFailure("{failure_name}", {interval_str}, {duration_str}, "SimulationTime", {failure_start}, {failure_stop}, false)'
                )
                model_setup.append(
                    f".模型.模型.{node_name}.Failures.{failure_name}.Active := true"
                )

    model_setup.append("")  # 空行分隔

    # 3. 实体连接（使用完整路径）
    for edge in edges:
        from_node = edge["from"]
        to_node = edge["to"]
        model_setup.append(
            f".物料流.连接器.connect(.模型.模型.{from_node}, .模型.模型.{to_node});"
        )

    model_setup.append("")  # 空行分隔

    # 4. 事件控制器设置
    model_setup.append(".模型.模型.事件控制器.start")
    model_setup.append(f".模型.模型.事件控制器.end := {source_stop_time}")
    model_setup.append(".模型.模型.事件控制器.startwithoutanimation")

    return "\n".join(model_setup)
