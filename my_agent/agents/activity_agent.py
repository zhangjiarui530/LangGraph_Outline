from typing import Dict, Any, List, Annotated, TypedDict
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
import operator
import json
import time
from colorama import init, Fore, Style

# 预定义学科和年级特点
subject_features = {
    "语文": "注重语言积累、阅读理解、写作训练和口语交际",
    "数学": "强调概念理解、逻辑推理、解题能力和实际应用",
    "英语": "侧重听说读写全面发展、语言实践和文化理解",
    "物理": "突出实验探究、原理分析和生活应用",
    "化学": "重视实验操作、规律认知和应用实践",
    "生物": "关注观察记录、探究分析和实验技能",
    "历史": "注重史料解读、历史思维和价值判断",
    "地理": "强调地图技能、区域认知和综合思维",
    "政治": "侧重价值观培养、社会认知和实践体验"
}

grade_features = {
    "小学": "以趣味性和生活化为主，注重基础知识和良好习惯的培养",
    "初中": "以理解性和系统性为主，注重思维发展和学习方法的掌握",
    "高中": "以深度性和综合性为主，注重能力提升和学科素养的形成"
}

# 初始化colorama
init()

def print_header(text: str):
    """打印带颜色的标题"""
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}>>> {text}")
    print(f"{'='*50}{Style.RESET_ALL}")

def print_section(text: str):
    """打印带颜色的小节标题"""
    print(f"\n{Fore.GREEN}{'-'*40}")
    print(f">> {text}")
    print(f"{'-'*40}{Style.RESET_ALL}")

def print_success(text: str):
    """打印成功信息"""
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_error(text: str):
    """打印错误信息"""
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

def print_info(text: str):
    """打印普通信息"""
    print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")

def print_warning(text: str):
    """打印警告信息"""
    print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")

def print_progress(text: str):
    """打印进度信息"""
    print(f"{Fore.MAGENTA}→ {text}{Style.RESET_ALL}")

# 定义教学活动子图的状态类型
class ActivityState(TypedDict):
    """教学活动状态"""
    knowledge_points: Dict[str, Any]  # 知识点内容
    total_hours: int  # 总课时
    grade: str  # 年级
    subject: str  # 学科
    activities: Annotated[List[Dict[str, Any]], operator.add]  # 教学活动
    messages: Annotated[List[str], operator.add]  # 消息列表
    toc_content: str  # 目录内容

def create_activity_subgraph() -> StateGraph:
    """创建教学活动子图"""
    # 创建子图构建器
    graph = StateGraph(ActivityState)
    
    def start_activities(state: ActivityState) -> Dict[str, Any]:
        """开始设计教学活动"""
        print_header("开始设计教学活动")
        return state
    
    def generate_activity_names(state: ActivityState) -> Dict[str, Any]:
        """生成活动名称列表"""
        start_time = time.time()
        try:
            total_hours = state['total_hours'][0]
            knowledge_points = state['knowledge_points']
            grade = state['grade'][0] if isinstance(state['grade'], list) else state['grade']
            subject = state['subject'][0] if isinstance(state['subject'], list) else state['subject']
            toc_content = state['toc_content']
            
            print_section(f"正在为{grade}{subject}课程生成{total_hours}课时的教学活动名称")
            
            prompt = f"""作为一名资深的{subject}教师，根据知识点和目录内容，以单元为单位，请为{grade}{subject}课程设计{total_hours}课时的8-10个教学活动名称。

要求：
1. 活动名称要与教材内容直接对应
2. 每个活动名称要包含：活动名称、对应单元、活动类型（讲授/讨论/练习/实践）、建议课时数
3. 活动要覆盖教材主要章节
4. 活动难度要循序渐进，符合{grade}学生的认知特点
5. 活动类型要多样化，体现{subject}学科特色
6. 数量是8-10个，不用标号

根据{subject}学科特点：
- 语文：注重语言积累、阅读理解、写作训练和口语交际
- 数学：强调概念理解、逻辑推理、解题能力和实际应用
- 英语：侧重听说读写全面发展、语言实践和文化理解
- 物理：突出实验探究、原理分析和生活应用
- 化学：重视实验操作、规律认知和应用实践
- 生物：关注观察记录、探究分析和实验技能
- 历史：注重史料解读、历史思维和价值判断
- 地理：强调地图技能、区域认知和综合思维
- 政治：侧重价值观培养、社会认知和实践体验

根据{grade}学生特点：
- 小学：以趣味性和生活化为主，注重基础知识和良好习惯的培养
- 初中：以理解性和系统性为主，注重思维发展和学习方法的掌握
- 高中：以深度性和综合性为主，注重能力提升和学科素养的形成

格式示例(不需要标号)：
诗歌鉴赏入门 | 第一单元 | 讲授 | 2课时
古诗文朗读与品析 | 第二单元 | 实践 | 3课时

知识点内容如下：
{knowledge_points}

目录内容如下：
{toc_content}
"""
            
            llm_config = get_llm()
            print_progress("正在生成活动名称列表...")
            response = llm_config.client.chat.completions.create(
                model=llm_config.model,
                temperature=llm_config.temperature,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            
            collected_content = []
            print_section("活动名称列表")
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    collected_content.append(content)
            print("\n")
            
            result = "".join(collected_content)
            elapsed_time = time.time() - start_time
            print_success(f"活动名称列表生成完成，耗时：{elapsed_time:.2f}秒")
            
            # 解析活动列表
            activities = []
            for line in result.strip().split('\n'):
                if line.strip() and '|' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 4:
                        activities.append({
                            "name": parts[0],
                            "chapter": parts[1],
                            "type": parts[2],
                            "hours": parts[3],
                            "content": ""
                        })
            
            print_info(f"共生成 {len(activities)} 个教学活动")
            return {
                "messages": ["活动名称列表生成完成"],
                "activity_list": activities
            }
            
        except Exception as e:
            print_error(f"生成活动名称列表失败 - {str(e)}")
            return {"messages": [f"错误：生成活动名称列表失败 - {str(e)}"]}

    def continue_to_activities(state: ActivityState) -> List[Send]:
        """分发到各个活动的详细设计节点"""
        activities = state.get("activity_list", [])
        return [
            Send("design_activity_detail", {
                **state,
                "current_activity": activity
            })
            for activity in activities
        ]

    def design_activity_detail(state: ActivityState) -> Dict[str, Any]:
        """设计单个活动的详细内容"""
        start_time = time.time()
        try:
            activity = state["current_activity"]
            knowledge_points = state["knowledge_points"]
            grade = state["grade"][0] if isinstance(state["grade"], list) else state["grade"]
            subject = state["subject"][0] if isinstance(state["subject"], list) else state["subject"]
            toc_content = state["toc_content"]
            
            print_section(f"正在设计活动：{activity['name']}")
            
            prompt = f"""请基于以下内容设计教学活动：

1. 教材内容：
{toc_content}

2. 知识点：
{knowledge_points}

3. 学科特点：
{subject}学科注重{subject_features.get(subject, "")}

4. 学生特点：
{grade}学生{grade_features.get(grade, "")}

输出采用markdown格式，结构清晰，层次分明，全部使用中文
请按照以下格式设计教学活动：

- **对应章节**：{activity['chapter']}
- **活动类型**：{activity['type']}
- **课时安排**：{activity['hours']}
- **教学内容**：与教材内容直接对应的具体教学内容
- **教学目标**：1-3个与教材内容相关的具体目标
- **重难点**：基于教材内容的1-3个教学重点和难点
- **教学方法**：针对教材内容的具体教学方法
- **学生活动**：学生在课堂上的具体学习活动
- **预期效果**：1-3个与教材内容相关的具体预期效果
- **课后作业**：基于教材内容的具体作业设计
- **拓展活动**：结合教材资源的1-3个拓展活动建议


注意事项：
1. 活动设计要与教材具体章节和知识点直接对应
2. 难度要符合{grade}学生的认知水平
3. 教学方法要体现{subject}学科特点
4. 作业和拓展活动要紧密结合教材内容"""
            
            llm_config = get_llm()
            print_progress(f"正在生成活动设计内容...")
            response = llm_config.client.chat.completions.create(
                model=llm_config.model,
                temperature=llm_config.temperature,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            
            collected_content = []
            print_section("活动设计详情")
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    collected_content.append(content)
            print("\n")
            
            result = "".join(collected_content)
            activity["content"] = result
            
            elapsed_time = time.time() - start_time
            print_success(f"活动 {activity['name']} 设计完成，耗时：{elapsed_time:.2f}秒")
            
            return {
                "messages": [f"活动 {activity['name']} 设计完成"],
                "activities": [activity]
            }
            
        except Exception as e:
            print_error(f"设计活动详细内容失败 - {str(e)}")
            return {"messages": [f"错误：设计活动详细内容失败 - {str(e)}"]}

    def merge_activities(state: ActivityState) -> Dict[str, Any]:
        """合并所有活动的设计内容"""
        try:
            print_header("合并教学活动设计")
            
            # 计算课时分配
            total_hours = state['total_hours'][0]
            basic_hours = total_hours * 0.3
            skill_hours = total_hours * 0.3
            practice_hours = total_hours * 0.2
            discussion_hours = total_hours * 0.1
            assessment_hours = total_hours * 0.1
            
            # 合并所有活动
            result = """

### 课时分配

| 活动类型 | 课时数 | 占比 |
|----------|:------:|------|
| 基础知识讲授 | {:.1f} | 30% |
| 技能训练 | {:.1f} | 30% |
| 实践活动 | {:.1f} | 20% |
| 讨论交流 | {:.1f} | 10% |
| 测评反馈 | {:.1f} | 10% |

### 活动设计\n\n""".format(
                basic_hours, skill_hours, practice_hours, 
                discussion_hours, assessment_hours
            )
            
            # 添加活动详细内容
            # 使用集合去重，根据活动名称
            activities = state.get("activities", [])
            unique_activities = {activity["name"]: activity for activity in activities}.values()
            
            print_section("合并活动设计")
            for i, activity in enumerate(unique_activities, 1):
                print_progress(f"正在处理活动 {i}/{len(unique_activities)}: {activity['name']}")
                
                result += f"""#### 活动{i}：{activity['name']}

{activity['content']}

---\n\n"""
            
            print_success("教学活动设计合并完成")
            
            return {
                "messages": ["教学活动设计完成"],
                "activities": [result]
            }
            
        except Exception as e:
            print_error(f"合并教学活动设计失败: {str(e)}")
            return {"messages": [f"错误：合并教学活动设计失败 - {str(e)}"]}
    
    # 添加节点
    graph.add_node("start_activities", start_activities)
    graph.add_node("generate_activity_names", generate_activity_names)
    graph.add_node("design_activity_detail", design_activity_detail)
    graph.add_node("merge_activities", merge_activities)
    
    # 添加边
    graph.add_edge(START, "start_activities")
    graph.add_edge("start_activities", "generate_activity_names")
    graph.add_conditional_edges(
        "generate_activity_names",
        continue_to_activities,
        ["design_activity_detail"]
    )
    graph.add_edge("design_activity_detail", "merge_activities")
    graph.add_edge("merge_activities", END)
    
    return graph.compile()
