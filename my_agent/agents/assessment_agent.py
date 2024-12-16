from typing import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from ..config import get_llm
from ..utils.types import AgentState
from ..utils.output_formatter import format_final_output

def create_assessment(state: AgentState) -> AgentState:
    """创建评估方案的代理"""
    try:
        print("\n=== 开始生成评估方案 ===")
        state["progress_status"] = "正在制定评估方案..."
        
        system_prompt = """你是一位教育评估专家。
        你的任务是设计全面的评估方案来检验教学目标的达成情况。

        请遵循以下原则：
        1. 评估方式要多元化
        2. 注重过程性评价和终结性评价相结合
        3. 评估标准要清晰可操作
        4. 关注学生的全面发展
        5. 评估要体现素养导向
        6. 注重学生的自主评价和互评
        7. 评估结果要能指导教学改进

        输出格式：
        1. 过程性评价方案（占比60%）：
           A. 课堂表现（20%）
              - 具体评估要点
              - 评分标准
              - 记录方式
           
           B. 作业完成（20%）
              - 作业类型和要求
              - 批改要点
              - 反馈方式
           
           C. 实践活动（20%）
              - 活动评价维度
              - 评价方法
              - 证据收集

        2. 终结性评价方案（占比40%）：
           A. 理论测试
              - 题型设置
              - 难度分布
              - 重点考查内容
           
           B. 实践考核
              - 考核形式
              - 评分标准
              - 注意事项

        3. 评价反馈机制：
           - 及时反馈方式
           - 结果运用建议
           - 改进策略设计
        """
        
        user_prompt = f"""
        请基于以下内容，设计完整的评估方案。

        教学目标：
        {state['teaching_objectives']}

        知识点体系：
        {state['knowledge_points']}

        教学活动：
        {state['teaching_activities']}

        请确保评估方案：
        1. 全面覆盖教学目标
        2. 评价方式多样
        3. 标准清晰可操作
        4. 注重过程性评价
        5. 体现素养导向
        6. 具有可行性
        7. 促进教学改进
        """
        
        llm = get_llm(is_scanned=state["is_scanned"])
        print("正在调用 AI 生成评估方案...")
        response = llm.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        content = response.choices[0].message.content
        print("评估方案生成完成，正在整理输出...")
        
        assessment_plan = {
            "plan": content
        }
        
        # 生成最终输出
        final_output = format_final_output({
            **state,
            "assessment_plan": assessment_plan
        })
        
        print("正在保存最终结果...")
        # 确保所有字段都有有效值
        new_state = {
            **state,
            "assessment_plan": assessment_plan,
            "next_step": "end",
            "messages": [],
            "final_output": final_output,
            "progress_status": "已完成评估方案",
            "error_msg": None
        }
        print("=== 评估方案生成完成 ===\n")
        return new_state
        
    except Exception as e:
        print(f"\n!!! 评估方案生成失败: {str(e)} !!!\n")
        return {
            **state,
            "error_msg": str(e),
            "next_step": "error",
            "progress_status": "生成失败",
            "messages": [],
            "teaching_objectives": state.get("teaching_objectives"),
            "knowledge_points": state.get("knowledge_points", []),
            "teaching_activities": state.get("teaching_activities", []),
            "assessment_plan": {},
            "final_output": "",
            "hours_per_section": state.get("hours_per_section", {})
        } 