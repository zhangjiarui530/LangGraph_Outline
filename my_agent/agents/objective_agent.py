from typing import Dict, Any, List, Optional
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
import json

def extract_toc_content(content: Dict[str, Any]) -> str:
    """从教材内容中提取目录部分
    
    Args:
        content: 教材内容字典
        
    Returns:
        str: 目录内容
    """
    try:
        if not content or not isinstance(content, dict):
            return ""
            
        chapters = content.get("chapters", [])
        if not chapters:
            return ""
            
        # 只检查前10页
        max_pages = min(10, len(chapters))
        
        # 目录的常见标识
        toc_indicators = [
            "目录",
            "contents",
            "table of contents"
        ]
        
        # 提取目录内容
        toc_content = []
        in_toc = False
        
        for chapter in chapters[:max_pages]:
            text = chapter.get("content", "").lower()  # 转换为小写以便比较
            
            # 检查是否进入目录部分
            if not in_toc:
                for indicator in toc_indicators:
                    if indicator in text:
                        in_toc = True
                        toc_content.append(chapter.get("content", ""))  # 保留原始文本
                        break
            else:
                # 检查是否已经离开目录部分（通过检测是否出现正文、前言等标识）
                if any(x in text for x in ["第一章", "前言", "绪论", "正文", "第一单元", "第一节", "第一课"]):
                    break
                toc_content.append(chapter.get("content", ""))  # 保留原始文本
                
        return "\n".join(toc_content)
        
    except Exception as e:
        print(f"提取目录内容失败: {str(e)}")
        return ""

def design_objectives(content: str, total_hours: int, grade: str = "7年级", subject: str = "语文") -> Dict[str, Any]:
    """设计教学目标
    
    Args:
        content: 教材内容的JSON字符串
        total_hours: 总课时数
        grade: 年级，默认为7年级
        subject: 学科，默认为语文
    """
    try:
        # 验证输入
        if not content:
            raise ValueError("内容为空")
            
        if not isinstance(total_hours, (int, float)) or total_hours <= 0:
            raise ValueError(f"总课时格式错误: {total_hours}")
            
        try:
            # 解析内容为字典
            content_dict = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析失败: {str(e)}")
            
        # 提取目录内容
        toc_content = extract_toc_content(content_dict)
        if not toc_content:
            raise ValueError("未找到有效的目录内容")
            
        # print(f"提取的目录内容:\n{toc_content[:1000]}...")  # 打印前200个字符用于调试
            
        # 获取LLM配置
        llm_config = get_llm()
        
        # 构建提示词
        prompt = f"""作为一名资深的{subject}教师，请基于以下教材目录为{grade}学生设计教学目标。总课时为{total_hours}学时。

教材目录：
{toc_content}

请根据目录结构和内容，结合{subject}学科特点和{grade}学生的认知特点，设计以下几个方面的教学目标：
1. 知识与技能目标：基于目录反映的知识体系，设计学生应该掌握的具体知识和技能
2. 过程与方法目标：根据内容层次，设计学生应该掌握的学习方法和思维方式
3. 情感态度与价值观目标：结合课程主题，设计学生应该形成的情感态度和价值观

要求：
1. 目标要符合{grade}学生的认知水平和学习特点
2. 目标要体现{subject}学科的核心素养要求
3. 每个目标要具体、可测量、可达成
4. 要考虑{total_hours}课时的时间安排

请按以下格式输出：
{{
    "objectives": {{
        "knowledge_skill": [
            {{
                "content": "目标内容",
                "importance": "重要程度",
                "evaluation_criteria": ["评价标准1", "评价标准2"]
            }}
        ],
        "process_method": [
            {{
                "content": "目标内容",
                "importance": "重要程度",
                "evaluation_criteria": ["评价标准1", "评价标准2"]
            }}
        ],
        "emotion_attitude": [
            {{
                "content": "目标内容",
                "importance": "重要程度",
                "evaluation_criteria": ["评价标准1", "评价标准2"]
            }}
        ]
    }},
    "core_literacy": [
        {{
            "name": "素养名称",
            "description": "具体描述",
            "related_objectives": ["相关目标1", "相关目标2"]
        }}
    ]
}}"""

        print("\n=== 生成教学目标 ===")
        print(f"目录内容长度: {len(toc_content)}")
        print(f"年级: {grade}")
        print(f"学科: {subject}")
        print("调用LLM生成目标...")
        
        # 调用LLM
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": f"你是一个专业的{subject}教师，擅长基于教材目录设计整体教学目标。你的设计要符合新课标要求，体现{subject}学科特点和{grade}学生特点。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        # 解析响应
        try:
            result = response.choices[0].message.content
            if isinstance(result, str):
                result = json.loads(result)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM响应JSON解析失败: {str(e)}")
            
        # 验证结果
        if not isinstance(result, dict):
            raise ValueError(f"结果格式错误: {type(result)}")
            
        if "objectives" not in result:
            raise ValueError("缺少objectives字段")
            
        objectives = result["objectives"]
        if not isinstance(objectives, dict):
            raise ValueError(f"objectives格式错误: {type(objectives)}")
            
        for key in ["knowledge_skill", "process_method", "emotion_attitude"]:
            if key not in objectives:
                raise ValueError(f"缺少{key}目标")
            if not isinstance(objectives[key], list):
                raise ValueError(f"{key}目标必须是列表")
            if not objectives[key]:
                raise ValueError(f"{key}目标不能为空")
                
        print("目标生成完成")
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
    if not isinstance(objectives, dict):
        raise ValueError("教学目标必须是字典类型")
        
    if "objectives" not in objectives:
        raise ValueError("缺少objectives字段")
        
    # 检查教学目标
    obj = objectives["objectives"]
    for key in ["knowledge_skill", "process_method", "emotion_attitude"]:
        if key not in obj:
            raise ValueError(f"教学目标缺少{key}字段")
        if not isinstance(obj[key], list):
            raise ValueError(f"{key}必须是列表类型")
        if not obj[key]:
            raise ValueError(f"{key}不能为空")
            
    # 检查核心素养
    if "core_literacy" not in objectives:
        raise ValueError("缺少core_literacy字段")
    if not isinstance(objectives["core_literacy"], list):
        raise ValueError("core_literacy必须是列表类型")
    if not objectives["core_literacy"]:
        raise ValueError("core_literacy不能为空")

def generate_objectives(content: Optional[Dict[str, Any]], grade: str = "7年级", subject: str = "语文") -> Dict[str, Any]:
    """生成教学目标"""
    try:
        # 获取LLM配置
        llm_config = get_llm()
        
        # 构建提示词
        if content:
            content_json = json.dumps(content, indent=2, ensure_ascii=False)
            template = """作为一名资深的{subject}教师，请基于以下教材内容为{grade}学生生成教学目标。

教材内容：
{content}

请设计完整的教学目标，要求：
1. 目标要全面覆盖教材内容
2. 目标要分为三个维度：
   - 知识与技能目标
   - 过程与方法目标
   - 情感态度与价值观目标
3. 每个目标要：
   - 具体明确
   - 可测量
   - 可达成
   - 符合{grade}学生认知水平
   - 有时间限制
4. 目标设计要：
   - 符合{subject}学科特点
   - 体现核心素养
   - 注重能力培养
   - 关注学生发展
   - 突出应用实践
   - 重视情感熏陶

请按以下格式输出：
{{
    "objectives": {{
        "knowledge_skill": [
            {{
                "content": "目标内容",
                "importance": "重要程度",
                "evaluation_criteria": ["评价标准1", "评价标准2"]
            }}
        ],
        "process_method": [
            {{
                "content": "目标内容",
                "importance": "重要程度",
                "evaluation_criteria": ["评价标准1", "评价标准2"]
            }}
        ],
        "emotion_attitude": [
            {{
                "content": "目标内容",
                "importance": "重要程度",
                "evaluation_criteria": ["评价标准1", "评价标准2"]
            }}
        ]
    }},
    "core_literacy": [
        {{
            "name": "素养名称",
            "description": "具体描述",
            "related_objectives": ["相关目标1", "相关目标2"]
        }}
    ]
}}"""
        else:
            template = """作为一名资深的{subject}教师，请设计一个单元的教学目标。

请设计完整的教学目标，要求：
1. 目标要分为三个维度：
   - 知识与技能目标
   - 过程与方法目标
   - 情感态度与价值观目标
2. 每个目标要：
   - 具体明确
   - 可测量
   - 可达成
   - 符合{grade}学生认知水平
   - 有时间限制
3. 目标设计要：
   - 符合{subject}学科特点
   - 体现核心素养
   - 注重能力培养
   - 关注学生发展
   - 突出应用实践
   - 重视情感熏陶

请按以下格式输出：
{{
    "objectives": {{
        "knowledge_skill": [
            {{
                "content": "目标内容",
                "importance": "重要程度",
                "evaluation_criteria": ["评价标准1", "评价标准2"]
            }}
        ],
        "process_method": [
            {{
                "content": "目标内容",
                "importance": "重要程度",
                "evaluation_criteria": ["评价标准1", "评价标准2"]
            }}
        ],
        "emotion_attitude": [
            {{
                "content": "目标内容",
                "importance": "重要程度",
                "evaluation_criteria": ["评价标准1", "评价标准2"]
            }}
        ]
    }},
    "core_literacy": [
        {{
            "name": "素养名称",
            "description": "具体描述",
            "related_objectives": ["相关目标1", "相关目标2"]
        }}
    ]
}}"""

        prompt = template.format(
            content=content_json if content else "",
            grade=grade,
            subject=subject
        )

        print("\n=== 生成教学目标 ===")
        print("调用LLM生成教学目标...")
        
        # 调用LLM
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": f"你是一个专业的{subject}教师，擅长设计教学目标。你的设计要符合新课标要求，体现学科特点。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        # 解析响应
        result = response.choices[0].message.content
        if isinstance(result, str):
            result = json.loads(result)
            
        print("教学目标生成完成")
        return result
        
    except Exception as e:
        print(f"错误：生成教学目标失败 - {str(e)}")
        return {
            "objectives": {
                "knowledge_skill": [],
                "process_method": [],
                "emotion_attitude": []
            },
            "core_literacy": []
        } 
