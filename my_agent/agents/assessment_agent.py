from typing import Dict, Any, List
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
import json

def create_assessment(objectives: Dict[str, Any], knowledge_points: Dict[str, Any], grade: str, subject: str) -> str:
    """创建评估方案"""
    llm = get_llm()
    prompt = f"""作为一名资深的{subject}教师，请仔细阅读教材内容、教学目标和知识点，设计评估方案。

请首先分析教材的以下几个方面：
1. 教材的考核要点分布
2. 各单元的重难点设置
3. 教材提供的练习和测试
4. 学科核心素养的考查要求

然后基于以上分析，设计评估方案。要求：
1. 输出采用markdown格式，结构清晰，层次分明，全部使用中文
2. 评估方案应包含以下部分：

### 形成性评价

[此处结合教材内容，列出6-8个形成性评价项目，每个项目包含：
- **评价项目**：与教材内容直接相关的具体评价项目
- **对应章节**：该评价项目对应的教材章节
- **评价方式**：具体的评价方法
- **分值设置**：具体的分值分配
- **评价时间**：在教学过程中的具体实施时间
- **评价标准**：2-3个基于教材内容的具体评价标准
- **实施要点**：评价过程中需要注意的具体问题]

### 终结性评价

[此处结合教材重点内容，列出2-3个终结性评价项目，每个项目包含：
- **评价项目**：与教材重点内容相关的具体评价项目
- **考查范围**：具体对应的教材章节和内容
- **评价方式**：具体的评价方法
- **分值设置**：具体的分值分配
- **评价时间**：具体的评价时间安排
- **评价标准**：2-3个基于教材内容的具体评价标准
- **实施要点**：评价过程中需要注意的具体问题]

### 评价权重分配

- **形成性评价**：60%，包括：
  - 课堂表现：20%
  - 作业完成：20%
  - 实践活动：20%
- **终结性评价**：40%，包括：
  - 期中测试：15%
  - 期末考试：25%

### 反馈与改进机制

[此处结合教材特点，列出4种反馈方式，每种方式包含：
- **反馈方式**：具体的反馈方式描述
- **适用内容**：该反馈方式适用的教材内容
- **反馈时机**：在教学过程中的具体反馈时间
- **实施方法**：如何具体实施这种反馈]

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

    try:
        response = llm.client.chat.completions.create(
            model=llm.model,
            temperature=llm.temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise LLMGenerationError(f"生成评估方案失败: {str(e)}")

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
