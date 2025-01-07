from typing import Dict, Any, List, Annotated
import operator
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.channels.last_value import LastValue
import json

from my_agent.agents.objective_agent import generate_objectives, design_objectives
from my_agent.agents.knowledge_agent import analyze_knowledge
from my_agent.agents.activity_agent import design_activities
from my_agent.agents.assessment_agent import create_assessment
from my_agent.utils.pdf_utils import extract_text_from_pdf, is_valid_pdf, has_table_of_contents
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
            
            # 验证总课时
            total_hours = state["total_hours"][-1] if state["total_hours"] else 0
            if not isinstance(total_hours, int) or total_hours <= 0:
                raise ValueError(f"总课时格式错误: {total_hours}")
                
            if total_hours % 4 != 0:
                raise ValueError(f"总课时必须是4的倍数: {total_hours}")
                
            # 提取教材内容
            textbook_content = state["textbook_content"][-1] if state["textbook_content"] else {}
            if not isinstance(textbook_content, dict):
                raise ValueError(f"教材内容格式错误: {type(textbook_content)}")
                
            # 检查是否为纯图片版本
            if textbook_content.get("chapters"):
                total_text = "".join(chapter.get("content", "") for chapter in textbook_content["chapters"])
                if len(total_text.strip()) < 100:  # 如果提取的文本内容太少，认为是纯图片版本
                    return {
                        "messages": ["检测到纯图片版本的教材，处理终止"],
                        "textbook_content": [textbook_content],
                        "total_hours": [total_hours],
                        "next": ["END"]  # 直接结束处理
                    }
                
            return {
                "messages": ["教材内容处理完成"],
                "textbook_content": [textbook_content],
                "total_hours": [total_hours]
            }
            
        except Exception as e:
            return {"messages": [f"错误：处理教材内容失败 - {str(e)}"]}
            
    def generate_objectives(self, state: TeachingState) -> TeachingState:
        """生成教学目标"""
        try:
            print("\n=== 生成教学目标 ===")
            
            # 获取教材内容
            textbook_content = state["textbook_content"][-1] if state["textbook_content"] else {}
            
            # 获取年级和学科
            grade = state["grade"][-1] if state["grade"] else "7年级"
            subject = state["subject"][-1] if state["subject"] else "语文"
            
            # 根据是否有目录选择不同的目标生成方法
            if textbook_content and has_table_of_contents(textbook_content):
                print("检测到教材包含目录，使用design_objectives方法...")
                # 将字典内容转换为字符串
                content_str = json.dumps(textbook_content, ensure_ascii=False, indent=2)
                result = design_objectives(
                    content_str,
                    state["total_hours"][-1] if state["total_hours"] else 0,
                    grade,
                    subject
                )
            else:
                print("未检测到目录，使用generate_objectives方法...")
                result = generate_objectives(
                    textbook_content,
                    grade,
                    subject
                )
                
            return {
                "messages": ["教学目标生成完成"],
                "objectives": [result],
                "textbook_content": [textbook_content],
                "total_hours": [state["total_hours"][-1] if state["total_hours"] else 0],
                "grade": [grade],
                "subject": [subject]
            }
            
        except Exception as e:
            return {"messages": [f"错误：生成教学目标失败 - {str(e)}"]}
            
    def analyze_knowledge(self, state: TeachingState) -> TeachingState:
        """分析知识点"""
        try:
            print("\n=== 分析知识点 ===")
            
            # 调用知识点代理
            result = analyze_knowledge(
                state["textbook_content"][-1] if state["textbook_content"] else {},
                state["objectives"][-1] if state["objectives"] else {},
                state["grade"][-1] if state["grade"] else "7年级",
                state["subject"][-1] if state["subject"] else "语文"
            )
            return {
                "messages": ["知识点分析完成"],
                "knowledge_points": [result],
                "textbook_content": [state["textbook_content"][-1] if state["textbook_content"] else {}],
                "objectives": [state["objectives"][-1] if state["objectives"] else {}],
                "total_hours": [state["total_hours"][-1] if state["total_hours"] else 0],
                "grade": [state["grade"][-1] if state["grade"] else "7年级"],
                "subject": [state["subject"][-1] if state["subject"] else "语文"]
            }
            
        except Exception as e:
            return {"messages": [f"错误：分析知识点失败 - {str(e)}"]}
            
    def design_activities(self, state: TeachingState) -> TeachingState:
        """设计教学活动"""
        try:
            print("\n=== 设计教学活动 ===")
            
            # 调用活动代理
            result = design_activities(
                state["knowledge_points"][-1] if state["knowledge_points"] else {},
                state["total_hours"][-1] if state["total_hours"] else 0,
                state["grade"][-1] if state["grade"] else "7年级",
                state["subject"][-1] if state["subject"] else "语文"
            )
            return {
                "messages": ["教学活动设计完成"],
                "activities": [result],
                "total_hours": [state["total_hours"][-1] if state["total_hours"] else 0],
                "textbook_content": [state["textbook_content"][-1] if state["textbook_content"] else {}],
                "objectives": [state["objectives"][-1] if state["objectives"] else {}],
                "knowledge_points": [state["knowledge_points"][-1] if state["knowledge_points"] else {}],
                "grade": [state["grade"][-1] if state["grade"] else "7年级"],
                "subject": [state["subject"][-1] if state["subject"] else "语文"]
            }
            
        except Exception as e:
            return {"messages": [f"错误：设计教学活动失败 - {str(e)}"]}
            
    def create_assessment(self, state: TeachingState) -> TeachingState:
        """创建评估方案"""
        try:
            print("\n=== 创建评估方案 ===")
            
            # 调用评估代理
            result = create_assessment(
                state["objectives"][-1] if state["objectives"] else {},
                state["knowledge_points"][-1] if state["knowledge_points"] else {},
                state["grade"][-1] if state["grade"] else "7年级",
                state["subject"][-1] if state["subject"] else "语文"
            )
            return {
                "messages": ["评估方案创建完成"],
                "assessment": [result],
                "total_hours": [state["total_hours"][-1] if state["total_hours"] else 0],
                "textbook_content": [state["textbook_content"][-1] if state["textbook_content"] else {}],
                "objectives": [state["objectives"][-1] if state["objectives"] else {}],
                "knowledge_points": [state["knowledge_points"][-1] if state["knowledge_points"] else {}],
                "grade": [state["grade"][-1] if state["grade"] else "7年级"],
                "subject": [state["subject"][-1] if state["subject"] else "语文"]
            }
            
        except Exception as e:
            return {"messages": [f"错误：创建评估方案失败 - {str(e)}"]}
            
    def save_output(self, state: TeachingState) -> TeachingState:
        """保存输出"""
        try:
            print("\n=== 保存输出 ===")
            
            # 确保所有必要的状态都存在
            required_fields = ["textbook_content", "objectives", "knowledge_points", "activities", "assessment", "total_hours", "grade", "subject"]
            for field in required_fields:
                if field not in state or not state[field]:
                    raise ValueError(f"缺少必要的状态字段: {field}")
            
            # 获取课程名称
            course_name = state["textbook_content"][-1].get("title", "未命名课程")
            
            # 准备输出内容
            output = {
                "meta_info": {
                    "grade": state["grade"][-1],
                    "subject": state["subject"][-1],
                    "total_hours": state["total_hours"][-1],
                    "textbook_title": course_name
                },
                "teaching_objectives": state["objectives"][-1].get("objectives", {}),
                "core_literacy": state["objectives"][-1].get("core_literacy", []),
                "knowledge_points": state["knowledge_points"][-1],
                "teaching_activities": {
                    "activities": state["activities"][-1].get("activities", []),
                    "time_allocation": state["activities"][-1].get("time_allocation", {})
                },
                "assessment_plan": {
                    "formative": state["assessment"][-1].get("assessment_plan", {}).get("formative", []),
                    "summative": state["assessment"][-1].get("assessment_plan", {}).get("summative", []),
                    "weight": state["assessment"][-1].get("assessment_plan", {}).get("weight", {}),
                    "feedback_methods": state["assessment"][-1].get("feedback_methods", [])
                }
            }
            
            # 保存到文件
            save_lesson_plan_to_md(output, course_name)
            return {
                "messages": ["教学大纲已保存"],
                "textbook_content": [state["textbook_content"][-1]],
                "objectives": [state["objectives"][-1]],
                "knowledge_points": [state["knowledge_points"][-1]],
                "activities": [state["activities"][-1]],
                "assessment": [state["assessment"][-1]],
                "total_hours": [state["total_hours"][-1]],
                "grade": [state["grade"][-1]],
                "subject": [state["subject"][-1]]
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
                "subject": [subject]
            }
            
            # 运行状态图
            print("\n开始处理...")
            final_state = self.graph.invoke(initial_state)
            
            print("\n处理完成")
            return final_state
            
        except Exception as e:
            print(f"\n错误：教学代理运行失败 - {str(e)}")
            raise