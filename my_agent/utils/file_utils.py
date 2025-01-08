import os
from typing import Dict, Any, Union
import json
from datetime import datetime
from .output_formatter import (
    format_meta_info,
    format_objectives,
    format_knowledge_points,
    format_activities,
    format_assessment,
    format_markdown
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

def save_lesson_plan_to_md(data: Union[Dict[str, Any], str], course_name: str, textbook_name: str = "") -> None:
    """将教学大纲保存为Markdown文件
    
    Args:
        data: 教学大纲数据，可以是字典或字符串
        course_name: 课程名称
        textbook_name: 教材名称
    """
    try:
        # 创建输出目录
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "my_agent", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 如果有教材名称，添加到文件名中
        if textbook_name:
            md_path = os.path.join(output_dir, f"{course_name}_{textbook_name}_教学大纲_{timestamp}.md")
        else:
            md_path = os.path.join(output_dir, f"{course_name}_教学大纲_{timestamp}.md")
        
        # 如果输入是字符串，直接使用；否则使用format_markdown生成内容
        if isinstance(data, str):
            md_content = data
        else:
            md_content = format_markdown(data, course_name)
        
        # 保存Markdown文件
        save_markdown(md_content, md_path)
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
