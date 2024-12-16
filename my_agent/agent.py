from typing import Tuple
import os
from langgraph.graph import Graph, StateGraph
from langchain_core.messages import BaseMessage

from my_agent.agents.objective_agent import analyze_objectives
from my_agent.agents.knowledge_agent import generate_knowledge_points
from my_agent.agents.activity_agent import design_activities
from my_agent.agents.assessment_agent import create_assessment
from my_agent.utils.types import AgentState
from my_agent.utils.pdf_utils import extract_pdf_content
from my_agent.utils.exceptions import LessonPlanError, FileFormatError, ContentExtractionError
from my_agent.utils.file_utils import save_lesson_plan_to_md

def should_go_to_error(state: AgentState) -> bool:
    """检查是否需要进入错误状态"""
    return state.get("error_msg") is not None

def create_lesson_plan_graph() -> Graph:
    """创建教学大纲生成工作流图"""
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("analyze_objectives", analyze_objectives)
    workflow.add_node("generate_knowledge_points", generate_knowledge_points)
    workflow.add_node("design_activities", design_activities)
    workflow.add_node("create_assessment", create_assessment)
    workflow.add_node("error", lambda x: {**x, "next_step": "end"})
    
    # 设置边和条件
    workflow.add_edge("analyze_objectives", "generate_knowledge_points")
    workflow.add_edge("generate_knowledge_points", "design_activities")
    workflow.add_edge("design_activities", "create_assessment")
    
    # 添加错误处理边
    workflow.add_edge("analyze_objectives", "error")
    workflow.add_edge("generate_knowledge_points", "error")
    workflow.add_edge("design_activities", "error")
    workflow.add_edge("create_assessment", "error")
    
    # 设置条件函数
    def should_go_to_error(state: AgentState) -> bool:
        return state.get("error_msg") is not None

    # 为每个节点添加条件路由
    workflow.add_conditional_edges(
        "analyze_objectives",
        should_go_to_error,
        {
            True: "error",
            False: "generate_knowledge_points"
        }
    )
    
    workflow.add_conditional_edges(
        "generate_knowledge_points",
        should_go_to_error,
        {
            True: "error",
            False: "design_activities"
        }
    )
    
    workflow.add_conditional_edges(
        "design_activities",
        should_go_to_error,
        {
            True: "error",
            False: "create_assessment"
        }
    )
    
    workflow.set_entry_point("analyze_objectives")
    workflow.set_finish_point("create_assessment")
    workflow.set_finish_point("error")
    
    return workflow.compile()

def generate_lesson_plan(pdf_path: str, total_hours: int) -> Tuple[str, str, str | None]:
    """
    生成教学大纲
    
    Args:
        pdf_path: PDF文件路径
        total_hours: 总课时数
        
    Returns:
        tuple[str, str, str | None]: (进度状态, 最终输出或错误信息, 保存的文件路径)
    """
    try:
        graph = create_lesson_plan_graph()
        
        print("正在提取文件内容...")
        file_content, is_scanned = extract_pdf_content(pdf_path)
        print(f"提取的内容长度: {len(file_content) if file_content else 0}")
        
        # 准备初始状态
        initial_state: AgentState = {
            "messages": [],
            "teaching_objectives": None,
            "knowledge_points": None,
            "teaching_activities": None,
            "assessment_plan": None,
            "next_step": "analyze_objectives",
            "final_output": None,
            "file_content": file_content,
            "progress_status": "开始生成教学大纲...",
            "error_msg": None,
            "total_hours": total_hours,
            "hours_per_section": None,
            "is_scanned": is_scanned
        }
        
        print("开始运行工作流...")
        result = graph.invoke(initial_state)
        
        if result["error_msg"]:
            return "生成失败", f"无法生成教学大纲：{result['error_msg']}", None
            
        course_name = os.path.splitext(os.path.basename(pdf_path))[0]
        saved_path = save_lesson_plan_to_md(result["final_output"], course_name)
            
        return result["progress_status"], result["final_output"], saved_path
        
    except FileFormatError as e:
        print(f"文件格式错误: {str(e)}")
        return "格式错误", f"无法生成教学大纲：{str(e)}", None
    except ContentExtractionError as e:
        print(f"内容提取错误: {str(e)}")
        return "内容提取失败", f"无法生成教学大纲：{str(e)}", None
    except Exception as e:
        print(f"发生未预期的错误: {str(e)}")
        return "系统错误", "无法生成教学大纲，请检查教材格式或稍后再试", None

def main():
    """主函数"""
    pdf_path = r"C:\Users\Intel\Desktop\Dase2025\4_OpenTeacherAssistant\langgraphoutline\textbooks\普通高中教科书·语文必修 下册.pdf"
    if not os.path.exists(pdf_path):
        print(f"错误：找不到文件 {pdf_path}")
        return
        
    # 获取用户输入的课时数
    while True:
        try:
            total_hours = int(input("请输入总课时数："))
            if total_hours <= 0:
                print("课时数必须大于0")
                continue
            break
        except ValueError:
            print("请输入有效的数字")

    print(f"\n开始处理教材：{pdf_path}")
    print(f"总课时数：{total_hours}")
    
    status, content, file_path = generate_lesson_plan(pdf_path, total_hours)
    
    if file_path:
        print(f"\n生成状态：{status}")
        print(f"教学大纲已保存至：{file_path}")
    else:
        print(f"\n{status}：{content}")

if __name__ == "__main__":
    main()
