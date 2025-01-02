<<<<<<< HEAD
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
=======
from typing import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from ..config import get_llm
from ..utils.types import AgentState

def generate_knowledge_points(state: AgentState) -> AgentState:
    """生成知识点的代理"""
    try:
        print("\n=== 开始生成知识点 ===")
        state["progress_status"] = "正在生成知识点..."
        
        system_prompt = """你是一位专业的学科教师和知识图谱专家。
        你的任务是基于教学目标，梳理出系统的知识点体系。

        请遵循以下原则：
        1. 知识点应该层次分明，由浅入深
        2. 每个知识点要具体且可教学
        3. 注意知识点之间的逻辑关联
        4. 标注重难点内容
        5. 考虑到总课时{state['total_hours']}的限制，合理安排知识点数量
        6. 确保知识点覆盖所有教学目标
        7. 注意知识点的连贯性和递进关系

        输出格式：
        1. 基础知识点（必须掌握的核心内容）
           - 每个知识点都要简洁明确
           - 注明该知识点与教学目标的对应关系
           - 标注预计教学难度（易/中/难）

        2. 重点知识（需要重点讲解和训练的内容）
           - 说明为什么是重点
           - 与其他知识点的关联
           - 可能的教学难点提示

        3. 拓展知识（选讲内容，根据课时和学生情况安排）
           - 与基础知识的联系
           - 实际应用场景
           - 建议的教学方式
        """
        
        user_prompt = f"""
        请基于以下教学目标，生成系统的知识点体系。
        注意：这是一个{state['total_hours']}课时的教学单元。

        教学目标：
        {state['teaching_objectives']}

        请确保你的知识点体系：
        1. 完整覆盖所有教学目标
        2. 符合学生认知规律
        3. 便于教师组织教学
        4. 适合{state['total_hours']}课时的教学安排
        5. 重点突出，难点明确
        """
        
        llm = get_llm(is_scanned=state["is_scanned"])
        print("正在调用 AI 生成知识点...")
        response = llm.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        content = response.choices[0].message.content
        print("知识点生成完成")
        
        knowledge_points = [kp.strip() for kp in content.split('\n') if kp.strip()]
        print("=== 知识点生成完成 ===\n")
        
        # 确保所有字段都有有效值
        new_state = {
            **state,
            "knowledge_points": knowledge_points,
            "next_step": "design_activities",
            "messages": [],
            "teaching_activities": state.get("teaching_activities", []),
            "assessment_plan": state.get("assessment_plan", {}),
            "final_output": state.get("final_output", ""),
            "progress_status": "已生成知识点",
            "error_msg": None
        }
        return new_state
        
    except Exception as e:
        return {
            **state,
            "error_msg": str(e),
            "next_step": "error",
            "progress_status": "生成失败",
            "messages": [],
            "teaching_objectives": state.get("teaching_objectives"),
            "knowledge_points": [],
            "teaching_activities": [],
            "assessment_plan": {},
            "final_output": ""
        } 
>>>>>>> c4972e73ce82ab596751226cd0a07e233d3db998
