<<<<<<< HEAD
from typing import Dict, Any, List
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
from my_agent.utils.types import AgentState
import json

def design_activities(knowledge_points: Dict[str, Any], total_hours: int) -> Dict[str, Any]:
    """设计教学活动"""
    try:
        # 验证输入
        if not isinstance(knowledge_points, dict):
            raise ValueError(f"知识点格式错误: {type(knowledge_points)}")
            
        if not isinstance(total_hours, (int, float)) or total_hours <= 0:
            raise ValueError(f"总课时格式错误: {total_hours}")
            
        # 获取LLM配置
        llm_config = get_llm()
        
        # 构建提示词
        points_json = json.dumps(knowledge_points, indent=2, ensure_ascii=False)
        template = """作为教学设计专家，请基于以下知识点设计教学活动。总课时为{hours}学时（每课时45分钟）。

知识点：
{points}

请设计教学活动，要求：
1. 每个活动的时长必须是以下选项之一：
   - 15分钟（小节课）
   - 30分钟（半节课）
   - 45分钟（一节课）
   - 90分钟（两节连堂课）
2. 所有活动的总时长必须等于{total_minutes}分钟
3. 每个知识点都要有对应的教学活动
4. 活动设计要合理，包含导入、发展、总结等环节

请按以下格式输出：
{{
    "time_allocation": {{
        "knowledge": "知识讲解课时数",
        "skill": "技能训练课时数",
        "practice": "实践课时数",
        "discussion": "讨论课时数",
        "assessment": "评估课时数"
    }},
    "activities": [
        {{
            "activity": {{
                "title": "活动标题",
                "duration": "活动时长（分钟）",
                "教学重点": "教学重点内容",
                "教学方法": "使用的教学方法",
                "教学过程": {{
                    "导入环节": {{
                        "content": "环节内容",
                        "duration": "环节时长",
                        "activities": ["具体活动1", "具体活动2"],
                        "materials": ["教学材料1", "教学材料2"]
                    }},
                    "发展环节": {{
                        "content": "环节内容",
                        "duration": "环节时长",
                        "activities": ["具体活动1", "具体活动2"],
                        "materials": ["教学材料1", "教学材料2"]
                    }},
                    "总结环节": {{
                        "content": "环节内容",
                        "duration": "环节时长",
                        "activities": ["具体活动1", "具体活动2"],
                        "materials": ["教学材料1", "教学材料2"]
                    }}
                }},
                "设计亮点": "活动设计的亮点",
                "预期效果": "预期达到的效果",
                "可能问题": "可能遇到的问题",
                "对应章节": "对应的教材章节"
            }}
        }}
    ]
}}"""

        prompt = template.format(
            hours=total_hours,
            points=points_json,
            total_minutes=total_hours * 45
        )

        print("\n=== 设计教学活动 ===")
        print(f"总课时: {total_hours}")
        print("调用LLM设计活动...")
        
        # 调用LLM
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": "你是一个专业的教学设计专家，擅长设计教学活动。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        # 解析响应
        result = response.choices[0].message.content
        if isinstance(result, str):
            result = json.loads(result)
            
        # 验证结果
        if not isinstance(result, dict):
            raise ValueError(f"结果格式错误: {type(result)}")
            
        if "time_allocation" not in result:
            raise ValueError("缺少time_allocation字段")
            
        if "activities" not in result:
            raise ValueError("缺少activities字段")
            
        time_allocation = result["time_allocation"]
        if not isinstance(time_allocation, dict):
            raise ValueError(f"time_allocation格式错误: {type(time_allocation)}")
            
        activities = result["activities"]
        if not isinstance(activities, list):
            raise ValueError(f"activities格式错误: {type(activities)}")
            
        if not activities:
            raise ValueError("activities不能为空")
            
        # 验证时间分配
        total_time = sum(float(time_allocation.get(key, 0)) for key in ["knowledge", "skill", "practice", "discussion", "assessment"])
        if abs(total_time - total_hours) > 0.1:  # 允许0.1课时的误差
            raise ValueError(f"时间分配不正确：总和{total_time}课时，应为{total_hours}课时")
            
        # 验证活动时长
        valid_durations = {15, 30, 45, 90}
        for activity in activities:
            if not isinstance(activity, dict):
                raise ValueError(f"活动格式错误: {type(activity)}")
            if "activity" not in activity:
                raise ValueError("活动缺少activity字段")
            act = activity["activity"]
            if "duration" not in act:
                raise ValueError("活动缺少duration字段")
            try:
                duration = int(str(act["duration"]).replace("分钟", ""))
                if duration not in valid_durations:
                    raise ValueError(f"活动时长{duration}不是有效值（15/30/45/90）")
            except ValueError as e:
                raise ValueError(f"活动时长格式错误: {str(e)}")
                
        print("活动设计完成")
        return result
        
    except Exception as e:
        print(f"错误：设计教学活动失败 - {str(e)}")
        raise LLMGenerationError(f"设计教学活动失败: {str(e)}")

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
=======
from typing import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from ..config import get_llm
from ..utils.types import AgentState

def design_activities(state: AgentState) -> AgentState:
    """设计教学活动的代理"""
    try:
        print("\n=== 开始设计教学活动 ===")
        state["progress_status"] = "正在设计教学活动..."
        
        system_prompt = f"""你是一位创新的教学设计专家。
        你的任务是设计有效的教学活动来实现教学目标。

        请遵循以下原则：
        1. 活动设计要以学生为中心
        2. 结合多样化的教学方法
        3. 注重师生互动和生生互动
        4. 适当运用现代教育技术
        5. 每节课45分钟，总课时{state['total_hours']}课时
        6. 考虑教学内容的难度和学生接受程度
        7. 设计要体现教学目标的层次性和递进性
        8. 注重理论与实践的结合
        9. 适当融入学科核心素养的培养

        输出格式：
        1. 课时分配方案（总计{state['total_hours']}课时）：
           * 知识讲解：X课时（说明分配理由）
           * 技能训练：X课时（说明训练重点）
           * 实践活动：X课时（说明活动特色）
           * 研讨交流：X课时（说明交流形式）
           * 测试评价：X课时（说明评价方式）

        2. 具体活动设计：
           第X课时：[主题名称]
           - 教学重点：（对应知识点）
           - 教学方法：（采用的方法及理由）
           - 教学过程：
             * 导入环节（5分钟）：...
             * 发展环节（30分钟）：...
             * 总结环节（10分钟）：...
           - 设计亮点：（创新之处）
           - 预期效果：（对应教学目标）
           - 可能问题：（教学难点及应对）
        """
        
        user_prompt = f"""
        请基于以下内容，设计总计{state['total_hours']}课时的教学活动。

        教学目标：
        {state['teaching_objectives']}

        知识点体系：
        {state['knowledge_points']}

        请确保你的设计：
        1. 每个活动都明确对应教学目标
        2. 活动难度循序渐进
        3. 时间分配合理，总计{state['total_hours']}课时
        4. 充分考虑学生参与度
        5. 包含必要的复习和巩固环节
        6. 设计适当的课堂互动方式
        7. 注意理论与实践的结合
        """
        
        llm = get_llm(is_scanned=state["is_scanned"])
        print("正在调用 AI 设计教学活动...")
        response = llm.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        content = response.choices[0].message.content
        print("教学活动设计完成，正在解析课时分配...")
        
        # 解析课时分配
        hours_per_section = {}
        for line in content.split('\n'):
            if '：' in line and '课时' in line:
                try:
                    section = line.split('：')[0].strip()
                    hours = int(line.split('：')[1].replace('课时', ''))
                    hours_per_section[section] = hours
                except:
                    continue
        
        # 验证课时总和
        total = sum(hours_per_section.values())
        if total != state['total_hours']:
            raise ValueError(f"课时分配总和({total})不等于指定的总课时数({state['total_hours']})")
        
        activities = [
            {"activity": activity.strip()}
            for activity in content.split('\n')
            if activity.strip()
        ]
        
        # 确保所有字段都有有效值
        new_state = {
            **state,
            "teaching_activities": activities,
            "hours_per_section": hours_per_section,
            "next_step": "create_assessment",
            "messages": [],
            "assessment_plan": state.get("assessment_plan", {}),
            "final_output": state.get("final_output", ""),
            "progress_status": "已设计教学���动",
            "error_msg": None
        }
        print("=== 教学活动设计完成 ===\n")
        return new_state
        
    except Exception as e:
        return {
            **state,
            "error_msg": str(e),
            "next_step": "error",
            "progress_status": "生成失败",
            "messages": [],
            "teaching_objectives": state.get("teaching_objectives"),
            "knowledge_points": state.get("knowledge_points", []),
            "teaching_activities": [],
            "assessment_plan": {},
            "final_output": "",
            "hours_per_section": {}
        } 
>>>>>>> c4972e73ce82ab596751226cd0a07e233d3db998
