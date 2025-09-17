# 路径配置文件
import os

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

# 模型模板文件路径
MODEL_FILE = os.path.join(PROJECT_ROOT, "src", "config", "test2.spp")

# 生成的模型保存路径（保存到result目录）
SAVED_MODEL_FILE = os.path.join(PROJECT_ROOT, "src", "result", "saved.spp")

# 数据输出文件路径（保存到result目录）
DATA_OUTPUT_FILE = os.path.join(PROJECT_ROOT, "src", "result", "data_output.txt")

# 默认生产线配置文件路径
DEFAULT_PRODUCTION_LINE_FILE = os.path.join(
    PROJECT_ROOT, "src", "core", "optimization", "default_production_line.json"
)

# 文档文件路径
BACKGROUND_DOCUMENT_FILE = os.path.join(
    PROJECT_ROOT, "src", "docs", "background document.md"
)
SAMPLE_LIBRARY_FILE = os.path.join(PROJECT_ROOT, "src", "docs", "sample library.md")

"""
个人配置文件
集中存放所有与环境相关的配置项，包括：
- 本地软件路径
- API端点配置
- 其他个人敏感信息

此文件不应提交到版本控制(已在.gitignore中配置)
"""

# Plant Simulation可执行文件路径
PLANT_SIM_PATHS = [
    r"D:\Program Files\siemens\Tecnomatix Plant Simulation 15\PlantSimulation.exe",
    r"C:\Program Files\Siemens\Tecnomatix Plant Simulation 2404\PlantSimulation.exe",
    r"C:\Program Files (x86)\Siemens\Tecnomatix Plant Simulation 2404\PlantSimulation.exe",
]

# API配置
API_URL = "https://api.deepseek.com/v1/chat/completions"
API_KEY = "sk-e9974aad1f594c65a14cca3b48c8dea2"  # DeepSeek API密钥
