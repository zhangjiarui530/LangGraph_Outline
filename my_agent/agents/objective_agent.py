from typing import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from my_agent.config import get_llm
from my_agent.utils.types import AgentState
from my_agent.utils.exceptions import LLMGenerationError

def analyze_objectives(state: AgentState) -> AgentState:
    """分析教学目标的代理"""
    try:
        print("\n=== 开始分析教学目标 ===")
        state["progress_status"] = "正在分析教学目标..."
        
        system_prompt = """你是一位资深的教育专家和课程设计师，拥有丰富的教学大纲编写经验。
        你的任务是分析教材内容，提炼出清晰、可衡量的教学目标。

        请遵循以下原则：
        1. 目标应该具体、可测量、可实现、相关且有时限
        2. 需要涵盖知识、能力和素养三个维度
        3. 使用布鲁姆教育目标分类法的动词
        4. 确保目标与课程难度和学生水平相适应
        5. 每个维度的目标应该相互关联，形成完整的学习体系
        6. 考虑到总课时{state['total_hours']}的限制，设定合理的目标数量

        输出格式要求：
        1. 知识目标：（使用理解、记忆、应用等动词）
           - 目标应该清晰具体，避免模糊表述
           - 每个目标都应该可以通过评估来验证

        2. 能力目标：（使用分析、评价、创造等动词）
           - 重点关注高阶思维能力的培养
           - 目标应该与实际应用场景相结合

        3. 素养目标：（关注学科素养和核心素养的培养）
           - 体现学科特色和育人价值
           - 与学生的生活经验和未来发展相联系
        """
        
        user_prompt = f"""
        请基于以下教材内容，分析并提炼教学目标。
        注意：这是一个{state['total_hours']}课时的教学单元。

        教材内容：
        {state['file_content']}

        请确保你的分析：
        1. 准确把握教材重点和难点
        2. 考虑学生的认知水平和学习特点
        3. 体现教材的育人价值和学科特色
        """
        
        llm = get_llm(is_scanned=state["is_scanned"])
        print("正在调用 AI 分析教学目标...")  # 添加提示
        response = llm.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        content = response.choices[0].message.content
        print("教学目标分析完成")  # 添加提示
        
        if not content:
            raise LLMGenerationError("生成的教学目标为空")
        
        print("=== 教学目标分析完成 ===\n")  # 添加提示
        
        # 确保所有字段都有有效值
        new_state = {
            **state,
            "teaching_objectives": content,
            "next_step": "generate_knowledge_points",
            "messages": [],
            "knowledge_points": state.get("knowledge_points", []),
            "teaching_activities": state.get("teaching_activities", []),
            "assessment_plan": state.get("assessment_plan", {}),
            "final_output": state.get("final_output", ""),
            "progress_status": "已生成教学目标",
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
            "teaching_objectives": None,
            "knowledge_points": [],
            "teaching_activities": [],
            "assessment_plan": {},
            "final_output": ""
        } 