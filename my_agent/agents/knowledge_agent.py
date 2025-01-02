from typing import Dict, Any, List
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
from my_agent.utils.types import AgentState
import json

def analyze_knowledge(textbook_content: Dict[str, Any], objectives: Dict[str, Any]) -> Dict[str, Any]:
    """分析知识点"""
    try:
        # 验证输入
        if not isinstance(textbook_content, dict):
            raise ValueError(f"教材内容格式错误: {type(textbook_content)}")
            
        if not isinstance(objectives, dict):
            raise ValueError(f"教学目标格式错误: {type(objectives)}")
            
        # 获取LLM配置
        llm_config = get_llm()
        
        # 构建提示词
        content_json = json.dumps(textbook_content, indent=2, ensure_ascii=False)
        objectives_json = json.dumps(objectives, indent=2, ensure_ascii=False)
        template = """作为知识点分析专家，请基于以下教材内容和教学目标分析知识点。

教材内容：
{content}

教学目标：
{objectives}

请分析知识点，要求：
1. 知识点要完整、准确、系统
2. 知识点要有层次性，从基础到深入
3. 知识点要与教学目标对应
4. 知识点要包含重难点标注

请按以下格式输出：
{{
    "knowledge_points": {{
        "basic": [
            {{
                "name": "知识点名称",
                "content": "知识点内容",
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
                "content": "知识点内容",
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

        prompt = template.format(content=content_json, objectives=objectives_json)

        print("\n=== 分析知识点 ===")
        print("调用LLM分析知识点...")
        
        # 调用LLM
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": "你是一个专业的知识点分析专家，擅长分析教材知识点。"},
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
            
        if "knowledge_points" not in result:
            raise ValueError("缺少knowledge_points字段")
            
        knowledge_points = result["knowledge_points"]
        if not isinstance(knowledge_points, dict):
            raise ValueError(f"knowledge_points格式错误: {type(knowledge_points)}")
            
        required_fields = ["basic", "advanced", "key_points", "difficult_points"]
        for field in required_fields:
            if field not in knowledge_points:
                raise ValueError(f"缺少{field}字段")
                
        # 验证基础和高级知识点
        for field in ["basic", "advanced"]:
            points = knowledge_points[field]
            if not isinstance(points, list):
                raise ValueError(f"{field}知识点格式错误")
            if not points:
                raise ValueError(f"{field}知识点不能为空")
            for point in points:
                if not isinstance(point, dict):
                    raise ValueError(f"{field}知识点项格式错误")
                for key in ["name", "content", "difficulty", "importance", "prerequisites", "objectives", "teaching_suggestions"]:
                    if key not in point:
                        raise ValueError(f"{field}知识点缺少{key}字段")
                    if key in ["prerequisites", "objectives"]:
                        if not isinstance(point[key], list):
                            raise ValueError(f"{field}知识点的{key}字段必须是列表")
                    else:
                        if not isinstance(point[key], str):
                            raise ValueError(f"{field}知识点的{key}字段必须是字符串")
                            
        # 验证重难点
        for field in ["key_points", "difficult_points"]:
            points = knowledge_points[field]
            if not isinstance(points, list):
                raise ValueError(f"{field}格式错误")
            if not points:
                raise ValueError(f"{field}不能为空")
            for point in points:
                if not isinstance(point, str):
                    raise ValueError(f"{field}项必须是字符串")
                    
        print("知识点分析完成")
        return result
        
    except Exception as e:
        print(f"错误：分析知识点失败 - {str(e)}")
        raise LLMGenerationError(f"分析知识点失败: {str(e)}")

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