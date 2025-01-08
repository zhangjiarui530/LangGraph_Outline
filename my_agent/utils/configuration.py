from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(kw_only=True)
class Configuration:
    """教学大纲生成器的配置参数"""
    
    # LLM配置
    model_name: str = "glm-4-air"
    temperature: float = 0.2
    api_key: Optional[str] = None
    
    def __post_init__(self):
        """初始化后的处理"""
        # 如果没有提供api_key，从环境变量获取
        if self.api_key is None:
            self.api_key = os.getenv("ZHIPU_API_KEY")
            if not self.api_key:
                raise ValueError("未设置ZHIPU_API_KEY环境变量")
    
    @classmethod
    def from_cli_args(cls, args: list) -> "Configuration":
        """从命令行参数创建配置实例"""
        values = {}
            
        # 使用环境变量覆盖默认值
        env_map = {
            "model_name": "TEACHING_PLAN_MODEL",
            "temperature": "TEACHING_PLAN_TEMPERATURE",
            "api_key": "ZHIPU_API_KEY"
        }
        
        for field, env_key in env_map.items():
            env_value = os.environ.get(env_key)
            if env_value is not None:
                if field in ["temperature"]:
                    values[field] = float(env_value)
                else:
                    values[field] = env_value
                    
        return cls(**values)
    
    def get_llm_config(self) -> dict:
        """获取LLM配置"""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "api_key": self.api_key
        }
    
    def print_config(self) -> None:
        """打印配置信息"""
        print(f"\n=== LLM配置信息 ===")
        print(f"模型：{self.model_name}")
        print(f"温度：{self.temperature}") 