from typing import Dict, Any, List, Union
from datetime import datetime

def format_meta_info(meta_info: Dict[str, Any]) -> str:
    """格式化基本信息"""
    field_map = {
        "grade": "年级",
        "subject": "学科",
        "total_hours": "总课时",
        "textbook_title": "教材名称"
    }
    
    result = []
    for key, title in field_map.items():
        if key in meta_info:
            result.append(f"- **{title}**：{meta_info[key]}")
            
    # 处理其他未知字段
    for key, value in meta_info.items():
        if key not in field_map:
            result.append(f"- **{key}**：{value}")
            
    return "\n".join(result) + "\n"

def format_objectives(objectives: str) -> str:
    """格式化教学目标"""
    if not objectives:
        return "暂无教学目标"
    
    # 添加分隔线和引言
    result = [
        "本单元教学目标的设计基于课程标准要求，结合学生认知特点，从以下几个维度展开：\n",
        "---\n"
    ]
    
    # 添加正文内容，保持原有的层次结构
    result.append(objectives)
    
    # 添加结尾分隔线
    result.append("\n---\n")
    return "\n".join(result)

def format_knowledge_points(knowledge_points: str) -> str:
    """格式化知识点"""
    if not knowledge_points:
        return "暂无知识点分析"
    
    # 添加分隔线和引言
    result = [
        "本单元知识点体系的构建遵循由浅入深、循序渐进的原则，具体包含以下内容：\n",
        "---\n"
    ]
    
    # 添加正文内容，保持原有的层次结构
    result.append(knowledge_points)
    
    # 添加结尾分隔线
    result.append("\n---\n")
    return "\n".join(result)

def format_activities(activities: str) -> str:
    """格式化教学活动"""
    if not activities:
        return "暂无教学活动"
    
    # 添加分隔线和引言
    result = [
        "本单元教学活动的设计以学生为中心，注重能力培养和实践应用，具体安排如下：\n",
        "---\n"
    ]
    
    # 添加正文内容，保持原有的层次结构
    result.append(activities)
    
    # 添加结尾分隔线
    result.append("\n---\n")
    return "\n".join(result)

def format_assessment(assessment: str) -> str:
    """格式化评估方案"""
    if not assessment:
        return "暂无评估方案"
    
    # 添加分隔线和引言
    result = [
        "本单元评估方案采用多元评价方式，注重过程性评价与终结性评价的结合，具体包括：\n",
        "---\n"
    ]
    
    # 添加正文内容，保持原有的层次结构
    result.append(assessment)
    
    # 添加结尾分隔线
    result.append("\n---\n")
    return "\n".join(result)

def format_markdown(data: Dict[str, Any], course_name: str) -> str:
    """生成完整的Markdown文档"""
    sections = []
    
    # 添加文档标题和简介
    sections.extend([
        f"# {course_name}教学大纲\n",
        "> 本教学大纲依据新课程标准要求，结合学生认知特点和学科核心素养要求进行设计。\n",
        "> 通过系统化的教学目标、知识点分析、教学活动和评估方案，促进学生全面发展。\n\n"
    ])
    
    # 添加基本信息
    sections.extend([
        "## 一、基本信息\n",
        "*以下是本单元教学的基本信息：*\n",
        format_meta_info(data.get("meta_info", {}))
    ])
    
    # 添加教学目标
    sections.extend([
        "## 二、教学目标\n",
        format_objectives(data.get("teaching_objectives", ""))
    ])
    
    # 添加知识点分析
    sections.extend([
        "## 三、知识点分析\n",
        format_knowledge_points(data.get("knowledge_points", ""))
    ])
    
    # 添加教学活动
    sections.extend([
        "## 四、教学活动\n",
        format_activities(data.get("teaching_activities", ""))
    ])
    
    # 添加评估方案
    sections.extend([
        "## 五、评估方案\n",
        format_assessment(data.get("assessment_plan", ""))
    ])
    
    # 添加页脚
    sections.extend([
        "\n---\n",
        f"*文档生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
        "\n> 注：本教学大纲仅供参考，教师可根据实际教学情况进行适当调整。\n"
    ])
    
    return "\n".join(sections)
