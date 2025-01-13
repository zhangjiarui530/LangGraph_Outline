from typing import Dict, Any, List, Annotated
import operator
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.channels.last_value import LastValue
from langgraph.types import Send
import json
import time

from my_agent.agents.objective_agent import create_objective_subgraph
from my_agent.agents.knowledge_agent import create_knowledge_subgraph
from my_agent.agents.activity_agent import create_activity_subgraph
from my_agent.agents.assessment_agent import create_assessment_subgraph
from my_agent.utils.pdf_utils import extract_text_from_pdf, is_valid_pdf
from my_agent.utils.file_utils import save_lesson_plan_to_md
from my_agent.utils.exceptions import PDFExtractionError, LLMGenerationError

class TeachingState(TypedDict):
    """教学状态"""
    messages: Annotated[List[str], operator.add]
    textbook_content: Annotated[List[Dict[str, Any]], operator.add]
    objectives: Annotated[List[Dict[str, Any]], operator.add]
    knowledge_points: Annotated[List[Dict[str, Any]], operator.add]
    activities: Annotated[List[Dict[str, Any]], operator.add]
    assessment: Annotated[List[Dict[str, Any]], operator.add]
    total_hours: Annotated[List[int], operator.add]
    grade: Annotated[List[str], operator.add]  # 年级
    subject: Annotated[List[str], operator.add]  # 学科
    # 添加目录相关的状态
    toc_content: Annotated[List[str], operator.add]  # 目录内容
    units: Annotated[List[List[str]], operator.add]  # 单元列表
    unit_count: Annotated[List[int], operator.add]  # 单元数量
    # 添加知识点分析的状态
    basic_points: Annotated[List[Dict[str, Any]], operator.add]
    key_points: Annotated[List[Dict[str, Any]], operator.add]
    difficult_points: Annotated[List[Dict[str, Any]], operator.add]
    has_toc: Annotated[List[bool], operator.add]  # 是否包含目录

class TeachingAgent:
    """教学代理"""
    
    def __init__(self):
        """初始化教学代理"""
        # 创建状态图
        self.graph_builder = StateGraph(TeachingState)
        
        # 创建子图
        objective_subgraph = create_objective_subgraph()
        knowledge_subgraph = create_knowledge_subgraph()
        activity_subgraph = create_activity_subgraph()
        assessment_subgraph = create_assessment_subgraph()
        
        # 添加节点
        self.graph_builder.add_node("process_textbook", self.process_textbook)
        # 直接添加编译后的子图作为节点
        self.graph_builder.add_node("generate_objectives", objective_subgraph)
        self.graph_builder.add_node("analyze_knowledge", knowledge_subgraph)
        self.graph_builder.add_node("design_activities", activity_subgraph)
        self.graph_builder.add_node("create_assessment", assessment_subgraph)
        self.graph_builder.add_node("save_output", self.save_output)
        
        # 定义流程
        self.graph_builder.add_edge(START, "process_textbook")
        self.graph_builder.add_edge("process_textbook", "generate_objectives")
        self.graph_builder.add_edge("generate_objectives", "analyze_knowledge")
        
        # 设置并发节点
        self.graph_builder.add_edge("analyze_knowledge", "design_activities")
        self.graph_builder.add_edge("analyze_knowledge", "create_assessment")
        
        # 等待并发节点完成后继续
        self.graph_builder.add_edge("design_activities", "save_output")
        self.graph_builder.add_edge("create_assessment", "save_output")
        self.graph_builder.add_edge("save_output", END)
        
        # 编译图
        self.graph = self.graph_builder.compile()
        
    def process_textbook(self, state: TeachingState) -> TeachingState:
        """处理教材内容"""
        try:
            # 获取参数
            textbook_content = state["textbook_content"][-1] if state["textbook_content"] else {}
            total_hours = state["total_hours"][-1] if state["total_hours"] else 0
            
            # 调用教材处理代理
            from my_agent.agents.textbook_agent import process_textbook
            result = process_textbook(textbook_content, total_hours)
            
            # 如果是纯图片版本，直接返回结果
            if result.get("next") == "END":
                return {
                    "messages": result["messages"],
                    "textbook_content": [result["textbook_content"]],
                    "total_hours": [result["total_hours"]],
                    "next": ["END"]
                }
            
            # 构建返回状态
            return {
                "messages": result["messages"],
                "textbook_content": [result["textbook_content"]],
                "total_hours": [result["total_hours"]],
                "toc_content": [result["toc_content"]],
                "units": [result["units"]],
                "unit_count": [result["unit_count"]],
                "has_toc": [result["has_toc"]]
            }
            
        except Exception as e:
            return {"messages": [f"错误：处理教材内容失败 - {str(e)}"]}
            
    def save_output(self, state: TeachingState) -> TeachingState:
        """保存输出"""
        try:
            # 获取最新的状态值
            current_state = {
                "objectives": state["objectives"][-1] if state["objectives"] else {},
                "knowledge_points": state["knowledge_points"][-1] if state["knowledge_points"] else {},
                "activities": state["activities"][-1] if state["activities"] else {},
                "assessment": state["assessment"][-1] if state["assessment"] else {},
                "grade": state["grade"][-1] if state["grade"] else "",
                "subject": state["subject"][-1] if state["subject"] else "",
                "textbook_content": state["textbook_content"][-1] if state["textbook_content"] else {}
            }
            
            # 调用输出处理代理
            from my_agent.agents.output_agent import save_output
            result = save_output(current_state)
            
            # 构建返回状态
            return {
                "messages": result["messages"],
                "objectives": [result["objectives"]],
                "knowledge_points": [result["knowledge_points"]],
                "activities": [result["activities"]],
                "assessment": [result["assessment"]],
                "grade": [result["grade"]],
                "subject": [result["subject"]]
            }
            
        except Exception as e:
            return {"messages": [f"错误：保存输出失败 - {str(e)}"]}
            
    def run(self, pdf_path: str, total_hours: int, grade: str, subject: str) -> Dict[str, Any]:
        """运行教学代理
        
        Args:
            pdf_path: PDF文件路径
            total_hours: 总课时数
            grade: 年级，默认为7年级
            subject: 学科，默认为语文
        """
        start_time = time.time()
        try:
            print("\n=== 启动教学代理 ===")
            print(f"PDF路径: {pdf_path}")
            print(f"总课时: {total_hours}")
            print(f"年级: {grade}")
            print(f"学科: {subject}")
            
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
                "textbook_content": [textbook_content],
                "objectives": [],
                "knowledge_points": [],
                "activities": [],
                "assessment": [],
                "total_hours": [total_hours],
                "grade": [grade],
                "subject": [subject],
                # 添加目录相关的状态初始值
                "toc_content": [],
                "units": [],
                "unit_count": [],
                # 添加知识点分析的状态初始值
                "basic_points": [],
                "key_points": [],
                "difficult_points": [],
                "has_toc": [False]
            }
            
            # 运行状态图
            print("\n开始处理...")
            final_state = self.graph.invoke(initial_state)
            
            elapsed_time = time.time() - start_time
            print(f"\n处理完成，总耗时：{elapsed_time:.2f}秒")
            return final_state
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"\n错误：教学代理运行失败 - {str(e)}")
            print(f"失败总耗时：{elapsed_time:.2f}秒")
            raise