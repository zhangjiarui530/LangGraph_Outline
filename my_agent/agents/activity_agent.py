from typing import Dict, Any, List, Annotated, TypedDict
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
import operator
import json
import time

# 定义教学活动子图的状态类型
class ActivityState(TypedDict):
    """教学活动状态"""
    knowledge_points: Dict[str, Any]  # 知识点内容
    total_hours: int  # 总课时
    grade: str  # 年级
    subject: str  # 学科
    activities: Annotated[List[Dict[str, Any]], operator.add]  # 教学活动
    messages: Annotated[List[str], operator.add]  # 消息列表

def create_activity_subgraph() -> StateGraph:
    """创建教学活动子图"""
    # 创建子图构建器
    graph = StateGraph(ActivityState)
    
    def start_activities(state: ActivityState) -> Dict[str, Any]:
        """开始设计教学活动"""
        print("\n=== 开始设计教学活动 ===")
        return state
    
    # 添加起始节点
    graph.add_node("start_activities", start_activities)
    
    def design_activities_node(state: ActivityState) -> Dict[str, Any]:
        """设计教学活动节点"""
        start_time = time.time()
        try:            
            # 获取最新的状态值，不使用列表
            total_hours = state['total_hours'][0]
            knowledge_points = state['knowledge_points']
            grade = state['grade']
            subject = state['subject']
            
            print(f"总课时: {total_hours}")
            
            # 计算各类活动的课时分配
            basic_hours = total_hours * 0.3  # 基础知识讲授
            skill_hours = total_hours * 0.3  # 技能训练
            practice_hours = total_hours * 0.2  # 实践活动
            discussion_hours = total_hours * 0.1  # 讨论交流
            assessment_hours = total_hours * 0.1  # 剩余用于测评反馈
            
            prompt = f"""作为一名资深的{subject}教师，请仔细阅读教材知识点内容，设计教学活动。

请首先分析教材的以下几个方面：
1. 教材内容的编排特点
2. 各单元活动的设计思路
3. 教材中的练习和实践活动
4. 教材提供的拓展资源

然后基于以上分析，设计教学活动。要求：
1. 输出采用markdown格式，结构清晰，层次分明，全部使用中文
2. 教学活动设计应包含以下部分：

### 活动1：基础知识学习

[此处结合教材内容，详细说明活动设计，包含：
- **活动名称**：与教材内容相关的具体活动名称
- **对应章节**：该活动对应的教材章节
- **活动类型**：讲授/讨论/练习/实践
- **课时安排**：具体课时数
- **教学内容**：与教材内容直接对应的具体教学内容
- **教学目标**：2-3个与教材内容相关的具体目标
- **重难点**：基于教材内容的2-3个教学重点和难点
- **教学方法**：针对教材内容的具体教学方法
- **学生活动**：学生在课堂上的具体学习活动
- **预期效果**：2-3个与教材内容相关的具体预期效果
- **课后作业**：基于教材内容的具体作业设计
- **拓展活动**：结合教材资源的2-3个拓展活动建议]

[按照上述格式设计8-10个教学活动，每个活动都要与教材的具体章节和知识点对应]

### 课时分配表

- **基础知识讲授**：{basic_hours}课时
- **技能训练**：{skill_hours}课时
- **实践活动**：{practice_hours}课时
- **讨论交流**：{discussion_hours}课时
- **测评反馈**：{assessment_hours}课时

注意事项：
1. 每个活动都要明确指出与教材内容的对应关系
2. 活动设计要与知识点和教学目标相对应
3. 活动的难度要循序渐进，符合{grade}学生的认知规律
4. 教学方法要多样化，注重学生的参与度
5. 课后作业和拓展活动要紧密结合教材内容

知识点内容如下：
{knowledge_points}
"""
            
            # 调用LLM
            llm_config = get_llm()
            response = llm_config.client.chat.completions.create(
                model=llm_config.model,
                temperature=llm_config.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.choices[0].message.content
            elapsed_time = time.time() - start_time
            print(f"教学活动设计完成，耗时：{elapsed_time:.2f}秒")
            
            return {
                "messages": ["教学活动设计完成"],
                "activities": [result]  # 直接返回字符串，不包装在字典中
            }
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"错误：设计教学活动失败 - {str(e)}")
            print(f"失败耗时：{elapsed_time:.2f}秒")
            return {"messages": [f"错误：设计教学活动失败 - {str(e)}"]}
    
    # 添加节点
    graph.add_node("design_activities", design_activities_node)
    
    # 添加边
    graph.add_edge(START, "start_activities")
    graph.add_edge("start_activities", "design_activities")
    graph.add_edge("design_activities", END)
    
    return graph.compile()
