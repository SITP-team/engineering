"""LLM主导的输入标准化处理模块（简化版）"""

from typing import Optional
import requests
from ..utils.api_utils import make_api_request

SYSTEM_PROMPT = """你是一个工业建模语言标准化专家，请将用户输入转换为标准化的建模语言描述。
主要任务：
1. 术语标准化：使用标准工业术语(工位、加工时间等)
2. 消除模糊表述：将"快速"、"大量"等转换为具体数值
3. 输出的是一段简介规范的自然语言描述

输出要求：
- 直接返回标准化后的文本（不要JSON格式）
- 使用plant simulation中的术语
- 消除所有模糊表述,但不要擅自增加新的信息，要询问用户，直到信息完整
- 保持原始语义不变
- 要在每个属性之后说明所选分布或者是标明没有分布
- 逐步推理给出答案，输出你的思考过程

示例输入：我想让你帮我建一个缸盖生产线的模型。整个流程是这样的：最开始有个放缸盖毛坯的地方，它从0分钟开始干活，每隔10分钟就放出来一个毛坯，这样一直干满一整天。毛坯出来之后呢，会先到一个地方排队等着加工，这个地方不大，最多能堆8个毛坯。等排到了，就送去铣床加工那个关键的缸盖面。这台铣床干活的速度按正态分布来，平均要弄200秒左右，但有时快点有时慢点，大概差个30秒上下。它还有个爱坏的毛病，平均干个2000秒左右就会随机坏一次，一坏就得停下来修，平均修200秒才能好。铣床前面也有个小地方让加工完的缸盖稍微等等再走，也是最多能放8个。铣好的缸盖接下来要运去做检测，用的是条传送带，差不多2米长，半米宽，跑的速度是1米每秒，一次最多能运2个缸盖。运到了就开始做气密性测试，看缸盖漏不漏气，这个测试挺快，每个缸盖固定就卡1分钟。不过这个测试设备更不让人省心，它坏的时间间隔完全是按负指数分布随机来的，平均大概2000秒就坏一次，而且每次修多久也是按负指数分布随机的，平均得修200秒。测完结果就得分路了：大概七成（70%）的缸盖是合格的，是好产品，就直接送到存放好缸盖的仓库里；剩下三成（30%）是不合格的废品，就送到专门堆放废料的地方去。整个线就这么个顺序走下来：从出毛坯开始，经过第一个排队点，再到铣床加工，然后上传送带运去测试，最后测试完根据好坏分到好仓库或者废料堆。你就按我上面说的这些干活时间、机器爱坏的毛病、地方的大小、传送带的尺寸速度、还有合格率这些细节，把模型设定好跑起来看看。
示例输出：（此处为你的思考过程）为我生成一个有向图，节点包括源（源），缓冲区，加工工位（工位），传送器（传送器），测试工位（工位），合格库存（物料终结）和废品库存（物料终结），源，加工工位，缓冲区，传送器，测试工位依次为串联结构，测试工位分别连接合格库存与废品库存，源的时间间隔为10分钟，起始时间为0，结束时间为1天，缓冲区容量为8，传送器长度为2米，宽度为0.5米，速度为1m/s，容量为2，加工工位处理时间为正态分布平均值200，标准差30，故障间隔（没有分布）为2000，持续时间（没有分布）为200，缓冲区容量为8，测试工位的处理时间（没有分布）为1分钟，故障间隔时间为负指数分布，均值为2000，持续时间为负指数分布，均值为200，测试结果为合格率是70%，合格的产品输入合格库存，不合格的产品输入废品库存。
"""


def standardize_text(raw_text: str, max_attempts: int = 3) -> Optional[str]:
    """
    LLM主导的标准化处理主函数(交互式)
    参数:
        raw_text: 原始输入文本
        max_attempts: 最大交互次数
    返回:
        - 标准化后的字符串文本
        - 处理失败时返回None
    """
    if not raw_text or not isinstance(raw_text, str):
        return None

    # 初始化对话历史
    conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]
    current_text = raw_text
    attempts = 0

    while attempts < max_attempts:
        # 构建当前消息：系统提示 + 历史对话 + 最新输入
        messages = conversation_history.copy()
        messages.append({"role": "user", "content": current_text})

        try:
            response = make_api_request(messages)
            if not response.get("choices"):
                print(f"API响应格式异常: {response}")
                return None

            result = response["choices"][0]["message"]["content"]

            # 检查是否为真正的信息缺失询问（而不是AI的思考过程）
            # 更精确的检测逻辑：检查是否包含明确的询问句式，而不是简单的关键词
            check_phrases = [
                "需要补充",
                "缺失",
                "请提供",
                "请说明",
                "需要说明",
                "缺少",
                "不完整",
                "请详细描述",
            ]

            # 排除思考过程中的描述性关键词
            exclude_phrases = [
                "思考过程",
                "标准化输出",
                "示例输出",
                "流程顺序为",
                "术语标准化",
                "消除模糊表述",
                "检查信息完整性",
            ]

            # 检测是否为真正的询问：包含询问关键词但不包含思考过程描述
            has_inquiry = any(phrase in result for phrase in check_phrases)
            is_thought_process = (
                any(phrase in result for phrase in exclude_phrases)
                or "### 思考过程：" in result
            )

            # 只有当包含询问关键词且不是思考过程时才要求补充信息
            if has_inquiry and not is_thought_process:
                print("标准化过程需要补充信息:")
                print(result)
                # 记录完整对话到上下文
                conversation_history.append({"role": "user", "content": current_text})
                conversation_history.append({"role": "assistant", "content": result})

                print(f"\n=== 需要补充信息 (尝试 {attempts + 1}/{max_attempts}) ===")
                print(result)
                current_text = input("请输入补充内容: ")
                attempts += 1
                continue

            return result
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {type(e).__name__} - {str(e)}")
            return None
        except KeyError as e:
            print(f"API响应解析失败: 缺少关键字段 {e}")
            return None
        except Exception as e:
            print(f"未知错误: {type(e).__name__} - {str(e)}")
            return None


# 测试示例
if __name__ == "__main__":
    test_input = "我想让你帮我建一个缸盖生产线的模型。整个流程是这样的：最开始有个放缸盖毛坯的地方，它从0分钟开始干活，每隔10分钟就放出来一个毛坯，这样一直干满一整天。毛坯出来之后呢，会先到一个地方排队等着加工，这个地方不大，最多能堆8个毛坯。等排到了，就送去铣床加工那个关键的缸盖面。这台铣床干活的速度按正态分布来，平均要弄200秒左右，但有时快点有时慢点，大概差个30秒上下。它还有个爱坏的毛病，平均干个2000秒左右就会随机坏一次，一坏就得停下来修，平均修200秒才能好。铣床前面也有个小地方让加工完的缸盖稍微等等再走，也是最多能放8个。铣好的缸盖接下来要运去做检测，用的是条传送带，差不多2米长，半米宽，跑的速度是1米每秒，一次最多能运2个缸盖。运到了就开始做气密性测试，看缸盖漏不漏气，这个测试挺快，每个缸盖固定就卡1分钟。不过这个测试设备更不让人省心，它坏的时间间隔完全是按负指数分布随机来的，平均大概2000秒就坏一次，而且每次修多久也是按负指数分布随机的，平均得修200秒。测完结果就得分路了：大概七成（70%）的缸盖是合格的，是好产品，就直接送到存放好缸盖的仓库里；剩下三成（30%）是不合格的废品，就送到专门堆放废料的地方去。整个线就这么个顺序走下来：从出毛坯开始，经过第一个排队点，再到铣床加工，然后上传送带运去测试，最后测试完根据好坏分到好仓库或者废料堆。你就按我上面说的这些干活时间、机器爱坏的毛病、地方的大小、传送带的尺寸速度、还有合格率这些细节，把模型设定好跑起来看看。"
    result = standardize_text(test_input)
    print(result)
