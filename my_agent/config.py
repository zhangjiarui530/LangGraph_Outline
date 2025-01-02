from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class LLMConfig:
    """LLM配置"""
    model: str
    client: any
    temperature: float = 0.7
    
def get_llm() -> LLMConfig:
    """
    获取模型配置
    
    Returns:
        LLMConfig: 模型配置
    """
    from zhipuai import ZhipuAI
    client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))
    
    # 统一使用glm-4-air
    return LLMConfig(
        model="glm-4-air",
        client=client,
        temperature=0.3
    )