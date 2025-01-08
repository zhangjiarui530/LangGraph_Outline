from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
import os
from zhipuai import ZhipuAI

if TYPE_CHECKING:
    from my_agent.utils.configuration import Configuration

@dataclass
class LLMConfig:
    """LLM配置"""
    model: str
    client: any
    temperature: float = 0.2
    
def get_llm(config: Optional["Configuration"] = None) -> LLMConfig:
    """
    获取模型配置
    
    Args:
        config: 可选的配置对象，如果不提供则使用默认配置
        
    Returns:
        LLMConfig: 模型配置
    """
    if config is None:
        from my_agent.utils.configuration import Configuration
        config = Configuration()
        
    client = ZhipuAI(api_key=config.api_key)
    
    return LLMConfig(
        model=config.model_name,
        client=client,
        temperature=config.temperature
    )
