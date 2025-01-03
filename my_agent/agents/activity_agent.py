from typing import Dict, Any, List
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
from my_agent.utils.types import AgentState
import json

def design_activities(knowledge_points: Dict[str, Any], total_hours: int) -> Dict[str, Any]:
    """设计教学活动"""
    try:
        # 获取LLM配置
        llm_config = get_llm()
        
        # 构建提示词
        knowledge_json = json.dumps(knowledge_points, indent=2, ensure_ascii=False)
        template = """作为一名资深的语文教师，请基于以下知识点和总课时设计教学活动。

知识点：
{knowledge}

总课时：{hours}课时（每课时45分钟）

请设计完整的教学活动方案，要求：
1. 活动要完整覆盖所有知识点
2. 合理分配课时，确保重点内容有充足时间
3. 每个活动要说明：
   - 活动名称和类型（讲授/讨论/练习等）
   - 具体内容和流程
   - 所需课时
   - 教学目标
   - 重点和难点
   - 教学方法和策略
   - 学生参与方式
   - 预期效果
   - 课后作业和延伸
4. 活动设计要：
   - 符合语文学科特点
   - 体现学生主体性
   - 注重能力培养
   - 关注情感态度
   - 适应学生水平
   - 形式丰富多样
   - 理论联系实际

请按以下格式输出：
{{
    "activities": [
        {{
            "name": "活动名称",
            "type": "活动类型",
            "content": "具体内容",
            "duration": "课时数",
            "objectives": ["教学目标1", "教学目标2"],
            "key_points": ["重点1", "重点2"],
            "difficult_points": ["难点1", "难点2"],
            "methods": ["教学方法1", "教学方法2"],
            "student_participation": "学生参与方式",
            "expected_outcomes": ["预期效果1", "预期效果2"],
            "homework": "课后作业",
            "extensions": ["延伸活动1", "延伸活动2"]
        }}
    ],
    "time_allocation": {{
        "knowledge": "知识讲授课时",
        "skill": "技能训练课时",
        "practice": "实践活动课时",
        "discussion": "讨论交流课时",
        "assessment": "测试评价课时"
    }}
}}"""

        prompt = template.format(
            knowledge=knowledge_json,
            hours=total_hours
        )

        print("\n=== 设计教学活动 ===")
        print("调用LLM设计教学活动...")
        
        # 调用LLM
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": "你是一个专业的语文教师，擅长设计教学活动。你的设计要符合新课标要求，体现学科特点。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        # 解析响应
        result = response.choices[0].message.content
        if isinstance(result, str):
            result = json.loads(result)
            
        print("教学活动设计完成")
        return result
        
    except Exception as e:
        print(f"错误：设计教学活动失败 - {str(e)}")
        return {
            "activities": [],
            "time_allocation": {
                "knowledge": 0,
                "skill": 0,
                "practice": 0,
                "discussion": 0,
                "assessment": 0
            }
        }

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
