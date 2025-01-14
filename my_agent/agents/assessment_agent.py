from typing import Dict, Any, List, Annotated, TypedDict
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
import operator
import json
import time

# 定义评估子图的状态类型
class AssessmentState(TypedDict):
    """评估状态"""
    objectives: Dict[str, Any]  # 教学目标
    knowledge_points: Dict[str, Any]  # 知识点
    grade: str  # 年级
    subject: str  # 学科
    assessment: Annotated[List[Dict[str, Any]], operator.add]  # 评估方案
    messages: Annotated[List[str], operator.add]  # 消息列表

def create_assessment_subgraph() -> StateGraph:
    """创建评估子图"""
    # 创建子图构建器
    graph = StateGraph(AssessmentState)
    
    def start_assessment(state: AssessmentState) -> Dict[str, Any]:
        """开始创建评估方案"""
        print("\n=== 开始创建评估方案 ===")
        return state
    
    # 添加起始节点
    graph.add_node("start_assessment", start_assessment)
    
    def create_assessment_node(state: AssessmentState) -> Dict[str, Any]:
        """创建评估方案节点"""
        start_time = time.time()
        try:            
            # 获取最新的状态值，不使用列表
            objectives = state['objectives']
            knowledge_points = state['knowledge_points']
            grade = state['grade']
            subject = state['subject']
            
            prompt = f"""作为一名资深的{subject}教师，请仔细阅读教材内容、教学目标和知识点，设计评估方案，方案尽可能符合现实教学需求。

请首先分析教材的以下几个方面：
1. 教材的考核要点分布
2. 各单元的重难点设置
3. 教材提供的练习和测试
4. 学科核心素养的考查要求

然后基于以上分析，设计评估方案。要求：
1. 输出采用markdown格式，结构清晰，层次分明，全部使用中文
2. 评估方案应包含以下部分：

### 形成性评价

| 评价项目 | 对应章节 | 评价方式 | 分值设置 | 评价时间 | 评价标准 | 实施要点 |
|---------|---------|---------|---------|---------|---------|---------|
[此处结合教材内容，列出6-10个形成性评价项目，每行包含：
- 评价项目：与教材内容直接相关的具体评价项目
- 对应章节：该评价项目对应的教材章节
- 评价方式：具体的评价方法
- 分值设置：具体的分值分配
- 评价时间：在教学过程中的具体实施时间
- 评价标准：2-3个基于教材内容的具体评价标准
- 实施要点：评价过程中需要注意的具体问题]

### 终结性评价

| 评价项目 | 考查范围 | 评价方式 | 分值设置 | 评价时间 | 评价标准 | 实施要点 |
|---------|---------|---------|---------|---------|---------|---------|
[此处结合教材重点内容，列出2-3个终结性评价项目，每行包含：
- 评价项目：与教材重点内容相关的具体评价项目
- 考查范围：具体对应的教材章节和内容，尽可能的符合现实教学需求
- 评价方式：具体的评价方法
- 分值设置：具体的分值分配
- 评价时间：具体的评价时间安排
- 评价标准：2-3个基于教材内容的具体评价标准
- 实施要点：评价过程中需要注意的具体问题]

### 评价权重分配

| 评价类型 | 总分值 | 评价项目 | 分值占比 |
|---------|--------|---------|---------|
| 形成性评价 | 60% | 课堂表现 | 20% |
|  |  | 作业完成 | 20% |
|  |  | 实践活动 | 20% |
| 终结性评价 | 40% | 期中测试 | 15% |
|  |  | 期末考试 | 25% |

### 反馈与改进机制

| 反馈方式 | 适用内容 | 反馈时机 | 实施方法 |
|---------|---------|---------|---------|
[此处结合教材特点，列出4种反馈方式，每行包含：
- 反馈方式：具体的反馈方式描述
- 适用内容：该反馈方式适用的教材内容
- 反馈时机：在教学过程中的具体反馈时间
- 实施方法：如何具体实施这种反馈]

注意事项：
1. 每个评价项目都要与教材内容直接对应
2. 评价标准要具体、可测量、可操作
3. 评价方式要多样化，注重过程性评价
4. 反馈要及时、有效，促进学生改进
5. 所有评价活动要符合{grade}学生的认知水平
6. 评价内容要覆盖教材的重点、难点

教学目标和知识点如下：
{objectives}
{knowledge_points}
"""
            
            # 调用LLM
            llm_config = get_llm()
            print("\n正在创建评估方案...")
            response = llm_config.client.chat.completions.create(
                model=llm_config.model,
                temperature=llm_config.temperature,
                messages=[{"role": "user", "content": prompt}],
                stream=True  # 启用流式输出
            )
            
            # 收集流式输出的内容
            collected_content = []
            print("\n评估方案内容：")
            print("-" * 50)
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    collected_content.append(content)
            print("\n" + "-" * 50)
            
            result = "".join(collected_content)
            elapsed_time = time.time() - start_time
            print(f"\n评估方案创建完成，耗时：{elapsed_time:.2f}秒")
            
            return {
                "messages": ["评估方案创建完成"],
                "assessment": [result]  # 直接返回字符串，不包装在字典中
            }
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"错误：创建评估方案失败 - {str(e)}")
            print(f"失败耗时：{elapsed_time:.2f}秒")
            return {"messages": [f"错误：创建评估方案失败 - {str(e)}"]}
    
    # 添加节点
    graph.add_node("create_assessment", create_assessment_node)
    
    # 添加边
    graph.add_edge(START, "start_assessment")
    graph.add_edge("start_assessment", "create_assessment")
    graph.add_edge("create_assessment", END)
    
    return graph.compile()
