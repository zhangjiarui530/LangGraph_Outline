from typing import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from ..config import get_llm
from ..utils.types import AgentState

def design_activities(state: AgentState) -> AgentState:
    """设计教学活动的代理"""
    try:
        print("\n=== 开始设计教学活动 ===")
        state["progress_status"] = "正在设计教学活动..."
        
        system_prompt = f"""你是一位创新的教学设计专家。
        你的任务是设计有效的教学活动来实现教学目标。

        请遵循以下原则：
        1. 活动设计要以学生为中心
        2. 结合多样化的教学方法
        3. 注重师生互动和生生互动
        4. 适当运用现代教育技术
        5. 每节课45分钟，总课时{state['total_hours']}课时
        6. 考虑教学内容的难度和学生接受程度
        7. 设计要体现教学目标的层次性和递进性
        8. 注重理论与实践的结合
        9. 适当融入学科核心素养的培养

        输出格式：
        1. 课时分配方案（总计{state['total_hours']}课时）：
           * 知识讲解：X课时（说明分配理由）
           * 技能训练：X课时（说明训练重点）
           * 实践活动：X课时（说明活动特色）
           * 研讨交流：X课时（说明交流形式）
           * 测试评价：X课时（说明评价方式）

        2. 具体活动设计：
           第X课时：[主题名称]
           - 教学重点：（对应知识点）
           - 教学方法：（采用的方法及理由）
           - 教学过程：
             * 导入环节（5分钟）：...
             * 发展环节（30分钟）：...
             * 总结环节（10分钟）：...
           - 设计亮点：（创新之处）
           - 预期效果：（对应教学目标）
           - 可能问题：（教学难点及应对）
        """
        
        user_prompt = f"""
        请基于以下内容，设计总计{state['total_hours']}课时的教学活动。

        教学目标：
        {state['teaching_objectives']}

        知识点体系：
        {state['knowledge_points']}

        请确保你的设计：
        1. 每个活动都明确对应教学目标
        2. 活动难度循序渐进
        3. 时间分配合理，总计{state['total_hours']}课时
        4. 充分考虑学生参与度
        5. 包含必要的复习和巩固环节
        6. 设计适当的课堂互动方式
        7. 注意理论与实践的结合
        """
        
        llm = get_llm(is_scanned=state["is_scanned"])
        print("正在调用 AI 设计教学活动...")
        response = llm.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        content = response.choices[0].message.content
        print("教学活动设计完成，正在解析课时分配...")
        
        # 解析课时分配
        hours_per_section = {}
        for line in content.split('\n'):
            if '：' in line and '课时' in line:
                try:
                    section = line.split('：')[0].strip()
                    hours = int(line.split('：')[1].replace('课时', ''))
                    hours_per_section[section] = hours
                except:
                    continue
        
        # 验证课时总和
        total = sum(hours_per_section.values())
        if total != state['total_hours']:
            raise ValueError(f"课时分配总和({total})不等于指定的总课时数({state['total_hours']})")
        
        activities = [
            {"activity": activity.strip()}
            for activity in content.split('\n')
            if activity.strip()
        ]
        
        # 确保所有字段都有有效值
        new_state = {
            **state,
            "teaching_activities": activities,
            "hours_per_section": hours_per_section,
            "next_step": "create_assessment",
            "messages": [],
            "assessment_plan": state.get("assessment_plan", {}),
            "final_output": state.get("final_output", ""),
            "progress_status": "已设计教学���动",
            "error_msg": None
        }
        print("=== 教学活动设计完成 ===\n")
        return new_state
        
    except Exception as e:
        return {
            **state,
            "error_msg": str(e),
            "next_step": "error",
            "progress_status": "生成失败",
            "messages": [],
            "teaching_objectives": state.get("teaching_objectives"),
            "knowledge_points": state.get("knowledge_points", []),
            "teaching_activities": [],
            "assessment_plan": {},
            "final_output": "",
            "hours_per_section": {}
        } 