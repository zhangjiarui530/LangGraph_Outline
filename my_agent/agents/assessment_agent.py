<<<<<<< HEAD
from typing import Dict, Any, List
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
from my_agent.utils.types import AgentState
import json

def create_assessment(objectives: Dict[str, Any], knowledge_points: Dict[str, Any]) -> Dict[str, Any]:
    """创建评估方案"""
    try:
        # 验证输入
        if not isinstance(objectives, dict):
            raise ValueError(f"教学目标格式错误: {type(objectives)}")
            
        if not isinstance(knowledge_points, dict):
            raise ValueError(f"知识点格式错误: {type(knowledge_points)}")
            
        # 获取LLM配置
        llm_config = get_llm()
        
        # 构建提示词
        objectives_json = json.dumps(objectives, indent=2, ensure_ascii=False)
        points_json = json.dumps(knowledge_points, indent=2, ensure_ascii=False)
        template = """作为评估方案设计专家，请基于以下教学目标和知识点设计评估方案。

教学目标：
{objectives}

知识点：
{points}

请设计评估方案，要求：
1. 评估方案要全面覆盖教学目标和知识点
2. 评估方式要多样化，包含形成性评估和终结性评估
3. 评估标准要具体、可操作
4. 评估结果要可量化

请按以下格式输出：
{{
    "assessment_plan": {{
        "formative": [
            {{
                "type": "评估类型",
                "name": "评估名称",
                "description": "评估描述",
                "objectives": ["对应的教学目标1", "对应的教学目标2"],
                "knowledge_points": ["对应的知识点1", "对应的知识点2"],
                "criteria": {{
                    "优秀": "评分标准",
                    "良好": "评分标准",
                    "及格": "评分标准",
                    "不及格": "评分标准"
                }},
                "weight": "占总成绩的权重",
                "timing": "实施时间",
                "tools": ["评估工具1", "评估工具2"],
                "feedback": "反馈方式"
            }}
        ],
        "summative": [
            {{
                "type": "评估类型",
                "name": "评估名称",
                "description": "评估描述",
                "objectives": ["对应的教学目标1", "对应的教学目标2"],
                "knowledge_points": ["对应的知识点1", "对应的知识点2"],
                "criteria": {{
                    "优秀": "评分标准",
                    "良好": "评分标准",
                    "及格": "评分标准",
                    "不及格": "评分标准"
                }},
                "weight": "占总成绩的权重",
                "timing": "实施时间",
                "tools": ["评估工具1", "评估工具2"],
                "feedback": "反馈方式"
            }}
        ],
        "weights": {{
            "formative": "形成性评估总权重",
            "summative": "终结性评估总权重"
        }}
    }}
}}"""

        prompt = template.format(objectives=objectives_json, points=points_json)

        print("\n=== 创建评估方案 ===")
        print("调用LLM创建评估方案...")
        
        # 调用LLM
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": "你是一个专业的评估方案设计专家，擅长设计教学评估方案。"},
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
            
        if "assessment_plan" not in result:
            raise ValueError("缺少assessment_plan字段")
            
        plan = result["assessment_plan"]
        if not isinstance(plan, dict):
            raise ValueError(f"assessment_plan格式错误: {type(plan)}")
            
        required_fields = ["formative", "summative", "weights"]
        for field in required_fields:
            if field not in plan:
                raise ValueError(f"缺少{field}字段")
                
        # 验证形成性和终结性评估
        for field in ["formative", "summative"]:
            assessments = plan[field]
            if not isinstance(assessments, list):
                raise ValueError(f"{field}评估格式错误")
            if not assessments:
                raise ValueError(f"{field}评估不能为空")
            for assessment in assessments:
                if not isinstance(assessment, dict):
                    raise ValueError(f"{field}评估项格式错误")
                for key in ["type", "name", "description", "objectives", "knowledge_points", "criteria", "weight", "timing", "tools", "feedback"]:
                    if key not in assessment:
                        raise ValueError(f"{field}评估缺少{key}字段")
                    if key in ["objectives", "knowledge_points", "tools"]:
                        if not isinstance(assessment[key], list):
                            raise ValueError(f"{field}评估的{key}字段必须是列表")
                    elif key == "criteria":
                        if not isinstance(assessment[key], dict):
                            raise ValueError(f"{field}评估的{key}字段必须是字典")
                        for grade in ["优秀", "良好", "及格", "不及格"]:
                            if grade not in assessment[key]:
                                raise ValueError(f"{field}评估的评分标准缺少{grade}等级")
                    else:
                        if not isinstance(assessment[key], str):
                            raise ValueError(f"{field}评估的{key}字段必须是字符串")
                            
        # 验证权重
        weights = plan["weights"]
        if not isinstance(weights, dict):
            raise ValueError("weights格式错误")
        for key in ["formative", "summative"]:
            if key not in weights:
                raise ValueError(f"weights缺少{key}字段")
            if not isinstance(weights[key], str):
                raise ValueError(f"weights的{key}字段必须是字符串")
                
        print("评估方案创建完成")
        return result
        
    except Exception as e:
        print(f"错误：创建评估方案失败 - {str(e)}")
        raise LLMGenerationError(f"创建评估方案失败: {str(e)}")

def validate_assessment(assessment: Dict[str, Any]) -> None:
    """
    验证评估方案的格式和内容
    
    Args:
        assessment: 评估方案字典
        
    Raises:
        ValueError: 如果格式或内容不符合要求
    """
    # 检查基本结构
    if not isinstance(assessment, dict):
        raise ValueError("评估方案必须是字典类型")
        
    if "process_assessment" not in assessment:
        raise ValueError("缺少process_assessment字段")
        
    if "final_assessment" not in assessment:
        raise ValueError("缺少final_assessment字段")
        
    if "feedback_mechanism" not in assessment:
        raise ValueError("缺少feedback_mechanism字段")
        
    # 检查过程性评价
    proc = assessment["process_assessment"]
    if not isinstance(proc, dict):
        raise ValueError("process_assessment必须是字典类型")
    if "items" not in proc:
        raise ValueError("process_assessment缺少items字段")
    if "total_percentage" not in proc:
        raise ValueError("process_assessment缺少total_percentage字段")
    if proc["total_percentage"] != 60:
        raise ValueError("process_assessment的total_percentage必须为60")
        
    # 检查终结性评价
    final = assessment["final_assessment"]
    if not isinstance(final, dict):
        raise ValueError("final_assessment必须是字典类型")
    if "items" not in final:
        raise ValueError("final_assessment缺少items字段")
    if "total_percentage" not in final:
        raise ValueError("final_assessment缺少total_percentage字段")
    if final["total_percentage"] != 40:
        raise ValueError("final_assessment的total_percentage必须为40")
        
    # 检查评价项目
    for assessment_type in [proc, final]:
        items = assessment_type["items"]
        if not isinstance(items, list):
            raise ValueError("items必须是列表类型")
        if not items:
            raise ValueError("items不能为空")
            
        total = sum(float(item["percentage"]) for item in items)
        if abs(total - assessment_type["total_percentage"]) > 0.1:  # 允许0.1的误差
            raise ValueError(f"评价项目占比总和({total})不等于要求值({assessment_type['total_percentage']})")
            
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("评价项目必须是字典类型")
            for key in ["name", "description", "percentage", "criteria", "methods"]:
                if key not in item:
                    raise ValueError(f"评价项目缺少{key}字段")
                    
    # 检查反馈机制
    feed = assessment["feedback_mechanism"]
    if not isinstance(feed, dict):
        raise ValueError("feedback_mechanism必须是字典类型")
    for key in ["methods", "frequency", "improvement"]:
        if key not in feed:
            raise ValueError(f"反馈机制缺少{key}字段")
        if key != "frequency" and not isinstance(feed[key], list):
            raise ValueError(f"{key}必须是列表类型")
        if key == "frequency" and not isinstance(feed[key], str):
            raise ValueError("frequency必须是字符串类型")
=======
from typing import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from ..config import get_llm
from ..utils.types import AgentState
from ..utils.output_formatter import format_final_output

def create_assessment(state: AgentState) -> AgentState:
    """创建评估方案的代理"""
    try:
        print("\n=== 开始生成评估方案 ===")
        state["progress_status"] = "正在制定评估方案..."
        
        system_prompt = """你是一位教育评估专家。
        你的任务是设计全面的评估方案来检验教学目标的达成情况。

        请遵循以下原则：
        1. 评估方式要多元化
        2. 注重过程性评价和终结性评价相结合
        3. 评估标准要清晰可操作
        4. 关注学生的全面发展
        5. 评估要体现素养导向
        6. 注重学生的自主评价和互评
        7. 评估结果要能指导教学改进

        输出格式：
        1. 过程性评价方案（占比60%）：
           A. 课堂表现（20%）
              - 具体评估要点
              - 评分标准
              - 记录方式
           
           B. 作业完成（20%）
              - 作业类型和要求
              - 批改要点
              - 反馈方式
           
           C. 实践活动（20%）
              - 活动评价维度
              - 评价方法
              - 证据收集

        2. 终结性评价方案（占比40%）：
           A. 理论测试
              - 题型设置
              - 难度分布
              - 重点考查内容
           
           B. 实践考核
              - 考核形式
              - 评分标准
              - 注意事项

        3. 评价反馈机制：
           - 及时反馈方式
           - 结果运用建议
           - 改进策略设计
        """
        
        user_prompt = f"""
        请基于以下内容，设计完整的评估方案。

        教学目标：
        {state['teaching_objectives']}

        知识点体系：
        {state['knowledge_points']}

        教学活动：
        {state['teaching_activities']}

        请确保评估方案：
        1. 全面覆盖教学目标
        2. 评价方式多样
        3. 标准清晰可操作
        4. 注重过程性评价
        5. 体现素养导向
        6. 具有可行性
        7. 促进教学改进
        """
        
        llm = get_llm(is_scanned=state["is_scanned"])
        print("正在调用 AI 生成评估方案...")
        response = llm.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        content = response.choices[0].message.content
        print("评估方案生成完成，正在整理输出...")
        
        assessment_plan = {
            "plan": content
        }
        
        # 生成最终输出
        final_output = format_final_output({
            **state,
            "assessment_plan": assessment_plan
        })
        
        print("正在保存最终结果...")
        # 确保所有字段都有有效值
        new_state = {
            **state,
            "assessment_plan": assessment_plan,
            "next_step": "end",
            "messages": [],
            "final_output": final_output,
            "progress_status": "已完成评估方案",
            "error_msg": None
        }
        print("=== 评估方案生成完成 ===\n")
        return new_state
        
    except Exception as e:
        print(f"\n!!! 评估方案生成失败: {str(e)} !!!\n")
        return {
            **state,
            "error_msg": str(e),
            "next_step": "error",
            "progress_status": "生成失败",
            "messages": [],
            "teaching_objectives": state.get("teaching_objectives"),
            "knowledge_points": state.get("knowledge_points", []),
            "teaching_activities": state.get("teaching_activities", []),
            "assessment_plan": {},
            "final_output": "",
            "hours_per_section": state.get("hours_per_section", {})
        } 
>>>>>>> c4972e73ce82ab596751226cd0a07e233d3db998
