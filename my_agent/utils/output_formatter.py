from typing import Dict, Any, List, Union

def format_objectives(objectives: Union[Dict[str, List[str]], List[Dict[str, str]]]) -> str:
    """
    格式化教学目标
    支持两种格式：
    1. 字典格式：{'知识': ['目标1', '目标2'], '能力': ['目标1', '目标2']}
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
            for category, goals in objectives.items():
                if category == "teaching_objectives":  # 处理嵌套的teaching_objectives
                    if isinstance(goals, dict):
                        for sub_category, sub_goals in goals.items():
                            if isinstance(sub_goals, list):
                                result.append(f"\n### {sub_category}目标")
                                for goal in sub_goals:
                                    result.append(f"- {goal}")
                    continue
                
                if not isinstance(goals, list):
                    print(f"警告：目标列表格式错误，期望列表，实际是{type(goals)}")
                    continue
                    
                result.append(f"\n### {category}目标")
                for goal in goals:
                    result.append(f"- {goal}")
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

def format_knowledge_points(points: List[Any]) -> str:
    """格式化知识点"""
    try:
        result = []
        
        if not points:
            return "暂无知识点"
            
        if isinstance(points, list):
            # 如果是简单的知识点列表
            if all(isinstance(p, str) for p in points):
                for point in points:
                    result.append(f"- {point}")
            # 如果是复杂的知识点对象列表
            else:
                current_category = None
                for point in points:
                    if not isinstance(point, dict):
                        continue
                        
                    category = point.get('category')
                    if category != current_category:
                        current_category = category
                        if category:
                            result.append(f"\n### {category}")
                    
                    name = point.get('name')
                    if name:
                        result.append(f"\n#### {name}")
                        
                    attrs = point.get('attributes', {})
                    if isinstance(attrs, dict):
                        for key, value in attrs.items():
                            result.append(f"- {key}：{value}")
                            
                    content = point.get('content')
                    if content:
                        result.append(f"- {content}")
                        
                    result.append("")  # 添加空行分隔
                    
        return "\n".join(result)
        
    except Exception as e:
        print(f"警告：格式化知识点时出错：{str(e)}")
        return "格式化知识点失败"

def format_activities(activities: List[Dict[str, Any]]) -> str:
    """格式化教学活动"""
    try:
        result = []
        
        if not activities:
            return "暂无教学活动"
            
        for activity in activities:
            # 如果是简单活动
            if isinstance(activity, str):
                result.append(f"\n### {activity}")
                continue
                
            # 如果是复杂活动对象
            if not isinstance(activity, dict):
                continue
                
            # 获取活动数据
            act = activity.get('activity', activity)  # 支持直接的活动数据
            if not act:
                continue
                
            # 添加标题
            title = act.get('title', '未命名活动')
            result.append(f"\n### {title}")
            
            # 添加基本信息
            duration = act.get('duration', '未指定')
            result.append(f"时长：{duration}")
            
            # 格式化教学重点
            teaching_focus = act.get('教学重点', act.get('teaching_focus', '待补充'))
            result.append(f"\n1. 教学重点：{teaching_focus}")
            
            # 格式化教学方法
            teaching_method = act.get('教学方法', act.get('teaching_method', '待补充'))
            result.append(f"2. 教学方法：{teaching_method}")
            
            # 格式化教学过程
            result.append("3. 教学过程：")
            process = act.get('教学过程', act.get('teaching_process', {}))
            if isinstance(process, dict):
                for phase, phase_data in process.items():
                    if isinstance(phase_data, dict):
                        result.append(f"   - {phase}：{phase_data.get('content', '待补充')}")
                        # 添加具体活动
                        activities_list = phase_data.get('activities', [])
                        if activities_list:
                            result.append("     具体活动：")
                            for item in activities_list:
                                result.append(f"     * {item}")
                        # 添加教学材料
                        materials = phase_data.get('materials', [])
                        if materials:
                            result.append("     教学材料：")
                            for material in materials:
                                result.append(f"     * {material}")
                    else:
                        result.append(f"   - {phase}：{phase_data if phase_data else '待补充'}")
            
            # 添加其他信息
            for key in ['设计亮点', '预期效果', '可能问题', '对应章节']:
                value = act.get(key, '待补充')
                result.append(f"\n{len(result)+1}. {key}：{value}")
            
            # 添加空行分隔
            result.append("")
        
        return "\n".join(result)
        
    except Exception as e:
        print(f"警告：格式化教学活动时出错：{str(e)}")
        return "格式化教学活动失败"

def format_assessment(assessment: Dict[str, Any]) -> str:
    """格式化评估方案"""
    result = ["\n### 过程性评价（占比60%）"]
    
    # 格式化过程性评价
    process = assessment.get('process_assessment', {}).get('items', {})
    for name, item in process.items():
        result.append(f"\n#### {name}（{item.get('percentage', '0')}%）")
        details = item.get('details', {})
        for key, value in details.items():
            result.append(f"- {key}：{value}")
        
        # 添加评价标准
        if item.get('evaluation_criteria'):
            result.append("\n评价标准：")
            for criterion in item['evaluation_criteria']:
                result.append(f"- {criterion}")
        
        # 添加评价工具
        if item.get('evaluation_tools'):
            result.append("\n评价工具：")
            for tool in item['evaluation_tools']:
                result.append(f"- {tool.get('type', '未知类型')}：{tool.get('method', '待补充')}")
    
    result.append("\n### 终结性评价（占比40%）")
    
    # 格式化终结性评价
    final = assessment.get('final_assessment', {}).get('items', {})
    for name, item in final.items():
        result.append(f"\n#### {name}（{item.get('percentage', '0')}%）")
        details = item.get('details', {})
        for key, value in details.items():
            result.append(f"- {key}：{value}")
        
        # 添加评价标准
        if item.get('evaluation_criteria'):
            result.append("\n评价标准：")
            for criterion in item['evaluation_criteria']:
                result.append(f"- {criterion}")
        
        # 添加评价工具
        if item.get('evaluation_tools'):
            result.append("\n评价工具：")
            for tool in item['evaluation_tools']:
                result.append(f"- {tool.get('type', '未知类型')}：{tool.get('method', '待补充')}")
    
    # 格式化反馈机制
    result.append("\n### 评价反馈机制")
    feedback = assessment.get('feedback_mechanism', {})
    
    # 格式化即时反馈
    immediate = feedback.get('immediate', {})
    if immediate:
        result.append("\n#### 即时反馈")
        for key, value in immediate.items():
            result.append(f"- {key}：{value}")
    
    # 格式化总结性反馈
    summary = feedback.get('summary', {})
    if summary:
        result.append("\n#### 总结性反馈")
        for key, value in summary.items():
            result.append(f"- {key}：{value}")
    
    return "\n".join(result)

def format_final_output(data: Dict[str, Any]) -> str:
    """格式化最终输出"""
    try:
        # 获取教学目标
        teaching_objectives = data.get('teaching_objectives', {})
        if not teaching_objectives:
            print("警告：未找到教学目标数据")
            teaching_objectives = {}
            
        # 获取总课时
        total_hours = data.get('total_hours', 0)
        if not total_hours:
            print("警告：未找到总课时数据")
            
        # 获取教学活动
        activities = data.get('teaching_activities', {})
        if not isinstance(activities, dict):
            print(f"警告：教学活动格式错误，期望字典，实际是{type(activities)}")
            activities = {}
            
        # 获取时间分配
        time_allocation = activities.get('time_allocation', {})
        if not isinstance(time_allocation, dict):
            print(f"警告：时间分配格式错误，期望字典，实际是{type(time_allocation)}")
            time_allocation = {}
            
        # 构建输出
        sections = [
            "# 教学大纲",
            "\n## 1. 教学目标",
            format_objectives(teaching_objectives),
            "\n## 2. 教学内容与课时安排",
            f"\n### 总课时数：{total_hours}课时",
            "\n### 课时分配"
        ]
        
        # 添加课时分配
        if time_allocation:
            sections.extend([
                "- 知识讲解：{:.1f} 课时".format(time_allocation.get('knowledge', 0)),
                "- 技能训练：{:.1f} 课时".format(time_allocation.get('skill', 0)),
                "- 实践活动：{:.1f} 课时".format(time_allocation.get('practice', 0)),
                "- 研讨交流：{:.1f} 课时".format(time_allocation.get('discussion', 0)),
                "- 测评评估：{:.1f} 课时".format(time_allocation.get('assessment', 0))
            ])
        else:
            sections.append("暂无课时分配数据")
            
        # 添加知识点
        knowledge_points = data.get('knowledge_points', [])
        sections.extend([
            "\n### 知识点体系",
            format_knowledge_points(knowledge_points)
        ])
        
        # 添加教学活动
        activity_list = activities.get('activities', [])
        sections.extend([
            "\n## 3. 教学活动",
            format_activities(activity_list)
        ])
        
        # 添加评估方案
        assessment_plan = data.get('assessment_plan', {})
        sections.extend([
            "\n## 4. 评估方案",
            format_assessment(assessment_plan)
        ])
        
        # 合并所有部分
        return "\n".join(sections)
        
    except Exception as e:
        error_msg = f"格式化输出时发生错误: {str(e)}"
        print(error_msg)
        return error_msg 