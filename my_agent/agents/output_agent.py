from typing import Dict, Any
import time
from my_agent.utils.file_utils import save_lesson_plan_to_md

def save_output(state: Dict[str, Any]) -> Dict[str, Any]:
    """保存教学大纲输出
    
    Args:
        state: 包含以下字段的状态字典：
            - objectives: 教学目标
            - knowledge_points: 知识点分析
            - activities: 教学活动
            - assessment: 评估方案
            - grade: 年级
            - subject: 学科
            - textbook_content: 教材内容（可选）
            
    Returns:
        Dict[str, Any]: 处理结果，包含消息、最终大纲和具体内容
    """
    try:
        print("\n=== 保存输出 ===")
        
        # 确保所有必要的状态都存在
        required_fields = ["objectives", "knowledge_points", "activities", "assessment", "grade", "subject"]
        for field in required_fields:
            if field not in state or not state[field]:
                raise ValueError(f"缺少必要的状态字段: {field}")
        
        # 获取课程名称和教材名称
        subject = state["subject"]
        textbook_content = state.get("textbook_content", {})
        textbook_name = textbook_content.get("title", "").replace(".pdf", "")  # 从PDF文件名中提取教材名称
        
        # 处理评估方案的表格格式
        assessment_content = state["assessment"]
        # 确保表格的分隔线正确显示
        assessment_content = assessment_content.replace("\n|", "\n|")  # 确保每行表格都从|开始
        assessment_content = assessment_content.replace("|-", "|---")  # 确保分隔线足够长
        
        # 合并所有输出内容
        final_outline = f"""# {textbook_name if textbook_name else subject}教学大纲

## 一、教学目标
{state["objectives"]}

## 二、知识点分析
{state["knowledge_points"]}

## 三、教学活动
{state["activities"]}

## 四、评估方案
{assessment_content}
"""
        
        # print("生成的final_outline:", final_outline)  # 添加调试日志
        
        # 保存到文件
        save_lesson_plan_to_md(final_outline, subject, textbook_name)
        
        return {
            "messages": ["教学大纲已保存"],
            "final_outline": final_outline,
            "objectives": state["objectives"],
            "knowledge_points": state["knowledge_points"],
            "activities": state["activities"],
            "assessment": assessment_content
        }
        
    except Exception as e:
        print(f"错误：保存输出失败 - {str(e)}")
        raise ValueError(f"保存输出失败: {str(e)}") 