import os
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