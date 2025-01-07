from typing import Dict, Any, List, Union

def format_meta_info(meta_info: Dict[str, Any]) -> str:
    """格式化基本信息
    
    Args:
        meta_info: 基本信息数据
        
    Returns:
        str: Markdown格式的基本信息
    """
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

def format_objectives(objectives: Dict[str, Any]) -> str:
    """格式化教学目标
    
    Args:
        objectives: 教学目标数据
        
    Returns:
        str: Markdown格式的教学目标
    """
    result = []
    
    # 处理教学目标
    if "knowledge_skill" in objectives:
        result.append("### 知识与技能目标\n")
        for obj in objectives["knowledge_skill"]:
            result.append(f"- **{obj.get('content', '')}**")
            if "importance" in obj:
                result.append(f"  - 重要程度：{obj['importance']}")
            if "evaluation_criteria" in obj:
                result.append("  - 评价标准：")
                for criterion in obj["evaluation_criteria"]:
                    result.append(f"    - {criterion}")
            result.append("")
            
    if "process_method" in objectives:
        result.append("### 过程与方法目标\n")
        for obj in objectives["process_method"]:
            result.append(f"- **{obj.get('content', '')}**")
            if "importance" in obj:
                result.append(f"  - 重要程度：{obj['importance']}")
            if "evaluation_criteria" in obj:
                result.append("  - 评价标准：")
                for criterion in obj["evaluation_criteria"]:
                    result.append(f"    - {criterion}")
            result.append("")
            
    if "emotion_attitude" in objectives:
        result.append("### 情感态度与价值观目标\n")
        for obj in objectives["emotion_attitude"]:
            result.append(f"- **{obj.get('content', '')}**")
            if "importance" in obj:
                result.append(f"  - 重要程度：{obj['importance']}")
            if "evaluation_criteria" in obj:
                result.append("  - 评价标准：")
                for criterion in obj["evaluation_criteria"]:
                    result.append(f"    - {criterion}")
            result.append("")
            
    # 处理其他未知类型的目标
    for key, value in objectives.items():
        if key not in ["knowledge_skill", "process_method", "emotion_attitude"]:
            result.append(f"### {key}\n")
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            result.append(f"- **{k}**：{v}")
                    else:
                        result.append(f"- {item}")
                result.append("")
                
    return "\n".join(result)

def format_core_literacy(literacy: List[Dict[str, Any]]) -> str:
    """格式化核心素养
    
    Args:
        literacy: 核心素养数据
        
    Returns:
        str: Markdown格式的核心素养
    """
    result = []
    
    for item in literacy:
        if isinstance(item, dict):
            result.append(f"### {item.get('name', '未命名素养')}\n")
            if "description" in item:
                result.append(f"- **描述**：{item['description']}")
            if "related_objectives" in item:
                result.append("- **相关目标**：")
                for obj in item["related_objectives"]:
                    result.append(f"  - {obj}")
            # 处理其他未知字段
            for key, value in item.items():
                if key not in ["name", "description", "related_objectives"]:
                    result.append(f"- **{key}**：{value}")
            result.append("")
        else:
            result.append(f"- {item}\n")
            
    return "\n".join(result)

def format_knowledge_points(knowledge_points: Dict[str, Any]) -> str:
    """格式化知识点
    
    Args:
        knowledge_points: 知识点数据
        
    Returns:
        str: Markdown格式的知识点
    """
    result = []
    
    if "knowledge_points" in knowledge_points:
        kp = knowledge_points["knowledge_points"]
        
        # 处理基础知识点
        if "basic" in kp:
            result.append("### 基础知识点\n")
            for point in kp["basic"]:
                result.append(f"#### {point.get('name', '未命名知识点')}\n")
                result.append(f"- **内容**：{point.get('content', '')}")
                result.append(f"- **难度**：{point.get('difficulty', '')}")
                result.append(f"- **重要程度**：{point.get('importance', '')}")
                if "prerequisites" in point:
                    result.append("- **前置知识**：")
                    for pre in point["prerequisites"]:
                        result.append(f"  - {pre}")
                if "objectives" in point:
                    result.append("- **相关目标**：")
                    for obj in point["objectives"]:
                        result.append(f"  - {obj}")
                if "teaching_suggestions" in point:
                    result.append(f"- **教学建议**：{point['teaching_suggestions']}")
                # 处理其他未知字段
                for key, value in point.items():
                    if key not in ["name", "content", "difficulty", "importance", "prerequisites", "objectives", "teaching_suggestions"]:
                        result.append(f"- **{key}**：{value}")
                result.append("")
                
        # 处理拓展知识点
        if "advanced" in kp:
            result.append("### 拓展知识点\n")
            for point in kp["advanced"]:
                result.append(f"#### {point.get('name', '未命名知识点')}\n")
                result.append(f"- **内容**：{point.get('content', '')}")
                result.append(f"- **难度**：{point.get('difficulty', '')}")
                result.append(f"- **重要程度**：{point.get('importance', '')}")
                if "prerequisites" in point:
                    result.append("- **前置知识**：")
                    for pre in point["prerequisites"]:
                        result.append(f"  - {pre}")
                if "objectives" in point:
                    result.append("- **相关目标**：")
                    for obj in point["objectives"]:
                        result.append(f"  - {obj}")
                if "teaching_suggestions" in point:
                    result.append(f"- **教学建议**：{point['teaching_suggestions']}")
                # 处理其他未知字段
                for key, value in point.items():
                    if key not in ["name", "content", "difficulty", "importance", "prerequisites", "objectives", "teaching_suggestions"]:
                        result.append(f"- **{key}**：{value}")
                result.append("")
                
        # 处理重点和难点
        if "key_points" in kp:
            result.append("### 教学重点\n")
            for point in kp["key_points"]:
                result.append(f"- {point}")
            result.append("")
            
        if "difficult_points" in kp:
            result.append("### 教学难点\n")
            for point in kp["difficult_points"]:
                result.append(f"- {point}")
            result.append("")
            
        # 处理其他未知类型的知识点
        for key, value in kp.items():
            if key not in ["basic", "advanced", "key_points", "difficult_points"]:
                result.append(f"### {key}\n")
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            for k, v in item.items():
                                result.append(f"- **{k}**：{v}")
                        else:
                            result.append(f"- {item}")
                    result.append("")
                    
    return "\n".join(result)

def format_activities(activities: Dict[str, Any]) -> str:
    """格式化教学活动
    
    Args:
        activities: 教学活动数据
        
    Returns:
        str: Markdown格式的教学活动
    """
    result = []
    
    if "activities" in activities:
        for idx, activity in enumerate(activities["activities"], 1):
            result.append(f"### 活动{idx}：{activity.get('name', '未命名活动')}\n")
            result.append(f"- **类型**：{activity.get('type', '')}")
            result.append(f"- **课时**：{activity.get('duration', '')}课时")
            result.append(f"- **内容**：{activity.get('content', '')}\n")
            
            if "objectives" in activity:
                result.append("- **教学目标**：")
                for obj in activity["objectives"]:
                    result.append(f"  - {obj}")
                result.append("")
                
            if "key_points" in activity:
                result.append("- **重点**：")
                for point in activity["key_points"]:
                    result.append(f"  - {point}")
                result.append("")
                
            if "difficult_points" in activity:
                result.append("- **难点**：")
                for point in activity["difficult_points"]:
                    result.append(f"  - {point}")
                result.append("")
                
            if "methods" in activity:
                result.append("- **教学方法**：")
                for method in activity["methods"]:
                    result.append(f"  - {method}")
                result.append("")
                
            if "student_participation" in activity:
                result.append(f"- **学生参与**：{activity['student_participation']}\n")
                
            if "expected_outcomes" in activity:
                result.append("- **预期效果**：")
                for outcome in activity["expected_outcomes"]:
                    result.append(f"  - {outcome}")
                result.append("")
                
            if "homework" in activity:
                result.append(f"- **课后作业**：{activity['homework']}\n")
                
            if "extensions" in activity:
                result.append("- **拓展活动**：")
                for ext in activity["extensions"]:
                    result.append(f"  - {ext}")
                result.append("")
                
            # 处理其他未知字段
            for key, value in activity.items():
                if key not in ["name", "type", "duration", "content", "objectives", "key_points", "difficult_points", 
                             "methods", "student_participation", "expected_outcomes", "homework", "extensions"]:
                    if isinstance(value, list):
                        result.append(f"- **{key}**：")
                        for item in value:
                            result.append(f"  - {item}")
                    else:
                        result.append(f"- **{key}**：{value}")
                    result.append("")
                    
    if "time_allocation" in activities:
        result.append("### 课时分配\n")
        for key, value in activities["time_allocation"].items():
            result.append(f"- **{key}**：{value}课时")
        result.append("")
        
    # 处理其他未知字段
    for key, value in activities.items():
        if key not in ["activities", "time_allocation"]:
            result.append(f"### {key}\n")
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            result.append(f"- **{k}**：{v}")
                    else:
                        result.append(f"- {item}")
            else:
                result.append(f"- {value}")
            result.append("")
            
    return "\n".join(result)

def format_assessment(assessment: Dict[str, Any]) -> str:
    """格式化评估方案
    
    Args:
        assessment: 评估方案数据
        
    Returns:
        str: Markdown格式的评估方案
    """
    result = []
    
    if "formative" in assessment:
        result.append("### 形成性评价\n")
        for item in assessment["formative"]:
            result.append(f"#### {item.get('name', '未命名评估')}\n")
            result.append(f"- **内容**：{item.get('content', '')}")
            result.append(f"- **方法**：{item.get('method', '')}")
            result.append(f"- **分值**：{item.get('score', '')}")
            result.append(f"- **时间**：{item.get('timing', '')}")
            
            if "criteria" in item:
                result.append("- **评价标准**：")
                for criterion in item["criteria"]:
                    result.append(f"  - {criterion}")
                    
            if "notes" in item:
                result.append(f"- **注意事项**：{item['notes']}")
                
            # 处理其他未知字段
            for key, value in item.items():
                if key not in ["name", "content", "method", "score", "timing", "criteria", "notes"]:
                    if isinstance(value, list):
                        result.append(f"- **{key}**：")
                        for v in value:
                            result.append(f"  - {v}")
                    else:
                        result.append(f"- **{key}**：{value}")
            result.append("")
            
    if "summative" in assessment:
        result.append("### 终结性评价\n")
        for item in assessment["summative"]:
            result.append(f"#### {item.get('name', '未命名评估')}\n")
            result.append(f"- **内容**：{item.get('content', '')}")
            result.append(f"- **方法**：{item.get('method', '')}")
            result.append(f"- **分值**：{item.get('score', '')}")
            result.append(f"- **时间**：{item.get('timing', '')}")
            
            if "criteria" in item:
                result.append("- **评价标准**：")
                for criterion in item["criteria"]:
                    result.append(f"  - {criterion}")
                    
            if "notes" in item:
                result.append(f"- **注意事项**：{item['notes']}")
                
            # 处理其他未知字段
            for key, value in item.items():
                if key not in ["name", "content", "method", "score", "timing", "criteria", "notes"]:
                    if isinstance(value, list):
                        result.append(f"- **{key}**：")
                        for v in value:
                            result.append(f"  - {v}")
                    else:
                        result.append(f"- **{key}**：{value}")
            result.append("")
            
    if "weight" in assessment:
        result.append("### 评价权重\n")
        for key, value in assessment["weight"].items():
            result.append(f"- **{key}**：{value}")
        result.append("")
        
    if "feedback_methods" in assessment:
        result.append("### 反馈方式\n")
        for method in assessment["feedback_methods"]:
            result.append(f"#### {method.get('type', '未命名反馈')}\n")
            result.append(f"- **描述**：{method.get('description', '')}")
            result.append(f"- **时机**：{method.get('timing', '')}")
            result.append(f"- **形式**：{method.get('format', '')}")
            
            # 处理其他未知字段
            for key, value in method.items():
                if key not in ["type", "description", "timing", "format"]:
                    if isinstance(value, list):
                        result.append(f"- **{key}**：")
                        for v in value:
                            result.append(f"  - {v}")
                    else:
                        result.append(f"- **{key}**：{value}")
            result.append("")
            
    # 处理其他未知字段
    for key, value in assessment.items():
        if key not in ["formative", "summative", "weight", "feedback_methods"]:
            result.append(f"### {key}\n")
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            result.append(f"- **{k}**：{v}")
                    else:
                        result.append(f"- {item}")
            else:
                result.append(f"- {value}")
            result.append("")
            
    return "\n".join(result)
