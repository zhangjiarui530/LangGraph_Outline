<<<<<<< HEAD
from typing import Dict, Any, List, Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from my_agent.agents.objective_agent import generate_objectives
from my_agent.agents.knowledge_agent import analyze_knowledge
from my_agent.agents.activity_agent import design_activities
from my_agent.agents.assessment_agent import create_assessment
from my_agent.utils.pdf_utils import extract_text_from_pdf, is_valid_pdf
from my_agent.utils.file_utils import save_lesson_plan_to_md
from my_agent.utils.exceptions import PDFExtractionError, LLMGenerationError

class TeachingState(TypedDict):
    """教学状态"""
    messages: Annotated[List[str], add_messages]  # 使用add_messages来处理消息追加
    textbook_content: Dict[str, Any]
    objectives: Dict[str, Any]
    knowledge_points: Dict[str, Any]
    activities: Dict[str, Any]
    assessment: Dict[str, Any]
    total_hours: int

class TeachingAgent:
    """教学代理"""
    
    def __init__(self):
        """初始化教学代理"""
        # 创建状态图
        self.graph_builder = StateGraph(TeachingState)
        
        # 添加节点
        self.graph_builder.add_node("process_textbook", self.process_textbook)
        self.graph_builder.add_node("generate_objectives", self.generate_objectives)
        self.graph_builder.add_node("analyze_knowledge", self.analyze_knowledge)
        self.graph_builder.add_node("design_activities", self.design_activities)
        self.graph_builder.add_node("create_assessment", self.create_assessment)
        self.graph_builder.add_node("save_output", self.save_output)
        
        # 定义流程
        self.graph_builder.add_edge(START, "process_textbook")
        self.graph_builder.add_edge("process_textbook", "generate_objectives")
        self.graph_builder.add_edge("generate_objectives", "analyze_knowledge")
        self.graph_builder.add_edge("analyze_knowledge", "design_activities")
        self.graph_builder.add_edge("design_activities", "create_assessment")
        self.graph_builder.add_edge("create_assessment", "save_output")
        self.graph_builder.add_edge("save_output", END)
        
        # 编译图
        self.graph = self.graph_builder.compile()
        
    def process_textbook(self, state: TeachingState) -> TeachingState:
        """处理教材内容"""
        try:
            print("\n=== 处理教材内容 ===")
            
            # 验证总课时
            total_hours = state["total_hours"]
            if not isinstance(total_hours, int) or total_hours <= 0:
                raise ValueError(f"总课时格式错误: {total_hours}")
                
            if total_hours % 4 != 0:
                raise ValueError(f"总课时必须是4的倍数: {total_hours}")
                
            # 提取教材内容
            textbook_content = state["textbook_content"]
            if not isinstance(textbook_content, dict):
                raise ValueError(f"教材内容格式错误: {type(textbook_content)}")
                
            return {"messages": ["教材内容处理完成"]}
            
        except Exception as e:
            return {"messages": [f"错误：处理教材内容失败 - {str(e)}"]}
            
    def generate_objectives(self, state: TeachingState) -> TeachingState:
        """生成教学目标"""
        try:
            print("\n=== 生成教学目标 ===")
            
            # 调用目标代理
            result = generate_objectives(state["textbook_content"])
            return {
                "messages": ["教学目标生成完成"],
                "objectives": result
            }
            
        except Exception as e:
            return {"messages": [f"错误：生成教学目标失败 - {str(e)}"]}
            
    def analyze_knowledge(self, state: TeachingState) -> TeachingState:
        """分析知识点"""
        try:
            print("\n=== 分析知识点 ===")
            
            # 调用知识点代理
            result = analyze_knowledge(state["textbook_content"], state["objectives"])
            return {
                "messages": ["知识点分析完成"],
                "knowledge_points": result
            }
            
        except Exception as e:
            return {"messages": [f"错误：分析知识点失败 - {str(e)}"]}
            
    def design_activities(self, state: TeachingState) -> TeachingState:
        """设计教学活动"""
        try:
            print("\n=== 设计教学活动 ===")
            
            # 调用活动代理
            result = design_activities(state["knowledge_points"], state["total_hours"])
            return {
                "messages": ["教学活动设计完成"],
                "activities": result
            }
            
        except Exception as e:
            return {"messages": [f"错误：设计教学活动失败 - {str(e)}"]}
            
    def create_assessment(self, state: TeachingState) -> TeachingState:
        """创建评估方案"""
        try:
            print("\n=== 创建评估方案 ===")
            
            # 调用评估代理
            result = create_assessment(state["objectives"], state["knowledge_points"])
            return {
                "messages": ["评估方案创建完成"],
                "assessment": result
            }
            
        except Exception as e:
            return {"messages": [f"错误：创建评估方案失败 - {str(e)}"]}
            
    def save_output(self, state: TeachingState) -> TeachingState:
        """保存输出"""
        try:
            print("\n=== 保存输出 ===")
            
            # 获取课程名称
            course_name = state["textbook_content"].get("title", "未命名课程")
            
            # 准备输出内容
            output = {
                "objectives": state["objectives"],
                "knowledge_points": state["knowledge_points"],
                "activities": state["activities"],
                "assessment": state["assessment"],
                "total_hours": state["total_hours"]
            }
            
            # 保存到文件
            save_lesson_plan_to_md(output, course_name)
            return {"messages": ["教学大纲已保存"]}
            
        except Exception as e:
            return {"messages": [f"错误：保存输出失败 - {str(e)}"]}
            
    def run(self, pdf_path: str, total_hours: int) -> Dict[str, Any]:
        """运行教学代理"""
        try:
            print("\n=== 启动教学代理 ===")
            print(f"PDF路径: {pdf_path}")
            print(f"总课时: {total_hours}")
            
            # 验证PDF文件
            if not is_valid_pdf(pdf_path):
                raise ValueError(f"无效的PDF文件: {pdf_path}")
            
            # 提取教材内容
            print("正在提取PDF内容...")
            textbook_content = extract_text_from_pdf(pdf_path)
            print("PDF内容提取完成")
            
            # 初始化状态
            initial_state: TeachingState = {
                "messages": [],
                "textbook_content": textbook_content,
                "objectives": {},
                "knowledge_points": {},
                "activities": {},
                "assessment": {},
                "total_hours": total_hours
            }
            
            # 运行状态图
            print("\n开始处理...")
            final_state = initial_state
            for event in self.graph.stream(initial_state):
                for key, value in event.items():
                    if isinstance(value, dict):
                        final_state.update(value)
                    if "messages" in value:
                        for message in value["messages"]:
                            print(f"- {message}")
            
            print("\n处理完成")
            return final_state
            
        except Exception as e:
            print(f"\n错误：教学代理运行失败 - {str(e)}")
            raise
=======
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
>>>>>>> c4972e73ce82ab596751226cd0a07e233d3db998
