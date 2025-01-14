from typing import Dict, Any, List, Annotated, TypedDict
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
import operator
import json
import time
from langchain_core.callbacks import StreamingStdOutCallbackHandler

# 定义教学目标子图的状态类型
class ObjectiveState(TypedDict):
    """教学目标状态"""
    textbook_content: Dict[str, Any]  # 教材内容
    total_hours: int  # 总课时
    grade: str  # 年级
    subject: str  # 学科
    toc_content: str  # 目录内容
    units: List[str]  # 单元列表
    unit_count: int  # 单元数量
    has_toc: bool  # 是否包含目录
    objectives: Annotated[List[Dict[str, Any]], operator.add]  # 所有目标
    messages: Annotated[List[str], operator.add]  # 消息列表
    objective_type: str  # 目标类型
    objective_count: int  # 目标数量

def create_objective_subgraph() -> StateGraph:
    """创建教学目标子图"""
    # 创建子图构建器
    graph = StateGraph(ObjectiveState)
    
    # 定义子图节点函数
    def prepare_objectives(state: ObjectiveState) -> Dict[str, Any]:
        """准备目标生成的初始状态"""
        print("\n=== 开始生成教学目标 ===")
        unit_count = state["unit_count"][0] if isinstance(state["unit_count"], list) else state["unit_count"]
        return {
            "messages": ["开始生成教学目标"],
            "objective_types": [
                {"type": "知识与技能", "count": max(1, unit_count)},
                {"type": "过程与方法", "count": max(1, (unit_count + 1) // 2)},
                {"type": "情感态度与价值观", "count": max(1, (unit_count + 1) // 2)},
                # {"type": "核心素养", "count": max(1, (unit_count + 1) // 2)}
            ]
        }

    def continue_to_objectives(state: ObjectiveState) -> List[Send]:
        """分发到不同类型的目标生成节点"""
        objective_types = state.get("objective_types", [])
        return [
            Send("generate_objective", {
                **state,
                "objective_type": obj["type"],
                "objective_count": obj["count"]
            })
            for obj in objective_types
        ]

    def generate_objective(state: ObjectiveState) -> Dict[str, Any]:
        """生成特定类型的教学目标"""
        start_time = time.time()
        try:            
            # 构建提示
            prompt = f"""作为{state['subject']}教师，请基于教材目录设计{state['objective_type']}目标。

要求：
1. 生成{state['objective_count']}个目标，每个章节或单元都要有所体现
2. 每个目标用序号标注
3. 目标要简洁明确，突出重点
4. 符合{state['grade']}学生认知水平
5. 体现{state['subject']}学科特点

教材目录：
```text
{state['toc_content']}
```
"""
            
            # 调用LLM
            llm_config = get_llm()
            
            # 添加流式输出回调
            callbacks = [StreamingStdOutCallbackHandler()]
            
            print(f"\n正在生成{state['objective_type']}目标...")
            response = llm_config.client.chat.completions.create(
                model=llm_config.model,
                messages=[
                    {"role": "system", "content": f"你是{state['subject']}教师，请设计教学目标。"},
                    {"role": "user", "content": prompt}
                ],
                stream=True  # 启用流式输出
            )
            
            # 收集流式输出的内容
            collected_content = []
            print("\n生成内容：")
            print("-" * 50)
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    collected_content.append(content)
            print("\n" + "-" * 50)
            
            result = "".join(collected_content)
            elapsed_time = time.time() - start_time
            print(f"\n{state['objective_type']}目标生成完成，耗时：{elapsed_time:.2f}秒")
            
            return {
                "messages": [f"{state['objective_type']}目标生成完成"],
                "objectives": [{"type": state["objective_type"], "content": result}]
            }
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"错误：生成{state['objective_type']}目标失败 - {str(e)}")
            print(f"失败耗时：{elapsed_time:.2f}秒")
            return {"messages": [f"错误：生成{state['objective_type']}目标失败 - {str(e)}"]}

    def merge_objectives(state: ObjectiveState) -> Dict[str, Any]:
        """合并所有类型的教学目标"""
        try:
            print("\n=== 合并教学目标 ===")
            
            # 从状态中获取目标
            result = ""
            # type_order = ["知识与技能", "过程与方法", "情感态度与价值观", "核心素养"]
            type_order = ["知识与技能", "过程与方法", "情感态度与价值观"]
            objectives = state.get("objectives", [])
            
            for obj_type in type_order:
                type_objectives = [obj for obj in objectives if obj.get("type") == obj_type]
                if type_objectives:
                    result += f"### {obj_type}目标\n\n"
                    for obj in type_objectives:
                        if isinstance(obj, dict) and "content" in obj:
                            result += obj["content"] + "\n\n"
            
            print(f"构建的教学目标内容长度: {len(result)}")
            
            # 返回合并后的结果
            return {
                "messages": ["教学目标合并完成"],
                "objectives": [result]  # 直接返回字符串，不包装在字典中
            }
            
        except Exception as e:
            print(f"合并教学目标时出错: {str(e)}")
            return {"messages": [f"错误：合并教学目标失败 - {str(e)}"]}

    # 添加节点
    graph.add_node("prepare", prepare_objectives)
    graph.add_node("generate_objective", generate_objective)
    graph.add_node("merge_objectives", merge_objectives)
    
    # 添加边
    graph.add_edge(START, "prepare")
    graph.add_conditional_edges("prepare", continue_to_objectives, ["generate_objective"])
    graph.add_edge("generate_objective", "merge_objectives")
    graph.add_edge("merge_objectives", END)
    
    return graph.compile()