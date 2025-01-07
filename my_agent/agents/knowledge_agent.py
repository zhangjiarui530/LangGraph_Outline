from typing import Dict, Any, List, Optional
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
import json

def analyze_knowledge(content: Dict[str, Any], objectives: Dict[str, Any], grade: str, subject: str) -> Dict[str, Any]:
    """分析知识点"""
    try:
        # 获取LLM配置
        llm_config = get_llm()
        
        # 构建提示词
        content_json = json.dumps(content, indent=2, ensure_ascii=False)
        objectives_json = json.dumps(objectives, indent=2, ensure_ascii=False)
        template = """作为一名资深的{subject}教师，请基于以下教材内容和教学目标为{grade}学生分析知识点。

教材内容：
{content}

教学目标：
{objectives}

请分析并输出完整的知识点体系，要求：
1. 将知识点分为基础和拓展两个层次
2. 每个知识点要说明：
   - 名称
   - 具体内容
   - 难度（简单/中等/困难）
   - 重要程度（核心/重要/一般）
   - 前置知识点
   - 对应教学目标
   - 教学建议
3. 分析要：
   - 符合{subject}学科特点
   - 体现教学目标
   - 难度符合{grade}学生认知水平
   - 逻辑合理
   - 便于教学

请按以下格式输出：
{{
    "knowledge_points": {{
        "basic": [
            {{
                "name": "知识点名称",
                "content": "具体内容",
                "difficulty": "难度",
                "importance": "重要程度",
                "prerequisites": ["前置知识点1", "前置知识点2"],
                "objectives": ["对应目标1", "对应目标2"],
                "teaching_suggestions": "教学建议"
            }}
        ],
        "advanced": [
            {{
                "name": "知识点名称",
                "content": "具体内容",
                "difficulty": "难度",
                "importance": "重要程度",
                "prerequisites": ["前置知识点1", "前置知识点2"],
                "objectives": ["对应目标1", "对应目标2"],
                "teaching_suggestions": "教学建议"
            }}
        ],
        "key_points": ["重点1", "重点2"],
        "difficult_points": ["难点1", "难点2"]
    }}
}}"""

        prompt = template.format(
            content=content_json,
            objectives=objectives_json,
            grade=grade,
            subject=subject
        )

        print("\n=== 分析知识点 ===")
        print("调用LLM分析知识点...")
        
        # 调用LLM
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": f"你是一个专业的{subject}教师，擅长分析教材知识点。你的分析要符合新课标要求，体现{subject}学科特点，适合{grade}学生的认知水平。"},
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
                "basic": [
                    {
                        "name": "基础知识点",
                        "content": "暂无内容",
                        "difficulty": "中等",
                        "importance": "核心",
                        "prerequisites": [],
                        "objectives": [],
                        "teaching_suggestions": "暂无建议"
                    }
                ],
                "advanced": [
                    {
                        "name": "拓展知识点",
                        "content": "暂无内容",
                        "difficulty": "困难",
                        "importance": "重要",
                        "prerequisites": [],
                        "objectives": [],
                        "teaching_suggestions": "暂无建议"
                    }
                ],
                "key_points": ["暂无重点"],
                "difficult_points": ["暂无难点"]
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
