import os
<<<<<<< HEAD
from typing import Dict, Any
import json
from datetime import datetime

def save_lesson_plan_to_md(data: Dict[str, Any], course_name: str) -> None:
    """将教学大纲保存为Markdown格式"""
    try:
        # 创建输出目录
        output_dir = os.path.join("my_agent", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{course_name}_教学大纲_{timestamp}"
        md_path = os.path.join(output_dir, f"{base_name}.md")
        json_path = os.path.join(output_dir, f"{base_name}.json")
        
        # 保存JSON文件（用于调试和数据保存）
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        # 生成Markdown内容
        md_content = [f"# {course_name}教学大纲\n"]
        
        # 教学目标部分
        md_content.append("## 一、教学目标\n")
        if "objectives" in data and "objectives" in data["objectives"]:
            objectives = data["objectives"]["objectives"]
            
            # 知识目标
            md_content.append("### 1. 知识目标\n")
            if "knowledge" in objectives:
                for obj in objectives["knowledge"]:
                    md_content.append(f"- {obj['description']}")
                    md_content.append(f"  - 层次：{obj['level']}")
                    md_content.append(f"  - 评价标准：{obj['evaluation']}\n")
            
            # 能力目标
            md_content.append("### 2. 能力目标\n")
            if "ability" in objectives:
                for obj in objectives["ability"]:
                    md_content.append(f"- {obj['description']}")
                    md_content.append(f"  - 层次：{obj['level']}")
                    md_content.append(f"  - 评价标准：{obj['evaluation']}\n")
            
            # 素养目标
            md_content.append("### 3. 素养目标\n")
            if "emotion" in objectives:
                for obj in objectives["emotion"]:
                    md_content.append(f"- {obj['description']}")
                    md_content.append(f"  - 层次：{obj['level']}")
                    md_content.append(f"  - 评价标准：{obj['evaluation']}\n")
        
        # 知识点分析部分
        md_content.append("## 二、知识点分析\n")
        if "knowledge_points" in data and isinstance(data["knowledge_points"], dict):
            kp = data["knowledge_points"].get("knowledge_points", {})
            
            # 基础知识点
            if "basic" in kp:
                md_content.append("### 1. 基础知识点\n")
                for point in kp["basic"]:
                    md_content.append(f"#### {point['name']}")
                    md_content.append(f"- 内容：{point['content']}")
                    md_content.append(f"- 难度：{point['difficulty']}")
                    md_content.append(f"- 重要性：{point['importance']}")
                    md_content.append("- 前置知识点：")
                    for pre in point["prerequisites"]:
                        md_content.append(f"  - {pre}")
                    md_content.append("- 对应教学目标：")
                    for obj in point["objectives"]:
                        md_content.append(f"  - {obj}")
                    md_content.append(f"- 教学建议：{point['teaching_suggestions']}\n")
            
            # 高级知识点
            if "advanced" in kp:
                md_content.append("### 2. 高级知识点\n")
                for point in kp["advanced"]:
                    md_content.append(f"#### {point['name']}")
                    md_content.append(f"- 内容：{point['content']}")
                    md_content.append(f"- 难度：{point['difficulty']}")
                    md_content.append(f"- 重要性：{point['importance']}")
                    md_content.append("- 前置知识点：")
                    for pre in point["prerequisites"]:
                        md_content.append(f"  - {pre}")
                    md_content.append("- 对应教学目标：")
                    for obj in point["objectives"]:
                        md_content.append(f"  - {obj}")
                    md_content.append(f"- 教学建议：{point['teaching_suggestions']}\n")
            
            # 重点和难点
            if "key_points" in kp:
                md_content.append("### 3. 教学重点\n")
                for point in kp["key_points"]:
                    md_content.append(f"- {point}\n")
            
            if "difficult_points" in kp:
                md_content.append("### 4. 教学难点\n")
                for point in kp["difficult_points"]:
                    md_content.append(f"- {point}\n")
        
        # 教学活动部分
        md_content.append("## 三、教学活动\n")
        if "activities" in data:
            activities = data["activities"]
            
            # 课时分配
            if "time_allocation" in activities:
                md_content.append("### 1. 课时分配\n")
                time = activities["time_allocation"]
                md_content.append(f"- 知识讲解：{time['knowledge']}课时")
                md_content.append(f"- 技能训练：{time['skill']}课时")
                md_content.append(f"- 实践活动：{time['practice']}课时")
                md_content.append(f"- 讨论交流：{time['discussion']}课时")
                md_content.append(f"- 评估考核：{time['assessment']}课时\n")
            
            # 具体活动
            if "activities" in activities:
                md_content.append("### 2. 具体活动\n")
                for idx, act in enumerate(activities["activities"], 1):
                    activity = act["activity"]
                    md_content.append(f"#### 活动{idx}：{activity['title']}")
                    md_content.append(f"- 时长：{activity['duration']}分钟")
                    md_content.append(f"- 教学重点：{activity['教学重点']}")
                    md_content.append(f"- 教学方法：{activity['教学方法']}")
                    
                    # 教学过程
                    md_content.append("- 教学过程：")
                    for phase, details in activity["教学过程"].items():
                        md_content.append(f"  - {phase}（{details['duration']}分钟）：")
                        md_content.append(f"    - 内容：{details['content']}")
                        md_content.append("    - 具体活动：")
                        for item in details["activities"]:
                            md_content.append(f"      - {item}")
                        md_content.append("    - 教学材料：")
                        for item in details["materials"]:
                            md_content.append(f"      - {item}")
                    
                    md_content.append(f"- 设计亮点：{activity['设计亮点']}")
                    md_content.append(f"- 预期效果：{activity['预期效果']}")
                    md_content.append(f"- 可能问题：{activity['可能问题']}")
                    md_content.append(f"- 对应章节：{activity['对应章节']}\n")
        
        # 评估方案部分
        md_content.append("## 四、评估方案\n")
        if "assessment" in data and "assessment_plan" in data["assessment"]:
            plan = data["assessment"]["assessment_plan"]
            
            # 形成性评估
            if "formative" in plan:
                md_content.append("### 1. 形成性评估\n")
                for assessment in plan["formative"]:
                    md_content.append(f"#### {assessment['name']}")
                    md_content.append(f"- 类型：{assessment['type']}")
                    md_content.append(f"- 描述：{assessment['description']}")
                    md_content.append("- 对应教学目标：")
                    for obj in assessment["objectives"]:
                        md_content.append(f"  - {obj}")
                    md_content.append("- 对应知识点：")
                    for kp in assessment["knowledge_points"]:
                        md_content.append(f"  - {kp}")
                    md_content.append("- 评分标准：")
                    for grade, criteria in assessment["criteria"].items():
                        md_content.append(f"  - {grade}：{criteria}")
                    md_content.append(f"- 权重：{assessment['weight']}")
                    md_content.append(f"- 实施时间：{assessment['timing']}")
                    md_content.append("- 评估工具：")
                    for tool in assessment["tools"]:
                        md_content.append(f"  - {tool}")
                    md_content.append(f"- 反馈方式：{assessment['feedback']}\n")
            
            # 终结性评估
            if "summative" in plan:
                md_content.append("### 2. 终结性评估\n")
                for assessment in plan["summative"]:
                    md_content.append(f"#### {assessment['name']}")
                    md_content.append(f"- 类型：{assessment['type']}")
                    md_content.append(f"- 描述：{assessment['description']}")
                    md_content.append("- 对应教学目标：")
                    for obj in assessment["objectives"]:
                        md_content.append(f"  - {obj}")
                    md_content.append("- 对应知识点：")
                    for kp in assessment["knowledge_points"]:
                        md_content.append(f"  - {kp}")
                    md_content.append("- 评分标准：")
                    for grade, criteria in assessment["criteria"].items():
                        md_content.append(f"  - {grade}：{criteria}")
                    md_content.append(f"- 权重：{assessment['weight']}")
                    md_content.append(f"- 实施时间：{assessment['timing']}")
                    md_content.append("- 评估工具：")
                    for tool in assessment["tools"]:
                        md_content.append(f"  - {tool}")
                    md_content.append(f"- 反馈方式：{assessment['feedback']}\n")
            
            # 评估权重
            if "weights" in plan:
                md_content.append("### 3. 评估权重\n")
                weights = plan["weights"]
                md_content.append(f"- 形成性评估：{weights['formative']}")
                md_content.append(f"- 终结性评估：{weights['summative']}\n")
        
        # 保存Markdown文件
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_content))
            
        print(f"教学大纲已保存到：{md_path}")
        print(f"JSON数据已保存到：{json_path}")
        
    except Exception as e:
        raise ValueError(f"保存教学大纲失败: {str(e)}")

def ensure_dir(path: str) -> None:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
    """
    if not os.path.exists(path):
        os.makedirs(path)

def get_file_extension(file_path: str) -> str:
    """
    获取文件扩展名
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 文件扩展名
    """
    return os.path.splitext(file_path)[1].lower()

def is_valid_pdf(file_path: str) -> bool:
    """
    检查是否是有效的PDF文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 是否是有效的PDF文件
    """
    if not os.path.exists(file_path):
        return False
    if not file_path.lower().endswith('.pdf'):
        return False
    return True 
=======
from datetime import datetime

def save_lesson_plan_to_md(content: str, course_name: str) -> str:
    """
    将教学大纲保存为markdown文件
    
    Args:
        content: 教学大纲内容
        course_name: 课程名称
        
    Returns:
        str: 保存的文件路径
    """
    # 创建downloads目录（如果不存在）
    download_dir = "downloads"
    os.makedirs(download_dir, exist_ok=True)
    
    # 生成文件名（使用时间戳避免重名）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{course_name}_教学大纲_{timestamp}.md"
    filepath = os.path.join(download_dir, filename)
    
    # 写入文件
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filepath 
>>>>>>> c4972e73ce82ab596751226cd0a07e233d3db998
