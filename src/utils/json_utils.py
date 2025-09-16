#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re


def extract_json_from_response(response_text):
    """从API响应中提取纯JSON内容，处理AI思考过程混入的情况"""

    # 1. 首先尝试提取被```json ... ```包裹的内容
    json_match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # 2. 尝试提取被```包裹的内容
    code_match = re.search(r"```(.*?)```", response_text, re.DOTALL)
    if code_match:
        try:
            return json.loads(code_match.group(1))
        except json.JSONDecodeError:
            pass

    # 3. 尝试查找JSON对象（处理AI思考过程混入的情况）
    # 使用更精确的正则表达式匹配JSON对象
    json_pattern = r"(\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\})"
    json_matches = re.findall(json_pattern, response_text, re.DOTALL)

    # 优先选择最长的JSON匹配（通常是最完整的）
    if json_matches:
        # 按长度排序，选择最长的匹配
        json_matches.sort(key=len, reverse=True)
        for json_str in json_matches:
            # 清理可能的思考过程混入
            cleaned_json = _clean_json_string(json_str)
            try:
                parsed_data = json.loads(cleaned_json)
                # 检查是否包含必要的结构
                if isinstance(parsed_data, dict) and (
                    "nodes" in parsed_data or "edges" in parsed_data
                ):
                    return parsed_data
            except json.JSONDecodeError:
                continue

    # 4. 尝试查找被标记为JSON代码块的内容
    json_code_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
    json_code_matches = re.findall(json_code_pattern, response_text, re.DOTALL)
    for json_str in json_code_matches:
        try:
            parsed_data = json.loads(json_str)
            if isinstance(parsed_data, dict):
                return parsed_data
        except json.JSONDecodeError:
            continue

    # 5. 尝试移除可能的前缀后解析
    # 处理"AI完整响应:"等前缀情况
    cleaned_response = response_text.strip()
    if cleaned_response.startswith("AI完整响应:"):
        cleaned_response = cleaned_response.replace("AI完整响应:", "", 1).strip()
    elif cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response.replace("```json", "", 1).strip()
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3].strip()

    try:
        return json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {str(e)}")
        print("原始响应内容前500字符:")
        print(
            response_text[:500] + "..." if len(response_text) > 500 else response_text
        )
        return None


def _clean_json_string(json_str):
    """清理JSON字符串，修复AI思考过程混入的问题"""
    # 修复未终止的字符串
    lines = json_str.split("\n")
    cleaned_lines = []

    for line in lines:
        # 检查是否有未终止的字符串（包含中文但缺少引号）
        if ":" in line and '"' not in line and ":" in line.split(":")[1]:
            parts = line.split(":", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()

                # 如果值看起来像时间格式但被思考过程污染
                if re.match(r"^\d+:", value) and "：" in value:
                    # 提取时间部分（直到第一个中文字符）
                    time_match = re.match(r"^(\d+:\d+:\d+:\d+)", value)
                    if time_match:
                        cleaned_value = f'"{time_match.group(1)}"'
                        line = f'"{key}": {cleaned_value}'

        cleaned_lines.append(line)

    cleaned_json = "\n".join(cleaned_lines)

    # 修复常见的JSON格式问题
    cleaned_json = re.sub(
        r"([{,]\s*)(\w+)(\s*:)", r'\1"\2"\3', cleaned_json
    )  # 未引用的键
    cleaned_json = re.sub(
        r':\s*([^"\[\]{},\d][^,}\]\s]*)', r': "\1"', cleaned_json
    )  # 未引号的字符串值

    return cleaned_json
