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
