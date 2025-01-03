from typing import Dict, Any, List, Union

def format_objectives(objectives: Union[Dict[str, List[str]], List[Dict[str, str]]]) -> str:
    """
    格式化教学目标
    支持两种格式：
    1. 字典格式：{'objectives': {'knowledge': [...], 'ability': [...], 'emotion': [...]}}
    2. 列表格式：[{'category': '知识', 'content': '目标1'}, ...]
    """
    try:
    result = []
    
        # 类型检查
        if not isinstance(objectives, (dict, list)):
            print(f"警告：教学目标格式错误，期望字典或列表，实际是{type(objectives)}")
            return "教学目标格式错误"
        
    if isinstance(objectives, dict):
        # 处理字典格式
            if "objectives" in objectives:
                obj_data = objectives["objectives"]
                if isinstance(obj_data, dict):
                    category_map = {
                        "knowledge": "知识",
                        "ability": "能力",
                        "emotion": "情感"
                    }
                    for category in ["knowledge", "ability", "emotion"]:
                        if category in obj_data:
                            goals = obj_data[category]
                            if isinstance(goals, list):
                                result.append(f"\n### {category_map[category]}目标")
            for goal in goals:
                                    if isinstance(goal, dict):
                                        result.append(f"- {goal.get('description', '')}")
                                        result.append(f"  - 层次：{goal.get('level', '')}")
                                        result.append(f"  - 评价标准：{goal.get('evaluation', '')}")
                                    else:
                                        result.append(f"- {str(goal)}")
    else:
        # 处理列表格式
        current_category = None
        for obj in objectives:
                if not isinstance(obj, dict):
                    print(f"警告：目标对象格式错误，期望字典，实际是{type(obj)}")
                    continue
                    
                category = obj.get('category')
                if category != current_category:
                    current_category = category
                    if category:
                result.append(f"\n### {current_category}")
                content = obj.get('content')
                if content:
                    result.append(f"- {content}")
        
        return "\n".join(result) if result else "未找到有效的教学目标"
        
    except Exception as e:
        print(f"警告：格式化教学目标时出错：{str(e)}")
        return "格式化教学目标失败"

def format_knowledge_points(knowledge_points: Dict[str, Any]) -> str:
    """格式化知识点"""
    try:
    result = []
        
        if not isinstance(knowledge_points, dict):
            return "知识点格式错误"
            
        # 获取knowledge_points字段
        kp_data = knowledge_points.get("knowledge_points", {})
        if not isinstance(kp_data, dict):
            return "知识点数据格式错误"
            
        # 基础知识点
        if "basic" in kp_data:
            result.append("\n### 基础知识点")
            for point in kp_data["basic"]:
                if isinstance(point, dict):
                    result.append(f"\n#### {point.get('name', '未命名知识点')}")
                    result.append(f"- 内容：{point.get('content', '')}")
                    result.append(f"- 难度：{point.get('difficulty', '')}")
                    result.append(f"- 重要性：{point.get('importance', '')}")
                    result.append("- 前置知识点：")
                    for pre in point.get('prerequisites', []):
                        result.append(f"  - {pre}")
                    result.append("- 对应教学目标：")
                    for obj in point.get('objectives', []):
                        result.append(f"  - {obj}")
                    result.append(f"- 教学建议：{point.get('teaching_suggestions', '')}")
                    
        # 高级知识点
        if "advanced" in kp_data:
            result.append("\n### 拓展知识点")
            for point in kp_data["advanced"]:
                if isinstance(point, dict):
                    result.append(f"\n#### {point.get('name', '未命名知识点')}")
                    result.append(f"- 内容：{point.get('content', '')}")
                    result.append(f"- 难度：{point.get('difficulty', '')}")
                    result.append(f"- 重要性：{point.get('importance', '')}")
                    result.append("- 前置知识点：")
                    for pre in point.get('prerequisites', []):
                        result.append(f"  - {pre}")
                    result.append("- 对应教学目标：")
                    for obj in point.get('objectives', []):
                        result.append(f"  - {obj}")
                    result.append(f"- 教学建议：{point.get('teaching_suggestions', '')}")
                    
        # 重点和难点
        if "key_points" in kp_data:
            result.append("\n### 教学重点")
            for point in kp_data["key_points"]:
                result.append(f"- {point}")
                
        if "difficult_points" in kp_data:
            result.append("\n### 教学难点")
            for point in kp_data["difficult_points"]:
                result.append(f"- {point}")
                
        return "\n".join(result) if result else "未找到有效的知识点"
        
    except Exception as e:
        print(f"警告：格式化知识点时出错：{str(e)}")
        return "格式化知识点失败"

def format_activities(activities: Dict[str, Any]) -> str:
    """格式化教学活动"""
    try:
        result = []
        
        if not isinstance(activities, dict):
            return "教学活动格式错误"
            
        # 课时分配
        if "time_allocation" in activities:
            result.append("\n### 课时分配")
            time = activities["time_allocation"]
            if isinstance(time, dict):
                result.append(f"- 知识讲解：{time.get('knowledge', 0)}课时")
                result.append(f"- 技能训练：{time.get('skill', 0)}课时")
                result.append(f"- 实践活动：{time.get('practice', 0)}课时")
                result.append(f"- 讨论交流：{time.get('discussion', 0)}课时")
                result.append(f"- 评估考核：{time.get('assessment', 0)}课时")
                
        # 具体活动
        if "activities" in activities:
            result.append("\n### 具体活动")
            for idx, act in enumerate(activities["activities"], 1):
                if isinstance(act, dict) and "activity" in act:
                    activity = act["activity"]
                    result.append(f"\n#### 活动{idx}：{activity.get('title', '未命名活动')}")
                    result.append(f"- 时长：{activity.get('duration', 0)}分钟")
                    result.append(f"- 教学重点：{activity.get('教学重点', '')}")
                    result.append(f"- 教学方法：{activity.get('教学方法', '')}")
                    
                    # 教学过程
                    result.append("- 教学过程：")
                    process = activity.get("教学过程", {})
                    for phase, details in process.items():
                        if isinstance(details, dict):
                            result.append(f"  - {phase}（{details.get('duration', 0)}分钟）：")
                            result.append(f"    - 内容：{details.get('content', '')}")
                            result.append("    - 具体活动：")
                            for item in details.get("activities", []):
                                result.append(f"      - {item}")
                            result.append("    - 教学材料：")
                            for item in details.get("materials", []):
                                result.append(f"      - {item}")
                                
                    result.append(f"- 设计亮点：{activity.get('设计亮点', '')}")
                    result.append(f"- 预期效果：{activity.get('预期效果', '')}")
                    result.append(f"- 可能问题：{activity.get('可能问题', '')}")
                    result.append(f"- 对应章节：{activity.get('对应章节', '')}")
                    
        return "\n".join(result) if result else "未找到有效的教学活动"
        
    except Exception as e:
        print(f"警告：格式化教学活动时出错：{str(e)}")
        return "格式化教学活动失败"

def format_assessment(assessment: Dict[str, Any]) -> str:
    """格式化评估方案"""
    try:
        result = []
        
        if not isinstance(assessment, dict):
            return "评估方案格式错误"
            
        # 获取assessment_plan字段
        plan = assessment.get("assessment_plan", {})
        if not isinstance(plan, dict):
            return "评估方案数据格式错误"
            
        # 形成性评估
        if "formative" in plan:
            result.append("\n### 形成性评估")
            for item in plan["formative"]:
                if isinstance(item, dict):
                    result.append(f"\n#### {item.get('name', '未命名评估')}")
                    result.append(f"- 评估类型：{item.get('type', '')}")
                    result.append(f"- 评估描述：{item.get('description', '')}")
                    result.append("- 对应教学目标：")
                    for obj in item.get("objectives", []):
                        result.append(f"  - {obj}")
                    result.append("- 对应知识点：")
                    for kp in item.get("knowledge_points", []):
                        result.append(f"  - {kp}")
                    result.append("- 评分标准：")
                    for grade, criteria in item.get("criteria", {}).items():
                        result.append(f"  - {grade}：{criteria}")
                    result.append(f"- 评估权重：{item.get('weight', '')}")
                    result.append(f"- 实施时间：{item.get('timing', '')}")
                    result.append("- 评估工具：")
                    for tool in item.get("tools", []):
                        result.append(f"  - {tool}")
                    result.append(f"- 反馈方式：{item.get('feedback', '')}")
                    
        # 终结性评估
        if "summative" in plan:
            result.append("\n### 终结性评估")
            for item in plan["summative"]:
                if isinstance(item, dict):
                    result.append(f"\n#### {item.get('name', '未命名评估')}")
                    result.append(f"- 评估类型：{item.get('type', '')}")
                    result.append(f"- 评估描述：{item.get('description', '')}")
                    result.append("- 对应教学目标：")
                    for obj in item.get("objectives", []):
                        result.append(f"  - {obj}")
                    result.append("- 对应知识点：")
                    for kp in item.get("knowledge_points", []):
                        result.append(f"  - {kp}")
                    result.append("- 评分标准：")
                    for grade, criteria in item.get("criteria", {}).items():
                        result.append(f"  - {grade}：{criteria}")
                    result.append(f"- 评估权重：{item.get('weight', '')}")
                    result.append(f"- 实施时间：{item.get('timing', '')}")
                    result.append("- 评估工具：")
                    for tool in item.get("tools", []):
                        result.append(f"  - {tool}")
                    result.append(f"- 反馈方式：{item.get('feedback', '')}")
                    
        # 评估权重
        if "weights" in plan:
            result.append("\n### 评估权重分配")
            weights = plan["weights"]
            if isinstance(weights, dict):
                result.append(f"- 形成性评估占比：{weights.get('formative', '')}")
                result.append(f"- 终结性评估占比：{weights.get('summative', '')}")
                
        return "\n".join(result) if result else "未找到有效的评估方案"
        
    except Exception as e:
        print(f"警告：格式化评估方案时出错：{str(e)}")
        return "格式化评估方案失败"

def format_final_output(data: Dict[str, Any]) -> str:
    """格式化最终输出"""
    try:
        sections = []
        
        # 教学目标
        sections.append("## 一、教学目标")
        if "objectives" in data:
            sections.append(format_objectives(data["objectives"]))
        else:
            sections.append("未生成教学目标")
            
        # 知识点分析
        sections.append("\n## 二、知识点分析")
        if "knowledge_points" in data:
            sections.append(format_knowledge_points(data["knowledge_points"]))
        else:
            sections.append("未生成知识点")
            
        # 教学活动
        sections.append("\n## 三、教学活动")
        if "activities" in data:
            sections.append(format_activities(data["activities"]))
        else:
            sections.append("未生成教学活动")
            
        # 评估方案
        sections.append("\n## 四、评估方案")
        if "assessment" in data:
            sections.append(format_assessment(data["assessment"]))
        else:
            sections.append("未生成评估方案")
        
        return "\n".join(sections)
        
    except Exception as e:
        error_msg = f"格式化输出时发生错误: {str(e)}"
        print(error_msg)
        return error_msg 
