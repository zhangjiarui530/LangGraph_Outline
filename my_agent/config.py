from langchain_openai import ChatOpenAI
from zhipuai import ZhipuAI
import os
import json
from dotenv import load_dotenv
from .utils.exceptions import LLMGenerationError

# 加载环境变量
load_dotenv()

# API 配置
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
DEFAULT_TEXT_MODEL = "glm-4-air"  # 文字版PDF使用的模型
DEFAULT_VISION_MODEL = "glm-4v-flash"  # 图片版PDF使用的模型
DEFAULT_TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

def handle_api_error(error_code: str, error_message: str) -> str:
    """处理API错误并返回用户友好的错误信息"""
    error_messages = {
        "1113": "API账户余额不足，请联系管理员充值",
        "1111": "API调用频率超限，请稍后再试",
        "1112": "API服务暂时不可用，请稍后再试",
    }
    return error_messages.get(error_code, f"API调用失败: {error_message}")

# LLM 配置
def get_llm(is_scanned: bool = False, temperature: float = DEFAULT_TEMPERATURE):
    """
    获取LLM客户端
    
    Args:
        is_scanned: 是否为扫描版PDF
        temperature: 温度参数
    """
    if not ZHIPU_API_KEY:
        raise LLMGenerationError("未找到 ZHIPU_API_KEY 环境变量")
        
    # 创建基础客户端
    client = ZhipuAI(api_key=ZHIPU_API_KEY)
    
    # 根据PDF类型选择模型
    model = DEFAULT_VISION_MODEL if is_scanned else DEFAULT_TEXT_MODEL
    
    class ModelWrapper:
        def __init__(self, client, model, temperature):
            self.client = client
            self.model = model
            self.temperature = temperature
            
        def chat(self, messages):
            """调用API进行对话"""
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature
                )
                return response
            except Exception as e:
                # 解析错误信息
                error_text = str(e)
                if "error" in error_text:
                    try:
                        error_data = json.loads(error_text.split("error text ")[-1])
                        error_code = error_data["error"]["code"]
                        error_message = error_data["error"]["message"]
                        friendly_message = handle_api_error(error_code, error_message)
                        raise LLMGenerationError(friendly_message)
                    except json.JSONDecodeError:
                        # 如果JSON解析失败，抛出原始错误
                        raise LLMGenerationError(f"API调用失败: {str(e)}")
                # 如果不是JSON错误，抛出原始错误
                raise LLMGenerationError(f"API调用失败: {str(e)}")
    
    return ModelWrapper(client, model, temperature)