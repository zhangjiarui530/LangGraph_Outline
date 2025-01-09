from typing import Dict, Any, List, Annotated
import operator
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.channels.last_value import LastValue
from langgraph.types import Send
import json
import time

from my_agent.agents.objective_agent import generate_objectives, design_objectives
from my_agent.agents.knowledge_agent import analyze_point_type, get_point_config
from my_agent.agents.activity_agent import design_activities
from my_agent.agents.assessment_agent import create_assessment
from my_agent.utils.pdf_utils import extract_text_from_pdf, is_valid_pdf, has_table_of_contents, extract_toc_content
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
        
        # 添加节点
        self.graph_builder.add_node("process_textbook", self.process_textbook)
        self.graph_builder.add_node("generate_objectives", self.generate_objectives)
        self.graph_builder.add_node("analyze_knowledge", self.analyze_knowledge)
        self.graph_builder.add_node("analyze_point", self.analyze_point)
        self.graph_builder.add_node("merge_knowledge", self.merge_knowledge)
        self.graph_builder.add_node("design_activities", self.design_activities)
        self.graph_builder.add_node("create_assessment", self.create_assessment)
        self.graph_builder.add_node("save_output", self.save_output)
        
        # 定义流程
        self.graph_builder.add_edge(START, "process_textbook")
        self.graph_builder.add_edge("process_textbook", "generate_objectives")
        self.graph_builder.add_edge("generate_objectives", "analyze_knowledge")
        
        # 设置知识点分析的MapReduce流程
        self.graph_builder.add_conditional_edges(
            "analyze_knowledge",
            self.continue_to_point_analysis,
            ["analyze_point"]
        )
        self.graph_builder.add_edge("analyze_point", "merge_knowledge")
        
        # 设置并发节点
        self.graph_builder.add_edge("merge_knowledge", "design_activities")
        self.graph_builder.add_edge("merge_knowledge", "create_assessment")
        
        # 等待并发节点完成后继续
        self.graph_builder.add_edge("design_activities", "save_output")
        self.graph_builder.add_edge("create_assessment", "save_output")
        self.graph_builder.add_edge("save_output", END)
        
        # 编译图
        self.graph = self.graph_builder.compile()
        
    def process_textbook(self, state: TeachingState) -> TeachingState:
        """处理教材内容"""
        start_time = time.time()
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

            # 检查是否包含目录
            print("检查教材是否包含目录...")
            has_toc = has_table_of_contents(textbook_content)
            print(f"目录检查结果：{'包含目录' if has_toc else '未包含目录'}")

            # 提取目录内容
            print("正在提取目录内容...")
            toc_content = extract_toc_content(textbook_content) if has_toc else ""
            if not toc_content:
                print("未找到目录内容，将使用完整内容...")
                toc_content = json.dumps(textbook_content, ensure_ascii=False, indent=2)
            
            print(f"成功提取目录内容，长度：{len(toc_content)}")
            
            # 计算单元数量
            import re
            unit_count = 0
            chapter_count = 0
            units = []  # 存储单元名称
            
            for line in toc_content.split('\n'):
                # 匹配单元标题
                unit_match = re.search(r'第[一二三四五六七八九十\d]+单元[^，。；]*', line)
                if unit_match:
                    unit_count += 1
                    units.append(unit_match.group())
                # 如果没有单元，匹配章节
                elif re.search(r'第[一二三四五六七八九十\d]+章', line):
                    chapter_count += 1
            
            # 如果没有找到单元，使用章节作为单元
            if unit_count == 0:
                unit_count = chapter_count
                print(f"未找到单元，使用章节数：{chapter_count}")
                
            if unit_count == 0:
                print("未找到单元或章节数量，将使用默认值")
                unit_count = 6  # 默认值
                
            print(f"检测到单元数量：{unit_count}")
            if units:
                print("单元列表：")
                for unit in units:
                    print(f"  - {unit}")
                
            elapsed_time = time.time() - start_time
            print(f"教材内容处理完成，耗时：{elapsed_time:.2f}秒")
            return {
                "messages": ["教材内容处理完成"],
                "textbook_content": [textbook_content],
                "total_hours": [total_hours],
                "toc_content": [toc_content],  # 添加目录内容到状态
                "units": [units],  # 添加单元列表到状态
                "unit_count": [unit_count],  # 添加单元数量到状态
                "has_toc": [has_toc]  # 添加是否包含目录的标志
            }
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"错误：处理教材内容失败 - {str(e)}")
            print(f"失败耗时：{elapsed_time:.2f}秒")
            return {"messages": [f"错误：处理教材内容失败 - {str(e)}"]}
            
    def generate_objectives(self, state: TeachingState) -> TeachingState:
        """生成教学目标"""
        start_time = time.time()
        try:
            print("\n=== 生成教学目标 ===")
            
            # 获取教材内容
            textbook_content = state["textbook_content"][-1] if state["textbook_content"] else {}
            
            # 获取年级和学科
            grade = state["grade"][-1] if state["grade"] else "7年级"
            subject = state["subject"][-1] if state["subject"] else "语文"
            
            # 根据是否有目录选择不同的目标生成方法
            has_toc = state["has_toc"][-1] if state["has_toc"] else False
            if has_toc:
                print("检测到教材包含目录，使用design_objectives方法...")
                # 构建包含目录内容的字典
                content_dict = {
                    "textbook_content": textbook_content,
                    "toc_content": state["toc_content"][-1] if state["toc_content"] else "",
                    "units": state["units"][-1] if state["units"] else [],
                    "unit_count": state["unit_count"][-1] if state["unit_count"] else 0
                }
                # 将字典内容转换为字符串
                content_str = json.dumps(content_dict, ensure_ascii=False, indent=2)
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
                
            elapsed_time = time.time() - start_time
            print(f"教学目标生成完成，耗时：{elapsed_time:.2f}秒")
            return {
                "messages": ["教学目标生成完成"],
                "objectives": [result],
                "textbook_content": [textbook_content],
                "total_hours": [state["total_hours"][-1] if state["total_hours"] else 0],
                "grade": [grade],
                "subject": [subject]
            }
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"错误：生成教学目标失败 - {str(e)}")
            print(f"失败耗时：{elapsed_time:.2f}秒")
            return {"messages": [f"错误：生成教学目标失败 - {str(e)}"]}
            
    def continue_to_point_analysis(self, state: TeachingState):
        """将状态分发到各个知识点分析节点"""
        point_types = ["basic", "key", "difficult"]
        
        # 获取最新的状态值
        textbook_content = state["textbook_content"][-1] if state["textbook_content"] else {}
        objectives = state["objectives"][-1] if state["objectives"] else {}
        grade = state["grade"][-1] if state["grade"] else ""
        subject = state["subject"][-1] if state["subject"] else ""
        toc_content = state["toc_content"][-1] if state["toc_content"] else ""
        units = state["units"][-1] if state["units"] else []
        unit_count = state["unit_count"][-1] if state["unit_count"] else 0
        
        return [
            Send("analyze_point", {
                "content": textbook_content,
                "objectives": objectives,
                "grade": grade,
                "subject": subject,
                "point_type": point_type,
                "toc_content": toc_content,
                "units": units,
                "unit_count": unit_count
            })
            for point_type in point_types
        ]
            
    def analyze_knowledge(self, state: TeachingState) -> TeachingState:
        """分析知识点 - Map阶段"""
        try:
            print("\n=== 开始知识点分析 ===")
            
            # 获取最新的状态值
            textbook_content = state["textbook_content"][-1] if state["textbook_content"] else {}
            objectives = state["objectives"][-1] if state["objectives"] else {}
            grade = state["grade"][-1] if state["grade"] else ""
            subject = state["subject"][-1] if state["subject"] else ""
            toc_content = state["toc_content"][-1] if state["toc_content"] else ""
            units = state["units"][-1] if state["units"] else []
            unit_count = state["unit_count"][-1] if state["unit_count"] else 0
            
            return {
                "messages": ["开始知识点分析"],
                "textbook_content": [textbook_content],
                "objectives": [objectives],
                "grade": [grade],
                "subject": [subject],
                "toc_content": [toc_content],
                "units": [units],
                "unit_count": [unit_count]
            }
        except Exception as e:
            return {"messages": [f"错误：知识点分析初始化失败 - {str(e)}"]}
            
    def analyze_point(self, state: TeachingState) -> TeachingState:
        """分析单个类型的知识点"""
        start_time = time.time()
        point_type = state.get("point_type", "")  # 先获取point_type，避免在异常处理中未定义
        try:
            # 从状态中获取参数
            content = {
                "textbook_content": state.get("content", {}),
                "toc_content": state.get("toc_content", ""),  # 直接获取toc_content，不需要[-1]
                "units": state.get("units", []),  # 直接获取units，不需要[-1]
                "unit_count": state.get("unit_count", 0)  # 直接获取unit_count，不需要[-1]
            }
            objectives = state.get("objectives", {})
            grade = state.get("grade", "")
            subject = state.get("subject", "")
            
            # 调用知识点分析函数
            result = analyze_point_type(content, objectives, grade, subject, point_type)
            
            elapsed_time = time.time() - start_time
            print(f"{point_type}知识点分析完成，耗时：{elapsed_time:.2f}秒")
            return {
                "messages": [f"{point_type}知识点分析完成"],
                **result  # 这里会添加 {point_type}_points 到状态中
            }
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"错误：{point_type}知识点分析失败 - {str(e)}")
            print(f"失败耗时：{elapsed_time:.2f}秒")
            return {"messages": [f"错误：{point_type}知识点分析失败 - {str(e)}"]}
            
    def merge_knowledge(self, state: TeachingState) -> TeachingState:
        """合并知识点分析结果 - Reduce阶段"""
        try:
            print("\n=== 合并知识点分析结果 ===")
            
            # 从状态中获取各类知识点
            result = ""
            point_types = ["basic", "key", "difficult"]
            
            for point_type in point_types:
                points = state.get(f"{point_type}_points", [])
                if points:
                    from my_agent.agents.knowledge_agent import get_point_config
                    config = get_point_config(point_type)
                    result += f"### {config['title']}\n\n"
                    for point in points:
                        result += point.get("content", "") + "\n\n"
            
            return {
                "messages": ["知识点分析完成"],
                "knowledge_points": [result],
                "textbook_content": [state["textbook_content"][-1]],
                "objectives": [state["objectives"][-1]],
                "grade": [state["grade"][-1]],
                "subject": [state["subject"][-1]],
                "total_hours": [state["total_hours"][-1]]
            }
        except Exception as e:
            return {"messages": [f"错误：合并知识点分析结果失败 - {str(e)}"]}
            
    def design_activities(self, state: TeachingState) -> TeachingState:
        """设计教学活动"""
        start_time = time.time()
        try:
            print("\n=== 设计教学活动 ===")
            
            # 调用活动代理
            result = design_activities(
                state["knowledge_points"][-1] if state["knowledge_points"] else {},
                state["total_hours"][-1] if state["total_hours"] else 0,
                state["grade"][-1] if state["grade"] else "7年级",
                state["subject"][-1] if state["subject"] else "语文"
            )
            elapsed_time = time.time() - start_time
            print(f"教学活动设计完成，耗时：{elapsed_time:.2f}秒")
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
            elapsed_time = time.time() - start_time
            print(f"错误：设计教学活动失败 - {str(e)}")
            print(f"失败耗时：{elapsed_time:.2f}秒")
            return {"messages": [f"错误：设计教学活动失败 - {str(e)}"]}
            
    def create_assessment(self, state: TeachingState) -> TeachingState:
        """创建评估方案"""
        start_time = time.time()
        try:
            print("\n=== 创建评估方案 ===")
            
            # 调用评估代理
            result = create_assessment(
                state["objectives"][-1] if state["objectives"] else {},
                state["knowledge_points"][-1] if state["knowledge_points"] else {},
                state["grade"][-1] if state["grade"] else "7年级",
                state["subject"][-1] if state["subject"] else "语文"
            )
            elapsed_time = time.time() - start_time
            print(f"评估方案创建完成，耗时：{elapsed_time:.2f}秒")
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
            elapsed_time = time.time() - start_time
            print(f"错误：创建评估方案失败 - {str(e)}")
            print(f"失败耗时：{elapsed_time:.2f}秒")
            return {"messages": [f"错误：创建评估方案失败 - {str(e)}"]}
            
    def save_output(self, state: TeachingState) -> TeachingState:
        """保存输出"""
        try:
            print("\n=== 保存输出 ===")
            
            # 确保所有必要的状态都存在
            required_fields = ["objectives", "knowledge_points", "activities", "assessment", "grade", "subject"]
            for field in required_fields:
                if field not in state or not state[field]:
                    raise ValueError(f"缺少必要的状态字段: {field}")
            
            # 获取课程名称和教材名称
            subject = state["subject"][-1]
            textbook_content = state["textbook_content"][-1] if state["textbook_content"] else {}
            textbook_name = textbook_content.get("title", "").replace(".pdf", "")  # 从PDF文件名中提取教材名称
            
            # 合并所有输出内容
            output = f"""# {textbook_name if textbook_name else subject}教学大纲

## 一、教学目标
{state["objectives"][-1]}

## 二、知识点分析
{state["knowledge_points"][-1]}

## 三、教学活动
{state["activities"][-1]}

## 四、评估方案
{state["assessment"][-1]}
"""
            
            # 保存到文件
            save_lesson_plan_to_md(output, subject, textbook_name)
            
            return {
                "messages": ["教学大纲已保存"],
                "objectives": [state["objectives"][-1]],
                "knowledge_points": [state["knowledge_points"][-1]],
                "activities": [state["activities"][-1]],
                "assessment": [state["assessment"][-1]],
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