from typing import Dict, Any, List, Optional
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
from my_agent.utils.types import AgentState
import json

def analyze_knowledge(content: Optional[Dict[str, Any]], objectives: Dict[str, Any]) -> Dict[str, Any]:
    """分析知识点"""
    try:
        # 获取LLM配置
        llm_config = get_llm()
        
        # 构建提示词
        objectives_json = json.dumps(objectives, indent=2, ensure_ascii=False)
        if content:
            content_json = json.dumps(content, indent=2, ensure_ascii=False)
            template = """作为一名资深的语文教师，请基于以下教材内容和教学目标分析知识点。

教材内容：
{content}

教学目标：
{objectives}

请分析并整理知识点体系，要求：
1. 知识点要完整覆盖教材内容和教学目标
2. 区分基础知识点和拓展知识点
3. 明确标注重点和难点
4. 每个知识点要说明：
   - 具体内容和范围
   - 难度等级（容易/中等/困难）
   - 重要程度（一般/重要/核心）
   - 前置知识要求
   - 对应的教学目标
   - 教学建议
5. 知识点之间要体现内在联系和层次关系
6. 要符合语文学科特点和学生认知规律

请按以下格式输出：
{{
    "knowledge_points": {{
        "basic": [
            {{
                "name": "知识点名称",
                "content": "具体内容",
                "difficulty": "容易/中等/困难",
                "importance": "一般/重要/核心",
                "prerequisites": ["前置知识点1", "前置知识点2"],
                "objectives": ["对应的教学目标1", "对应的教学目标2"],
                "teaching_suggestions": "教学建议"
            }}
        ],
        "advanced": [
            {{
                "name": "知识点名称",
                "content": "具体内容",
                "difficulty": "容易/中等/困难",
                "importance": "一般/重要/核心",
                "prerequisites": ["前置知识点1", "前置知识点2"],
                "objectives": ["对应的教学目标1", "对应的教学目标2"],
                "teaching_suggestions": "教学建议"
            }}
        ],
        "key_points": ["重点1", "重点2"],
        "difficult_points": ["难点1", "难点2"]
    }}
}}"""
        else:
            template = """作为一名资深的语文教师，请基于以下教学目标设计知识点体系。

教学目标：
{objectives}

请设计完整的知识点体系，要求：
1. 知识点要完整覆盖教学目标
2. 区分基础知识点和拓展知识点
3. 明确标注重点和难点
4. 每个知识点要说明：
   - 具体内容和范围
   - 难度等级（容易/中等/困难）
   - 重要程度（一般/重要/核心）
   - 前置知识要求
   - 对应的教学目标
   - 教学建议
5. 知识点之间要体现内在联系和层次关系
6. 要符合语文学科特点和学生认知规律

请按以下格式输出：
{{
    "knowledge_points": {{
        "basic": [
            {{
                "name": "知识点名称",
                "content": "具体内容",
                "difficulty": "容易/中等/困难",
                "importance": "一般/重要/核心",
                "prerequisites": ["前置知识点1", "前置知识点2"],
                "objectives": ["对应的教学目标1", "对应的教学目标2"],
                "teaching_suggestions": "教学建议"
            }}
        ],
        "advanced": [
            {{
                "name": "知识点名称",
                "content": "具体内容",
                "difficulty": "容易/中等/困难",
                "importance": "一般/重要/核心",
                "prerequisites": ["前置知识点1", "前置知识点2"],
                "objectives": ["对应的教学目标1", "对应的教学目标2"],
                "teaching_suggestions": "教学建议"
            }}
        ],
        "key_points": ["重点1", "重点2"],
        "difficult_points": ["难点1", "难点2"]
    }}
}}"""

        prompt = template.format(
            content=content_json if content else "",
            objectives=objectives_json
        )

        print("\n=== 分析知识点 ===")
        print("调用LLM分析知识点...")
        
        # 调用LLM
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": "你是一个专业的语文教师，擅长分析和组织知识点体系。你的分析要符合新课标要求，体现学科特点。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        # 解析响应
        result = response.choices[0].message.content
        if isinstance(result, str):
            result = json.loads(result)
            
        print("知识点分析完成")
        return result
        
    except Exception as e:
        print(f"错误：分析知识点失败 - {str(e)}")
        return {
            "knowledge_points": {
                "basic": [],
                "advanced": [],
                "key_points": [],
                "difficult_points": []
            }
        }

def validate_knowledge_points(knowledge: Dict[str, Any]) -> None:
    """
    验证知识点分析的格式和内容
    
    Args:
        knowledge: 知识点分析字典
        
    Raises:
        ValueError: 如果格式或内容不符合要求
    """
    # 检查基本结构
    if not isinstance(knowledge, dict):
        raise ValueError("知识点分析必须是字典类型")
        
    if "knowledge_points" not in knowledge:
        raise ValueError("缺少knowledge_points字段")
        
    if "relations" not in knowledge:
        raise ValueError("缺少relations字段")
        
    # 检查知识点
    kp = knowledge["knowledge_points"]
    for key in ["basic", "important", "advanced"]:
        if key not in kp:
            raise ValueError(f"知识点缺少{key}字段")
        if not isinstance(kp[key], list):
            raise ValueError(f"{key}必须是列表类型")
        if not kp[key]:
            raise ValueError(f"{key}不能为空")
            
    # 检查关系
    rel = knowledge["relations"]
    for key in ["prerequisites", "connections", "extensions"]:
        if key not in rel:
            raise ValueError(f"关系缺少{key}字段")
        if not isinstance(rel[key], list):
            raise ValueError(f"{key}必须是列表类型")
        if not rel[key]:
            raise ValueError(f"{key}不能为空")
