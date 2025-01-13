from typing import Dict, Any, List, Annotated, TypedDict
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from pydantic import BaseModel
from my_agent.config import get_llm
import operator
import json
import time

# 定义知识点子图的状态类型
class KnowledgeState(TypedDict):
    """知识点分析状态"""
    textbook_content: Dict[str, Any]  # 教材内容
    objectives: Dict[str, Any]  # 教学目标
    grade: str  # 年级
    subject: str  # 学科
    point_type: str  # 知识点类型
    toc_content: str  # 目录内容
    units: List[str]  # 单元列表
    unit_count: int  # 单元数量
    basic_points: Annotated[List[Dict[str, Any]], operator.add]
    key_points: Annotated[List[Dict[str, Any]], operator.add]
    difficult_points: Annotated[List[Dict[str, Any]], operator.add]
    knowledge_points: Annotated[List[Dict[str, Any]], operator.add]  # 合并后的知识点
    messages: Annotated[List[str], operator.add]

# 定义结构化输出模型
class KnowledgePoint(BaseModel):
    """知识点结构"""
    content: str

def get_point_config(point_type: str) -> Dict[str, Any]:
    """获取知识点类型的配置"""
    return {
        "basic": {
            "title": "基础知识点",
            "count": "6-10个",
            "difficulty": "简单/中等/困难",
            "importance": "核心/重要/一般",
            "suggestion_name": "教学建议"
        },
        "key": {
            "title": "重点知识点",
            "count": "4-6个",
            "difficulty": "中等/困难",
            "importance": "核心/重要",
            "suggestion_name": "教学建议"
        },
        "difficult": {
            "title": "难点知识点",
            "count": "3-4个",
            "difficulty": "困难",
            "importance": "核心/重要",
            "suggestion_name": "突破建议"
        }
    }[point_type]

def analyze_point_type(textbook_content: Dict[str, Any], objectives: Dict[str, Any], grade: str, subject: str, point_type: str) -> Dict[str, Any]:
    """分析单个类型的知识点"""
    start_time = time.time()
    try:
        llm_config = get_llm()
        config = get_point_config(point_type)
        
        # 获取目录内容和单元信息
        toc_content = textbook_content.get("toc_content", "")
        units = textbook_content.get("units", [])
        content = textbook_content.get("textbook_content", {})
        
        # 如果没有目录内容，使用完整内容
        if not toc_content:
            print("未找到目录内容，将使用完整内容进行分析...")
            toc_content = json.dumps(content, ensure_ascii=False, indent=2)
        
        # 构建单元知识点提示
        unit_points_prompt = ""
        if units:
            unit_points_prompt = "\n单元知识点要求：\n"
            for i, unit in enumerate(units, 1):
                unit_points_prompt += f"{i}. {unit}的知识点应该体现该单元的特点和重点\n"
        
        prompt = f"""作为一名资深的{subject}教师，请分析教材的{config['title']}。

分析步骤：
1. 通读教材目录和教学目标，理解整体知识体系
2. 根据教材特点，识别{config['title']}的分布规律
3. 结合教学目标和学生认知特点，筛选合适的知识点
4. 按照知识体系的内在逻辑组织知识点

请列出{config['count']}{config['title']}。要求：
1. 知识点要覆盖教材主要章节，体现知识体系的完整性
2. 每个知识点包含以下要素：
   - 知识内容：具体说明知识点的内容和范围
   - 所在章节：
   - 难度：{config['difficulty']}中选一个
   - 重要程度：{config['importance']}中选一个
   - 前置知识：列出必要的前置知识，注明对应章节
   - {config['suggestion_name']}：1-2点具体建议
3. 知识点数量要严格控制在{config['count']}

格式示例：
1. 直角三角形的定义与性质
   章节：第二章第1节
   难度：中等
   重要程度：核心
   前置知识：平面图形基础知识（第一章）、角的概念（第一章第2节）
   教学建议：
   - 通过实物演示理解直角特征
   - 用折纸活动体验直角三角形的性质

注意：
1. 知识点要体现教材的整体性和系统性，避免仅关注前几章
2. 知识点之间要体现内在联系和递进关系
3. 知识点要符合{grade}学生的认知水平
4. 建议要具体、可操作，避免空泛

{unit_points_prompt}

教材目录和教学目标如下：
{objectives}
{toc_content}
"""
        
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": f"你是一个专业的{subject}教师，擅长分析教材{config['title']}。请从整体角度分析教材，确保知识点覆盖全面，体系完整。输出格式要简约、清晰、层次分明。"},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content
        elapsed_time = time.time() - start_time
        print(f"{config['title']}分析完成，耗时：{elapsed_time:.2f}秒")
        return {f"{point_type}_points": [{"content": result}]}
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"错误：{config['title']}分析失败 - {str(e)}")
        print(f"失败耗时：{elapsed_time:.2f}秒")
        return {f"{point_type}_points": []}

def create_knowledge_subgraph() -> StateGraph:
    """创建知识点分析子图"""
    # 创建子图构建器
    graph = StateGraph(KnowledgeState)
    print("\n=== 开始知识点分析 ===")
    
    # 定义子图节点函数
    def analyze_point(state: KnowledgeState) -> Dict[str, Any]:
        """分析单个类型的知识点"""
        try:
            point_type = state["point_type"]
            content = {
                "textbook_content": state["textbook_content"],
                "toc_content": state["toc_content"],
                "units": state["units"],
                "unit_count": state["unit_count"]
            }
            
            # 调用知识点分析函数
            result = analyze_point_type(content, state["objectives"], state["grade"], state["subject"], point_type)
            
            return {
                "messages": [f"{point_type}知识点分析完成"],
                **result  # 这里会添加 {point_type}_points 到状态中
            }
        except Exception as e:
            return {"messages": [f"错误：{point_type}知识点分析失败 - {str(e)}"]}
    
    def continue_to_points(state: KnowledgeState) -> List[Send]:
        """将状态分发到各个知识点分析节点"""
        point_types = ["basic", "key", "difficult"]
        return [
            Send("analyze_point", {
                "textbook_content": state["textbook_content"],
                "objectives": state["objectives"],
                "grade": state["grade"],
                "subject": state["subject"],
                "point_type": point_type,
                "toc_content": state["toc_content"],
                "units": state["units"],
                "unit_count": state["unit_count"],
                "basic_points": [],
                "key_points": [],
                "difficult_points": [],
                "knowledge_points": [],
                "messages": []
            })
            for point_type in point_types
        ]
    
    def merge_points(state: KnowledgeState) -> Dict[str, Any]:
        """合并知识点分析结果"""
        try:
            print("\n=== 合并知识点分析结果 ===")
            
            # 从状态中获取各类知识点
            result = ""
            point_types = ["basic", "key", "difficult"]
            
            for point_type in point_types:
                points = state.get(f"{point_type}_points", [])
                if points:
                    config = get_point_config(point_type)
                    result += f"### {config['title']}\n\n"
                    for point in points:
                        if isinstance(point, dict) and "content" in point:
                            result += point["content"] + "\n\n"
            
            print(f"构建的知识点内容长度: {len(result)}")
            
            # 返回合并后的结果
            return {
                "messages": ["知识点分析完成"],
                # "knowledge_points": [{"content": content}],
                "knowledge_points": [result],  # 直接返回字符串，不包装在字典中
                # "basic_points": state.get("basic_points", []),
                # "key_points": state.get("key_points", []),
                # "difficult_points": state.get("difficult_points", [])
            }
        except Exception as e:
            print(f"合并知识点时出错: {str(e)}")  # 添加错误信息
            return {"messages": [f"错误：合并知识点分析结果失败 - {str(e)}"]}
    
    # 添加节点
    graph.add_node("start_analysis", lambda x: x)  # 添加一个起始节点
    graph.add_node("analyze_point", analyze_point)
    graph.add_node("merge_points", merge_points)
    
    # 添加边
    graph.add_edge(START, "start_analysis")
    # 使用条件边来实现map操作
    graph.add_conditional_edges(
        "start_analysis",
        continue_to_points,
        ["analyze_point"]
    )
    # merge操作
    graph.add_edge("analyze_point", "merge_points")
    graph.add_edge("merge_points", END)
    
    return graph.compile()