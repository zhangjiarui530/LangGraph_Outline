from typing import Dict, Any, List
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
import json

def design_activities(knowledge_points: Dict[str, Any], total_hours: int, grade: str, subject: str) -> str:
    """设计教学活动"""
    llm = get_llm()
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

- **基础知识讲授**：{total_hours * 0.3}课时
- **技能训练**：{total_hours * 0.3}课时
- **实践活动**：{total_hours * 0.2}课时
- **讨论交流**：{total_hours * 0.1}课时
- **测评反馈**：{total_hours * 0.1}课时

注意事项：
1. 每个活动都要明确指出与教材内容的对应关系
2. 活动设计要与知识点和教学目标相对应
3. 活动的难度要循序渐进，符合{grade}学生的认知规律
4. 教学方法要多样化，注重学生的参与度
5. 课后作业和拓展活动要紧密结合教材内容

知识点内容如下：
{knowledge_points}
"""
    
    try:
        response = llm.client.chat.completions.create(
            model=llm.model,
            temperature=llm.temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise LLMGenerationError(f"生成教学活动失败: {str(e)}")

def validate_activities(activities: Dict[str, Any], total_hours: int) -> None:
    """
    验证教学活动的格式和内容
    
    Args:
        activities: 教学活动字典
        total_hours: 总课时数
        
    Raises:
        ValueError: 如果格式或内容不符合要求
    """
    # 检查基本结构
    if not isinstance(activities, dict):
        raise ValueError("教学活动必须是字典类型")
        
    if "teaching_activities" not in activities:
        raise ValueError("缺少teaching_activities字段")
        
    if "time_allocation" not in activities:
        raise ValueError("缺少time_allocation字段")
        
    if "resources_needed" not in activities:
        raise ValueError("缺少resources_needed字段")
        
    if "activity_sequence" not in activities:
        raise ValueError("缺少activity_sequence字段")
        
    # 检查教学活动
    acts = activities["teaching_activities"]
    if not isinstance(acts, list):
        raise ValueError("teaching_activities必须是列表类型")
    if not acts:
        raise ValueError("teaching_activities不能为空")
        
    # 检查每个活动的必要字段
    for act in acts:
        if not isinstance(act, dict):
            raise ValueError("活动必须是字典类型")
        for key in ["phase", "name", "description", "duration", "resources", "knowledge_points"]:
            if key not in act:
                raise ValueError(f"活动缺少{key}字段")
                
    # 检查课时分配
    time = activities["time_allocation"]
    if not isinstance(time, dict):
        raise ValueError("time_allocation必须是字典类型")
    for key in ["knowledge", "skill", "practice", "discussion", "assessment"]:
        if key not in time:
            raise ValueError(f"课时分配缺少{key}字段")
            
    # 检查总课时是否匹配
    total = sum(float(act["duration"]) for act in acts)
    if abs(total - total_hours) > 0.1:  # 允许0.1的误差
        raise ValueError(f"总课时不匹配：计划{total_hours}，实际{total}")
        
    # 检查资源
    res = activities["resources_needed"]
    if not isinstance(res, dict):
        raise ValueError("resources_needed必须是字典类型")
    for key in ["hardware", "software", "materials"]:
        if key not in res:
            raise ValueError(f"资源列表缺少{key}字段")
        if not isinstance(res[key], list):
            raise ValueError(f"{key}必须是列表类型")
            
    # 检查活动序列
    seq = activities["activity_sequence"]
    if not isinstance(seq, dict):
        raise ValueError("activity_sequence必须是字典类型")
    for key in ["prerequisites", "parallel", "dependencies"]:
        if key not in seq:
            raise ValueError(f"活动序列缺少{key}字段")
        if key != "dependencies" and not isinstance(seq[key], list):
            raise ValueError(f"{key}必须是列表类型")
    
    # 检查依赖关系
    deps = seq["dependencies"]
    if not isinstance(deps, list):
        raise ValueError("dependencies必须是列表类型")
    for dep in deps:
        if not isinstance(dep, dict):
            raise ValueError("依赖项必须是字典类型")
        if "activity" not in dep or "depends_on" not in dep:
            raise ValueError("依赖项缺少activity或depends_on字段")
        if not isinstance(dep["depends_on"], list):
            raise ValueError("depends_on必须是列表类型")
