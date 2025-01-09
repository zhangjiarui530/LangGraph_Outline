from typing import Dict, Any, List, Optional
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
import json

def design_objectives(content: Dict[str, Any], total_hours: int, grade: str, subject: str) -> str:
    """基于目录设计教学目标"""
    try:
        # 将字符串解析为字典
        try:
            content_dict = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return generate_objectives(content, total_hours, grade, subject)
        
        # 获取目录内容
        toc_content = content_dict.get("toc_content", "")
        if not toc_content:
            print("未找到目录内容，将使用generate_objectives方法...")
            return generate_objectives(content, total_hours, grade, subject)
            
        print(f"成功获取目录内容，长度：{len(toc_content)}")
        
        # 获取单元信息
        units = content_dict.get("units", [])
        unit_count = content_dict.get("unit_count", 0)
        
        # 根据单元数调整目标数量，尽量保持一个单元一个目标
        knowledge_goals = unit_count  # 知识目标与单元一一对应
        process_goals = (unit_count + 1) // 2  # 每两个单元对应一个过程目标（向上取整）
        attitude_goals = (unit_count + 1) // 2  # 每两个单元对应一个态度目标（向上取整）
        competency_goals = (unit_count + 1) // 2  # 每两个单元对应一个核心素养目标（向上取整）
        
        # 获取LLM配置
        llm_config = get_llm()
        
        # 构建单元目标提示
        unit_goals_prompt = ""
        if units:
            unit_goals_prompt = "\n单元目标要求：\n"
            for i, unit in enumerate(units, 1):
                unit_goals_prompt += f"{i}. {unit}的教学目标应该体现该单元的特点和重点\n"
        
        prompt = f"""作为{subject}教师，请基于教材目录设计总课时为{total_hours}课时的教学目标。

请分析目录内容，设计简明扼要的教学目标：

### 知识目标（{knowledge_goals}个）
[每个单元列出1个核心知识目标，描述学生应掌握的关键知识点]

### 能力目标（{process_goals}个）
[列出培养的关键能力，每2个单元对应1个目标]

### 素养目标（{attitude_goals}个）
[列出培养的核心素养，每2个单元对应1个目标]

注意：
1. 目标要简洁明确，突出重点
2. 符合{grade}学生认知水平
3. 体现{subject}学科特点
4. 确保在{total_hours}课时内可完成

{unit_goals_prompt}

教材目录：
{toc_content}
"""
        
        print("\n=== 基于目录设计教学目标 ===")
        print("调用LLM设计目标...")
        
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": f"你是{subject}教师，请简明扼要地设计教学目标。"},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content
        print("目标设计完成")
        return result
        
    except Exception as e:
        print(f"错误：设计教学目标失败 - {str(e)}")
        raise ValueError(f"设计教学目标失败: {str(e)}")

def validate_objectives(objectives: Dict[str, Any]) -> None:
    """
    验证教学目标的格式和内容
    
    Args:
        objectives: 教学目标字典
        
    Raises:
        ValueError: 如果格式或内容不符合要求
    """
    # 检查基本结构
    if not isinstance(objectives, str):
        raise ValueError("教学目标必须是字符串类型")
        
    # 检查必要的章节标题
    required_sections = [
        "一、知识与技能目标",
        "二、过程与方法目标",
        "三、情感态度与价值观目标",
        "四、核心素养"
    ]
    
    for section in required_sections:
        if section not in objectives:
            raise ValueError(f"教学目标缺少{section}章节")
            
    # 检查内容长度
    if len(objectives) < 500:  # 假设至少需要500字的详细描述
        raise ValueError("教学目标内容过短，请提供更详细的描述")

def generate_objectives(content: Dict[str, Any], total_hours: int, grade: str, subject: str) -> str:
    """根据教材内容生成教学目标"""
    try:
        llm_config = get_llm()
        
        prompt = f"""作为{subject}教师，请基于教材内容设计总课时为{total_hours}课时的教学目标。

请分析教材内容，设计简明扼要的教学目标：

### 知识目标（4-5个）
[列出学生需要掌握的核心知识点]

### 能力目标（3-4个）
[列出培养的关键能力]

### 素养目标（2-3个）
[列出培养的核心素养]

注意：
1. 目标要简洁明确，突出重点
2. 符合{grade}学生认知水平
3. 体现{subject}学科特点
4. 确保在{total_hours}课时内可完成

教材内容：
{json.dumps(content, ensure_ascii=False, indent=2)}
"""
        
        print("\n=== 根据内容生成教学目标 ===")
        print("调用LLM生成目标...")
        
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": f"你是{subject}教师，请简明扼要地设计教学目标。"},
                {"role": "user", "content": prompt}
            ],
        )
        
        result = response.choices[0].message.content
        print("目标生成完成")
        return result
        
    except Exception as e:
        print(f"错误：生成教学目标失败 - {str(e)}")
        raise ValueError(f"生成教学目标失败: {str(e)}") 
