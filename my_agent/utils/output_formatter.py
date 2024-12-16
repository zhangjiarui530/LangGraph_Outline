from .types import AgentState

def format_final_output(state: AgentState) -> str:
    """格式化最终输出"""
    # 格式化知识点列表
    knowledge_points_str = ""
    for kp in state.get("knowledge_points", []):
        knowledge_points_str += f"- {kp}\n"

    # 格式化教学活动列表
    activities_str = ""
    for activity in state.get("teaching_activities", []):
        activities_str += f"- {activity['activity']}\n"

    # 格式化课时分配
    hours_str = ""
    for section, hours in state.get("hours_per_section", {}).items():
        hours_str += f"- {section}：{hours}课时\n"

    # 构建最终输出
    output = f"""# 教学大纲

## 1. 教学目标
{state.get('teaching_objectives', '')}

## 2. 教学内容与课时安排
### 总课时数：{state.get('total_hours', 0)}课时

### 课时分配：
{hours_str}

### 知识点：
{knowledge_points_str}

## 3. 教学活动：
{activities_str}

## 4. 评估方案：
{state.get('assessment_plan', {}).get('plan', '')}
"""
    return output 