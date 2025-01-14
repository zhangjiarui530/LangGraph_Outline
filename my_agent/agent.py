from typing import Dict, Any, List, Annotated, TypeVar, Optional, Union
import operator
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.channels.last_value import LastValue
from langgraph.types import Send
from langchain_core.messages import HumanMessage
import json
import time

from my_agent.agents.objective_agent import create_objective_subgraph
from my_agent.agents.knowledge_agent import create_knowledge_subgraph
from my_agent.agents.activity_agent import create_activity_subgraph
from my_agent.agents.assessment_agent import create_assessment_subgraph

class TeachingInputState(TypedDict):
    """教学输入状态"""
    messages: List[HumanMessage]  # 输入消息列表

class TeachingOutputState(TypedDict):
    """教学输出状态"""
    messages: List[str]  # 处理消息
    objectives: Dict[str, Any]  # 教学目标
    knowledge_points: Dict[str, Any]  # 知识点
    activities: Dict[str, Any]  # 教学活动
    assessment: Dict[str, Any]  # 评估方案
    final_outline: Dict[str, Any]  # 最终的教学大纲内容

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
    pdf_path: Annotated[List[str], operator.add]  # PDF文件路径
    # 添加目录相关的状态
    toc_content: Annotated[List[str], operator.add]  # 目录内容
    units: Annotated[List[List[str]], operator.add]  # 单元列表
    unit_count: Annotated[List[int], operator.add]  # 单元数量
    # 添加知识点分析的状态
    basic_points: Annotated[List[Dict[str, Any]], operator.add]
    key_points: Annotated[List[Dict[str, Any]], operator.add]
    difficult_points: Annotated[List[Dict[str, Any]], operator.add]
    has_toc: Annotated[List[bool], operator.add]  # 是否包含目录
    final_outline: Annotated[List[Dict[str, Any]], operator.add]  # 最终的教学大纲内容

class TeachingAgent:
    """教学代理"""
    
    def __init__(self):
        """初始化教学代理"""
        # 创建状态图，指定状态类型
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
            print("\n=== 处理教材内容 ===")
            print(f"接收到的状态: {state}")
            
            # 获取参数
            if not state.get("pdf_path"):
                raise ValueError("状态中缺少pdf_path")
                
            pdf_path = state["pdf_path"][0]  # 获取第一个元素
            total_hours = state["total_hours"][0] if state["total_hours"] else 0
            
            print(f"从状态获取到的PDF路径: {pdf_path}")
            print(f"从状态获取到的总课时: {total_hours}")
            
            # 调用教材处理代理
            from my_agent.agents.textbook_agent import process_textbook
            result = process_textbook(pdf_path, total_hours)
            
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
            print(f"处理教材内容失败: {str(e)}")
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
            
            # print("保存输出结果:", result)  # 添加调试日志
            
            # 返回消息和最终大纲
            return {
                "messages": result["messages"],
                "final_outline": [result["final_outline"]],  # 确保final_outline是字符串
                "objectives": state["objectives"],
                "knowledge_points": state["knowledge_points"],
                "activities": state["activities"],
                "assessment": state["assessment"]
            }
            
        except Exception as e:
            print(f"保存输出失败: {str(e)}")  # 添加错误日志
            return {"messages": [f"错误：保存输出失败 - {str(e)}"]}
            
    def run(self, config: TeachingInputState) -> TeachingOutputState:
        """运行教学代理
        
        Args:
            config: 教学输入状态，包含以下字段：
                - messages: List[HumanMessage] 输入消息列表，第一条消息应该是JSON格式的配置
            
        Returns:
            TeachingOutputState: 处理结果，包含处理消息、最终大纲和具体内容
        """
        start_time = time.time()
        try:
            # 解析第一条消息中的配置
            if not config["messages"]:
                raise ValueError("没有输入消息")
            
            first_message = config["messages"][0]
            input_config = json.loads(first_message.content)
            
            print("\n=== 启动教学代理 ===")
            print(f"PDF路径: {input_config['pdf_path']}")
            print(f"总课时: {input_config['total_hours']}")
            print(f"年级: {input_config['grade']}")
            print(f"学科: {input_config['subject']}")
            
            # 初始化状态
            initial_state: TeachingState = {
                "messages": [],
                "textbook_content": [],
                "objectives": [],
                "knowledge_points": [],
                "activities": [],
                "assessment": [],
                "total_hours": [input_config['total_hours']],
                "grade": [input_config['grade']],
                "subject": [input_config['subject']],
                # 添加目录相关的状态初始值
                "toc_content": [],
                "units": [],
                "unit_count": [],
                # 添加知识点分析的状态初始值
                "basic_points": [],
                "key_points": [],
                "difficult_points": [],
                "has_toc": [False],
                "pdf_path": [input_config['pdf_path']],  # 添加PDF路径到状态
                "final_outline": []
            }
            
            print("\n初始状态:")
            print(f"PDF路径: {initial_state['pdf_path']}")
            print(f"总课时: {initial_state['total_hours']}")
            print(f"年级: {initial_state['grade']}")
            print(f"学科: {initial_state['subject']}")
            
            # 运行状态图
            print("\n开始处理...")
            final_state = self.graph.invoke(initial_state)
            
            # print("最终状态:", final_state)  # 添加调试日志
            
            # 构造输出状态
            output_state: TeachingOutputState = {
                "messages": final_state.get("messages", []),
                "final_outline": final_state.get("final_outline", [""])[-1],  # 确保有默认值
                "objectives": final_state.get("objectives", [{}])[-1],
                "knowledge_points": final_state.get("knowledge_points", [{}])[-1],
                "activities": final_state.get("activities", [{}])[-1],
                "assessment": final_state.get("assessment", [{}])[-1]
            }
            
            # print("输出状态:", output_state)  # 添加调试日志
            
            elapsed_time = time.time() - start_time
            print(f"\n处理完成，总耗时：{elapsed_time:.2f}秒")
            return output_state
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"\n错误：教学代理运行失败 - {str(e)}")
            print(f"失败耗时：{elapsed_time:.2f}秒")
            raise