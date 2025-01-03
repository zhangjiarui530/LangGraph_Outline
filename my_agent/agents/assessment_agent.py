from typing import Dict, Any, List
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
from my_agent.utils.types import AgentState
import json

def create_assessment(objectives: Dict[str, Any], knowledge_points: Dict[str, Any]) -> Dict[str, Any]:
    """创建评估方案"""
    try:
        # 获取LLM配置
        llm_config = get_llm()
        
        # 构建提示词
        objectives_json = json.dumps(objectives, indent=2, ensure_ascii=False)
        knowledge_json = json.dumps(knowledge_points, indent=2, ensure_ascii=False)
        template = """作为一名资深的语文教师，请基于以下教学目标和知识点设计评估方案。

教学目标：
{objectives}

知识点：
{knowledge}

请设计完整的评估方案，要求：
1. 评估要全面覆盖教学目标和知识点
2. 评估方式要多样化，包括：
   - 课堂观察
   - 口头提问
   - 作业练习
   - 小组讨论
   - 实践活动
   - 测试考查
   - 自评互评
3. 每个评估项目要说明：
   - 评估内容
   - 评估方式
   - 评估标准
   - 分值分配
   - 实施时间
   - 注意事项
4. 评估设计要：
   - 注重过程性评价
   - 关注学生发展
   - 体现能力导向
   - 突出应用实践
   - 重视情感态度
   - 考虑个体差异
   - 保证科学公平

请按以下格式输出：
{{
    "assessment_plan": {{
        "formative": [
            {{
                "name": "评估项目名称",
                "content": "评估内容",
                "method": "评估方式",
                "criteria": ["评估标准1", "评估标准2"],
                "score": "分值分配",
                "timing": "实施时间",
                "notes": "注意事项"
            }}
        ],
        "summative": [
            {{
                "name": "评估项目名称",
                "content": "评估内容",
                "method": "评估方式",
                "criteria": ["评估标准1", "评估标准2"],
                "score": "分值分配",
                "timing": "实施时间",
                "notes": "注意事项"
            }}
        ],
        "weight": {{
            "formative": "过程性评价权重",
            "summative": "终结性评价权重"
        }}
    }},
    "feedback_methods": [
        {{
            "type": "反馈类型",
            "description": "具体描述",
            "timing": "反馈时机",
            "format": "反馈形式"
        }}
    ]
}}"""

        prompt = template.format(
            objectives=objectives_json,
            knowledge=knowledge_json
        )

        print("\n=== 设计评估方案 ===")
        print("调用LLM设计评估方案...")
        
        # 调用LLM
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": "你是一个专业的语文教师，擅长设计教学评估方案。你的设计要符合新课标要求，体现学科特点。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        # 解析响应
        result = response.choices[0].message.content
        if isinstance(result, str):
            result = json.loads(result)
            
        print("评估方案设计完成")
        return result
        
    except Exception as e:
        print(f"错误：设计评估方案失败 - {str(e)}")
        return {
            "assessment_plan": {
                "formative": [],
                "summative": [],
                "weight": {
                    "formative": 0,
                    "summative": 0
                }
            },
            "feedback_methods": []
        }

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
