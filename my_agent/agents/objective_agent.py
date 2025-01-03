from typing import Dict, Any, List, Optional
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

def generate_objectives(content: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """生成教学目标"""
    try:
        # 获取LLM配置
        llm_config = get_llm()
        
        # 构建提示词
        if content:
            content_json = json.dumps(content, indent=2, ensure_ascii=False)
            template = """作为一名资深的语文教师，请基于以下教材内容生成教学目标。

教材内容：
{content}

请设计完整的教学目标，要求：
1. 目标要全面覆盖教材内容
2. 目标要分为三个维度：
   - 知识与技能目标
   - 过程与方法目标
   - 情感态度与价值观目标
3. 每个目标要：
   - 具体明确
   - 可测量
   - 可达成
   - 符合实际
   - 有时间限制
4. 目标设计要：
   - 符合语文学科特点
   - 体现核心素养
   - 注重能力培养
   - 关注学生发展
   - 突出应用实践
   - 重视情感熏陶

请按以下格式输出：
{{
    "objectives": {{
        "knowledge_skill": [
            {{
                "content": "目标内容",
                "importance": "重要程度",
                "evaluation_criteria": ["评价标准1", "评价标准2"]
            }}
        ],
        "process_method": [
            {{
                "content": "目标内容",
                "importance": "重要程度",
                "evaluation_criteria": ["评价标准1", "评价标准2"]
            }}
        ],
        "emotion_attitude": [
            {{
                "content": "目标内容",
                "importance": "重要程度",
                "evaluation_criteria": ["评价标准1", "评价标准2"]
            }}
        ]
    }},
    "core_literacy": [
        {{
            "name": "素养名称",
            "description": "具体描述",
            "related_objectives": ["相关目标1", "相关目标2"]
        }}
    ]
}}"""
        else:
            template = """作为一名资深的语文教师，请设计一个单元的教学目标。

请设计完整的教学目标，要求：
1. 目标要分为三个维度：
   - 知识与技能目标
   - 过程与方法目标
   - 情感态度与价值观目标
2. 每个目标要：
   - 具体明确
   - 可测量
   - 可达成
   - 符合实际
   - 有时间限制
3. 目标设计要：
   - 符合语文学科特点
   - 体现核心素养
   - 注重能力培养
   - 关注学生发展
   - 突出应用实践
   - 重视情感熏陶

请按以下格式输出：
{{
    "objectives": {{
        "knowledge_skill": [
            {{
                "content": "目标内容",
                "importance": "重要程度",
                "evaluation_criteria": ["评价标准1", "评价标准2"]
            }}
        ],
        "process_method": [
            {{
                "content": "目标内容",
                "importance": "重要程度",
                "evaluation_criteria": ["评价标准1", "评价标准2"]
            }}
        ],
        "emotion_attitude": [
            {{
                "content": "目标内容",
                "importance": "重要程度",
                "evaluation_criteria": ["评价标准1", "评价标准2"]
            }}
        ]
    }},
    "core_literacy": [
        {{
            "name": "素养名称",
            "description": "具体描述",
            "related_objectives": ["相关目标1", "相关目标2"]
        }}
    ]
}}"""

        prompt = template.format(
            content=content_json if content else ""
        )

        print("\n=== 生成教学目标 ===")
        print("调用LLM生成教学目标...")
        
        # 调用LLM
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": "你是一个专业的语文教师，擅长设计教学目标。你的设计要符合新课标要求，体现学科特点。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        # 解析响应
        result = response.choices[0].message.content
        if isinstance(result, str):
            result = json.loads(result)
            
        print("教学目标生成完成")
        return result
        
    except Exception as e:
        print(f"错误：生成教学目标失败 - {str(e)}")
        return {
            "objectives": {
                "knowledge_skill": [],
                "process_method": [],
                "emotion_attitude": []
            },
            "core_literacy": []
        } 
