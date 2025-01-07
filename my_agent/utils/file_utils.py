import os
from typing import Dict, Any
import json
from datetime import datetime
from .output_formatter import (
    format_meta_info,
    format_objectives,
    format_core_literacy,
    format_knowledge_points,
    format_activities,
    format_assessment
)

def load_json(file_path: str) -> Dict[str, Any]:
    """读取JSON文件
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        Dict[str, Any]: JSON数据
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: Dict[str, Any], file_path: str) -> None:
    """保存JSON文件
    
    Args:
        data: 要保存的数据
        file_path: 保存路径
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_markdown(content: str, file_path: str) -> None:
    """保存Markdown文件
    
    Args:
        content: Markdown内容
        file_path: 保存路径
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def save_lesson_plan_to_md(data: Dict[str, Any], course_name: str) -> None:
    """将教学大纲保存为Markdown和JSON文件
    
    Args:
        data: 教学大纲数据
        course_name: 课程名称
    """
    try:
        # 创建输出目录
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "my_agent", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{course_name}_教学大纲_{timestamp}"
        json_path = os.path.join(output_dir, f"{base_name}.json")
        md_path = os.path.join(output_dir, f"{base_name}.md")
        
        # 保存JSON文件
        save_json(data, json_path)
        print(f"JSON文件已保存: {json_path}")
        
        # 生成Markdown内容
        md_content = []
        
        # 添加标题
        md_content.append(f"# {course_name}教学大纲\n")
        
        # 添加基本信息
        md_content.append("## 一、基本信息\n")
        meta_info = data.get("meta_info", {})
        md_content.append(format_meta_info(meta_info))
        
        # 添加教学目标
        md_content.append("## 二、教学目标\n")
        objectives = data.get("teaching_objectives", {})
        md_content.append(format_objectives(objectives))
        
        # 添加核心素养
        md_content.append("## 三、核心素养\n")
        literacy = data.get("core_literacy", [])
        md_content.append(format_core_literacy(literacy))
        
        # 添加知识点
        md_content.append("## 四、知识点\n")
        knowledge = data.get("knowledge_points", {})
        md_content.append(format_knowledge_points(knowledge))
        
        # 添加教学活动
        md_content.append("## 五、教学活动\n")
        activities = data.get("teaching_activities", {})
        md_content.append(format_activities(activities))
        
        # 添加评估方案
        md_content.append("## 六、评估方案\n")
        assessment = data.get("assessment_plan", {})
        md_content.append(format_assessment(assessment))
        
        # 保存Markdown文件
        save_markdown("\n".join(md_content), md_path)
        print(f"Markdown文件已保存: {md_path}")
        
    except Exception as e:
        print(f"错误：保存教学大纲失败 - {str(e)}")
        raise

def ensure_dir(path: str) -> None:
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(path):
        os.makedirs(path)

def get_file_extension(file_path: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(file_path)[1].lower()

def is_valid_pdf(file_path: str) -> bool:
    """检查是否是有效的PDF文件"""
    if not os.path.exists(file_path):
        return False
    if not file_path.lower().endswith('.pdf'):
        return False
    return True 
