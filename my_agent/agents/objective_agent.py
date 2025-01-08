from typing import Dict, Any, List, Optional
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
from my_agent.utils.pdf_utils import extract_toc_content
import json

def design_objectives(content: str, total_hours: int, grade: str, subject: str) -> str:
    """基于目录设计教学目标"""
    try:
        # 将字符串解析为字典
        try:
            content_dict = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return generate_objectives(content, total_hours, grade, subject)
        
        # 提取目录内容
        toc_content = extract_toc_content(content_dict)
        if not toc_content:
            print("未找到目录内容，将使用generate_objectives方法...")
            return generate_objectives(content, total_hours, grade, subject)
            
        print(f"成功提取目录内容，长度：{len(toc_content)}")
        
        # 计算单元数量
        import re
        unit_count = 0
        chapter_count = 0
        units = []  # 存储单元名称
        
        for line in toc_content.split('\n'):
            # 匹配单元标题
            unit_match = re.search(r'第[一二三四五六七八九十\d]+单元[^，。；]*', line)
            if unit_match:
                unit_count += 1
                units.append(unit_match.group())
            # 如果没有单元，匹配章节
            elif re.search(r'第[一二三四五六七八九十\d]+章', line):
                chapter_count += 1
        
        # 如果没有找到单元，使用章节作为单元
        if unit_count == 0:
            unit_count = chapter_count
            print(f"未找到单元，使用章节数：{chapter_count}")
            
        if unit_count == 0:
            print("未找到单元或章节数量，将使用默认值")
            unit_count = 6  # 默认值
            
        print(f"检测到单元数量：{unit_count}")
        if units:
            print("单元列表：")
            for unit in units:
                print(f"  - {unit}")
        
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
        
        prompt = f"""作为一名资深的{subject}教师，请基于教材目录设计总课时为{total_hours}课时的教学目标体系。

请首先分析目录中的以下要素：
1. 教材的整体编排思路（各单元主题、内容类型、难度分布）
2. 教学内容的时间分配（考虑{total_hours}课时的合理分配）
3. {subject}学科的能力要求（符合{grade}学生特点）
4. 核心素养的培养路径（结合{subject}学科特点）
{unit_goals_prompt}
然后基于以上分析，设计教学目标。要求：
1. 输出采用markdown格式，结构清晰，层次分明，全部使用中文
2. 目标体系应包含以下部分：

### 知识与技能目标

[此处列出{knowledge_goals}个具体目标（每个单元对应一个目标），每个目标包含：
- **目标描述**：具体说明学生应该掌握的知识和技能
- **重要程度**：高/中/低
- **对应单元**：该目标对应的具体单元
- **课时安排**：完成该目标需要的课时数
- **评价标准**：2-3个具体的评估标准]

### 过程与方法目标

[此处列出{process_goals}个具体目标（每2个单元对应一个目标），每个目标包含：
- **目标描述**：具体说明要培养的学习方法和思维能力
- **重要程度**：高/中/低
- **实现途径**：通过哪些单元内容实现
- **课时安排**：相关活动的课时分配
- **评价标准**：2-3个具体的评估标准]

### 情感态度与价值观目标

[此处列出{attitude_goals}个具体目标（每2个单元对应一个目标），每个目标包含：
- **目标描述**：具体说明要培养的情感态度和价值取向
- **重要程度**：高/中/低
- **培养载体**：通过哪些单元内容培养
- **渗透方式**：在教学过程中如何渗透
- **评价标准**：2-3个具体的评估标准]

### 核心素养

[此处列出{competency_goals}个核心素养（每2个单元对应一个素养），每个素养包含：
- **素养描述**：该素养的具体内容
- **对应单元**：该素养在哪些单元中培养
- **实现路径**：如何通过教学活动培养该素养
- **课时分配**：在总课时中的分配比例]

注意事项：
1. 目标设计要与课时安排相匹配，确保在{total_hours}课时内可以完成
2. 目标要符合{grade}学生的认知水平和{subject}学科特点
3. 目标之间要体现递进关系和内在联系
4. 评价标准要具体、可测量、可操作
5. 各类目标的课时分配要合理，确保总和为{total_hours}课时

教材目录如下：
{toc_content}
"""
        
        print("\n=== 基于目录设计教学目标 ===")
        print("调用LLM设计目标...")
        
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": f"你是一个专业的{subject}教师，擅长设计教学目标。你的设计要符合新课标要求，体现{subject}学科特点和{grade}学生特点。"},
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
        
        prompt = f"""作为一名资深的{subject}教师，请基于教材内容设计总课时为{total_hours}课时的教学目标体系。

请首先分析教材内容的以下要素：
1. 教材的知识点分布（重点、难点、基础点）
2. 教学内容的时间需求（考虑{total_hours}课时的合理分配）
3. {subject}学科的能力培养（符合{grade}学生特点）
4. 学习难度的递进关系（适应{grade}学生认知规律）

然后基于以上分析，设计教学目标。要求：
1. 输出采用markdown格式，结构清晰，层次分明，全部使用中文
2. 目标体系应包含以下部分：

### 知识与技能目标

[此处结合教材内容和{total_hours}课时安排，列出5-6个具体目标，每个目标包含：
- **目标描述**：具体说明学生应该掌握的知识和技能
- **重要程度**：高/中/低
- **对应内容**：该目标对应的具体教材内容
- **课时安排**：完成该目标需要的课时数
- **评价标准**：2-3个具体的评估标准]

### 过程与方法目标

[此处结合{subject}学科特点，列出3-4个具体目标，每个目标包含：
- **目标描述**：具体说明要培养的学习方法和思维能力
- **重要程度**：高/中/低
- **实现途径**：通过哪些教学内容实现
- **课时安排**：相关活动的课时分配
- **评价标准**：2-3个具体的评估标准]

### 情感态度与价值观目标

[此处结合{grade}学生特点，列出3-4个具体目标，每个目标包含：
- **目标描述**：具体说明要培养的情感态度和价值取向
- **重要程度**：高/中/低
- **培养载体**：通过哪些教学内容培养
- **渗透方式**：在教学过程中如何渗透
- **评价标准**：2-3个具体的评估标准]

### 核心素养

[此处结合{subject}学科核心素养，列出4个核心素养，每个素养包含：
- **素养描述**：该素养的具体内容
- **培养内容**：通过哪些教材内容培养
- **实现路径**：如何通过教学活动培养该素养
- **课时分配**：在总课时中的分配比例]

注意事项：
1. 目标设计要与课时安排相匹配，确保在{total_hours}课时内可以完成
2. 目标要符合{grade}学生的认知水平和{subject}学科特点
3. 目标之间要体现递进关系和内在联系
4. 评价标准要具体、可测量、可操作
5. 各类目标的课时分配要合理，确保总和为{total_hours}课时

教材内容如下：
{content}
"""
        
        print("\n=== 根据内容生成教学目标 ===")
        print("调用LLM生成目标...")
        
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": f"你是一个专业的{subject}教师，擅长设计教学目标。你的设计要符合新课标要求，体现{subject}学科特点和{grade}学生特点。"},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content
        print("目标生成完成")
        return result
        
    except Exception as e:
        print(f"错误：生成教学目标失败 - {str(e)}")
        raise ValueError(f"生成教学目标失败: {str(e)}") 
