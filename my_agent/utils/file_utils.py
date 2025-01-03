import os
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
            
            # 知识与技能目标
            md_content.append("### 1. 知识与技能目标\n")
            if "knowledge_skill" in objectives:
                for obj in objectives["knowledge_skill"]:
                    md_content.append(f"- {obj['content']}")
                    md_content.append(f"  - 重要程度：{obj['importance']}")
                    md_content.append("  - 评价标准：")
                    for criteria in obj["evaluation_criteria"]:
                        md_content.append(f"    - {criteria}")
                    md_content.append("")
            
            # 过程与方法目标
            md_content.append("### 2. 过程与方法目标\n")
            if "process_method" in objectives:
                for obj in objectives["process_method"]:
                    md_content.append(f"- {obj['content']}")
                    md_content.append(f"  - 重要程度：{obj['importance']}")
                    md_content.append("  - 评价标准：")
                    for criteria in obj["evaluation_criteria"]:
                        md_content.append(f"    - {criteria}")
                    md_content.append("")
            
            # 情感态度与价值观目标
            md_content.append("### 3. 情感态度与价值观目标\n")
            if "emotion_attitude" in objectives:
                for obj in objectives["emotion_attitude"]:
                    md_content.append(f"- {obj['content']}")
                    md_content.append(f"  - 重要程度：{obj['importance']}")
                    md_content.append("  - 评价标准：")
                    for criteria in obj["evaluation_criteria"]:
                        md_content.append(f"    - {criteria}")
                    md_content.append("")
            
            # 核心素养
            if "core_literacy" in data["objectives"]:
                md_content.append("### 4. 核心素养\n")
                for literacy in data["objectives"]["core_literacy"]:
                    md_content.append(f"#### {literacy['name']}")
                    md_content.append(f"- 描述：{literacy['description']}")
                    md_content.append("- 相关目标：")
                    for obj in literacy["related_objectives"]:
                        md_content.append(f"  - {obj}")
                    md_content.append("")
        
        # 知识点分析部分
        md_content.append("## 二、知识点分析\n")
        if "knowledge_points" in data and "knowledge_points" in data["knowledge_points"]:
            kp = data["knowledge_points"]["knowledge_points"]
            
            # 基础知识点
            if "basic" in kp:
                md_content.append("### 1. 基础知识点\n")
                for point in kp["basic"]:
                    md_content.append(f"#### {point['name']}")
                    md_content.append(f"- 内容：{point['content']}")
                    md_content.append(f"- 难度：{point['difficulty']}")
                    md_content.append(f"- 重要程度：{point['importance']}")
                    md_content.append("- 前置知识点：")
                    for pre in point["prerequisites"]:
                        md_content.append(f"  - {pre}")
                    md_content.append("- 对应教学目标：")
                    for obj in point["objectives"]:
                        md_content.append(f"  - {obj}")
                    md_content.append(f"- 教学建议：{point['teaching_suggestions']}\n")
            
            # 拓展知识点
            if "advanced" in kp:
                md_content.append("### 2. 拓展知识点\n")
                for point in kp["advanced"]:
                    md_content.append(f"#### {point['name']}")
                    md_content.append(f"- 内容：{point['content']}")
                    md_content.append(f"- 难度：{point['difficulty']}")
                    md_content.append(f"- 重要程度：{point['importance']}")
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
                for idx, activity in enumerate(activities["activities"], 1):
                    md_content.append(f"#### 活动{idx}：{activity['name']}")
                    md_content.append(f"- 类型：{activity['type']}")
                    md_content.append(f"- 内容：{activity['content']}")
                    md_content.append(f"- 课时：{activity['duration']}")
                    md_content.append("- 教学目标：")
                    for obj in activity["objectives"]:
                        md_content.append(f"  - {obj}")
                    md_content.append("- 重点：")
                    for point in activity["key_points"]:
                        md_content.append(f"  - {point}")
                    md_content.append("- 难点：")
                    for point in activity["difficult_points"]:
                        md_content.append(f"  - {point}")
                    md_content.append("- 教学方法：")
                    for method in activity["methods"]:
                        md_content.append(f"  - {method}")
                    md_content.append(f"- 学生参与：{activity['student_participation']}")
                    md_content.append("- 预期效果：")
                    for outcome in activity["expected_outcomes"]:
                        md_content.append(f"  - {outcome}")
                    md_content.append(f"- 课后作业：{activity['homework']}")
                    md_content.append("- 延伸活动：")
                    for ext in activity["extensions"]:
                        md_content.append(f"  - {ext}")
                    md_content.append("")
        
        # 评估方案部分
        md_content.append("## 四、评估方案\n")
        if "assessment" in data and "assessment_plan" in data["assessment"]:
            plan = data["assessment"]["assessment_plan"]
            
            # 形成性评估
            if "formative" in plan:
                md_content.append("### 1. 形成性评估\n")
                for assessment in plan["formative"]:
                    md_content.append(f"#### {assessment['name']}")
                    md_content.append(f"- 内容：{assessment['content']}")
                    md_content.append(f"- 方式：{assessment['method']}")
                    md_content.append("- 评估标准：")
                    for criteria in assessment["criteria"]:
                        md_content.append(f"  - {criteria}")
                    md_content.append(f"- 分值：{assessment['score']}")
                    md_content.append(f"- 时间：{assessment['timing']}")
                    md_content.append(f"- 注意事项：{assessment['notes']}\n")
            
            # 终结性评估
            if "summative" in plan:
                md_content.append("### 2. 终结性评估\n")
                for assessment in plan["summative"]:
                    md_content.append(f"#### {assessment['name']}")
                    md_content.append(f"- 内容：{assessment['content']}")
                    md_content.append(f"- 方式：{assessment['method']}")
                    md_content.append("- 评估标准：")
                    for criteria in assessment["criteria"]:
                        md_content.append(f"  - {criteria}")
                    md_content.append(f"- 分值：{assessment['score']}")
                    md_content.append(f"- 时间：{assessment['timing']}")
                    md_content.append(f"- 注意事项：{assessment['notes']}\n")
            
            # 评估权重
            if "weight" in plan:
                md_content.append("### 3. 评估权重\n")
                weight = plan["weight"]
                md_content.append(f"- 形成性评价：{weight['formative']}")
                md_content.append(f"- 终结性评价：{weight['summative']}\n")
            
            # 反馈方法
            if "feedback_methods" in data["assessment"]:
                md_content.append("### 4. 反馈方法\n")
                for feedback in data["assessment"]["feedback_methods"]:
                    md_content.append(f"#### {feedback['type']}")
                    md_content.append(f"- 描述：{feedback['description']}")
                    md_content.append(f"- 时机：{feedback['timing']}")
                    md_content.append(f"- 形式：{feedback['format']}\n")
        
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
