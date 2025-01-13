from typing import Dict, Any, List, Annotated, TypedDict
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
import operator
import json
import time

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
    objectives: Annotated[List[Dict[str, Any]], operator.add]
    messages: Annotated[List[str], operator.add]

def create_objective_subgraph() -> StateGraph:
    """创建教学目标子图"""
    # 创建子图构建器
    graph = StateGraph(ObjectiveState)
    print("\n=== 开始生成教学目标 ===")
    
    # 定义子图节点函数
    def generate_objectives_node(state: ObjectiveState) -> Dict[str, Any]:
        """生成教学目标节点"""
        start_time = time.time()
        try:
            print("\n=== 生成教学目标 ===")
            
            # 构建包含目录内容的字典
            content = {
                "textbook_content": state["textbook_content"],
                "toc_content": state["toc_content"],
                "units": state["units"],
                "unit_count": state["unit_count"]
            }
            result = design_objectives(
                content,
                state["total_hours"],
                state["grade"],
                state["subject"]
            )
                
            elapsed_time = time.time() - start_time
            print(f"教学目标生成完成，耗时：{elapsed_time:.2f}秒")
            return {
                "messages": ["教学目标生成完成"],
                "objectives": [result]
            }
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"错误：生成教学目标失败 - {str(e)}")
            print(f"失败耗时：{elapsed_time:.2f}秒")
            return {"messages": [f"错误：生成教学目标失败 - {str(e)}"]}
    
    # 添加节点
    graph.add_node("generate_objectives", generate_objectives_node)
    
    # 添加边
    graph.add_edge(START, "generate_objectives")
    graph.add_edge("generate_objectives", END)
    
    return graph.compile()

def design_objectives(content: Dict[str, Any], total_hours: int, grade: str, subject: str) -> str:
    """基于目录设计教学目标"""
    try:
        # 获取目录内容
        toc_content = content.get("toc_content", "")
        # print(f"目录内容：{toc_content}")
        # 如果是列表，取第一个元素
        if isinstance(toc_content, list):
            toc_content = toc_content[0] if toc_content else ""
            
        # 如果没有目录内容，使用完整内容
        if not toc_content:
            print("未找到目录内容，将使用完整内容进行分析...")
            toc_content = json.dumps(content, ensure_ascii=False, indent=2)
        else:
            print(f"成功获取目录内容，长度：{len(toc_content)}")
        
        # 获取单元信息
        units = content.get("units", [])
        unit_count = content.get("unit_count", 0)[0] # 直接使用单元列表长度
        print(f"单元数量：{unit_count}")
        
        # 根据单元数调整目标数量，尽量保持一个单元一个目标
        knowledge_goals = max(1, unit_count)  # 至少1个
        process_goals = max(1, (unit_count + 1) // 2)  # 至少1个
        attitude_goals = max(1, (unit_count + 1) // 2)  # 至少1个
        competency_goals = max(1, (unit_count + 1) // 2)  # 至少1个
        
        # 获取LLM配置
        llm_config = get_llm()
        
        # 构建单元目标提示
        unit_goals_prompt = ""
        if units:
            unit_goals_prompt = "\n单元目标要求：\n"
            for i, unit in enumerate(units, 1):
                unit_goals_prompt += f"{i}. {unit}的教学目标应该体现该单元的特点和重点\n"
        
        prompt = f"""作为{subject}教师，请基于教材目录设计总课时为{total_hours}课时的教学目标。

请分析目录内容，设计以下四个维度的教学目标：

## 一、知识与技能目标（{knowledge_goals}个）
> 每个单元列出1个核心知识目标，描述学生应掌握的关键知识点。请用序号标注。

## 二、过程与方法目标（{process_goals}个）
> 列出培养的关键能力，每2个单元对应1个目标。请用序号标注。

## 三、情感态度与价值观目标（{attitude_goals}个）
> 列出培养的核心情感态度，每2个单元对应1个目标。请用序号标注。

## 四、核心素养目标（{competency_goals}个）
> 列出培养的核心素养，每2个单元对应1个目标。请用序号标注。

### 设计要求
1. 目标表述要简洁明确，突出重点
2. 符合{grade}学生认知水平
3. 体现{subject}学科特点
4. 确保在{total_hours}课时内可完成

{unit_goals_prompt}

### 教材目录
```text
{toc_content}
```
"""
        
        print("\n=== 基于目录设计教学目标 ===")
        print("调用LLM设计目标...")
        
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": f"你是{subject}教师，请简明扼要地设计教学目标。"},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content
        print("目标设计完成")
        return result
        
    except Exception as e:
        print(f"错误：设计教学目标失败 - {str(e)}")
        raise ValueError(f"设计教学目标失败: {str(e)}")