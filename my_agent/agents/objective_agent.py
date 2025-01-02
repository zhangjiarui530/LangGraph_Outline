from typing import Dict, Any, List
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
from my_agent.utils.types import AgentState
import json

def design_objectives(content: str, total_hours: int) -> Dict[str, Any]:
    """设计教学目标"""
    try:
        # 验证输入
        if not content:
            raise ValueError("内容为空")
            
        if not isinstance(total_hours, (int, float)) or total_hours <= 0:
            raise ValueError(f"总课时格式错误: {total_hours}")
            
        # 获取LLM配置
        llm_config = get_llm()
        
        # 构建提示词
        prompt = f"""作为教学设计专家，请基于以下内容设计教学目标。总课时为{total_hours}学时。

内容概要：
{content[:2000]}  # 限制内容长度，避免token超限

请设计以下几个方面的教学目标：
1. 知识目标：学生应该掌握的具体知识点
2. 能力目标：学生应该培养的能力
3. 素养目标：学生应该形成的素养

请按以下格式输出：
{{
    "teaching_objectives": {{
        "知识": ["目标1", "目标2", ...],
        "能力": ["目标1", "目标2", ...],
        "素养": ["目标1", "目标2", ...]
    }}
}}"""

        print("\n=== 生成教学目标 ===")
        print(f"内容长度: {len(content)}")
        print("调用LLM生成目标...")
        
        # 调用LLM
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": "你是一个专业的教学设计专家，擅长设计教学目标。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        # 解析响应
        result = response.choices[0].message.content
        if not isinstance(result, dict):
            import json
            result = json.loads(result)
            
        # 验证结果
        if not isinstance(result, dict):
            raise ValueError(f"结果格式错误: {type(result)}")
            
        if "teaching_objectives" not in result:
            raise ValueError("缺少teaching_objectives字段")
            
        objectives = result["teaching_objectives"]
        if not isinstance(objectives, dict):
            raise ValueError(f"teaching_objectives格式错误: {type(objectives)}")
            
        for key in ["知识", "能力", "素养"]:
            if key not in objectives:
                raise ValueError(f"缺少{key}目标")
            if not isinstance(objectives[key], list):
                raise ValueError(f"{key}目标必须是列表")
            if not objectives[key]:
                raise ValueError(f"{key}目标不能为空")
                
        print("目标生成完成")
        return result
        
    except Exception as e:
        print(f"错误：设计教学目标失败 - {str(e)}")
        raise ValueError(f"设计教学目标失败: {str(e)}")

def validate_objectives(objectives: Dict[str, Any]) -> None:
    """
    验证教学目标的格式和内容
    
    Args:
        objectives: 教学目标字典
        
    Raises:
        ValueError: 如果格式或内容不符合要求
    """
    # 检查基本结构
    if not isinstance(objectives, dict):
        raise ValueError("教学目标必须是字典类型")
        
    if "teaching_objectives" not in objectives:
        raise ValueError("缺少teaching_objectives字段")
        
    if "teaching_suggestions" not in objectives:
        raise ValueError("缺少teaching_suggestions字段")
        
    # 检查教学目标
    obj = objectives["teaching_objectives"]
    for key in ["knowledge", "ability", "quality"]:
        if key not in obj:
            raise ValueError(f"教学目标缺少{key}字段")
        if not isinstance(obj[key], list):
            raise ValueError(f"{key}必须是列表类型")
        if not obj[key]:
            raise ValueError(f"{key}不能为空")
            
    # 检查教学建议
    sug = objectives["teaching_suggestions"]
    for key in ["key_points", "strategies", "time_allocation"]:
        if key not in sug:
            raise ValueError(f"教学建议缺少{key}字段")
        if not isinstance(sug[key], str):
            raise ValueError(f"{key}必须是字符串类型")
        if not sug[key].strip():
            raise ValueError(f"{key}不能为空") 

def generate_objectives(textbook_content: Dict[str, Any]) -> Dict[str, Any]:
    """生成教学目标"""
    try:
        # 验证输入
        if not isinstance(textbook_content, dict):
            raise ValueError(f"教材内容格式错误: {type(textbook_content)}")
            
        # 获取LLM配置
        llm_config = get_llm()
        
        # 构建提示词
        content_json = json.dumps(textbook_content, indent=2, ensure_ascii=False)
        template = """作为教学目标设计专家，请基于以下教材内容生成教学目标。

教材内容：
{content}

请生成教学目标，要求：
1. 目标要具体、可测量、可实现
2. 包含知识目标、能力目标和情感目标三个维度
3. 每个维度的目标要有层次性，从低到高
4. 目标要与教材内容紧密相关

请按以下格式输出：
{{
    "objectives": {{
        "knowledge": [
            {{
                "level": "记忆/理解/应用/分析/评价/创造",
                "description": "目标描述",
                "evaluation": "达成标准"
            }}
        ],
        "ability": [
            {{
                "level": "模仿/操作/熟练/创新",
                "description": "目标描述",
                "evaluation": "达成标准"
            }}
        ],
        "emotion": [
            {{
                "level": "感知/响应/形成/内化",
                "description": "目标描述",
                "evaluation": "达成标准"
            }}
        ]
    }}
}}"""

        prompt = template.format(content=content_json)

        print("\n=== 生成教学目标 ===")
        print("调用LLM生成目标...")
        
        # 调用LLM
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": "你是一个专业的教学目标设计专家，擅长设计教学目标。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        # 解析响应
        result = response.choices[0].message.content
        if isinstance(result, str):
            result = json.loads(result)
            
        # 验证结果
        if not isinstance(result, dict):
            raise ValueError(f"结果格式错误: {type(result)}")
            
        if "objectives" not in result:
            raise ValueError("缺少objectives字段")
            
        objectives = result["objectives"]
        if not isinstance(objectives, dict):
            raise ValueError(f"objectives格式错误: {type(objectives)}")
            
        required_fields = ["knowledge", "ability", "emotion"]
        for field in required_fields:
            if field not in objectives:
                raise ValueError(f"缺少{field}目标")
            if not isinstance(objectives[field], list):
                raise ValueError(f"{field}目标格式错误")
            if not objectives[field]:
                raise ValueError(f"{field}目标不能为空")
                
        # 验证每个目标的格式
        for field in required_fields:
            for obj in objectives[field]:
                if not isinstance(obj, dict):
                    raise ValueError(f"{field}目标项格式错误")
                for key in ["level", "description", "evaluation"]:
                    if key not in obj:
                        raise ValueError(f"{field}目标缺少{key}字段")
                    if not isinstance(obj[key], str):
                        raise ValueError(f"{field}目标的{key}字段必须是字符串")
                        
        print("目标生成完成")
        return result
        
    except Exception as e:
        print(f"错误：生成教学目标失败 - {str(e)}")
        raise LLMGenerationError(f"生成教学目标失败: {str(e)}") 