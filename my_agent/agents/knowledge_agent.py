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