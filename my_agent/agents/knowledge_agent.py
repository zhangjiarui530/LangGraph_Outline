from typing import Dict, Any, List, Optional
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
import json

def analyze_knowledge(content: Dict[str, Any], objectives: Dict[str, Any], grade: str, subject: str) -> str:
    """分析知识点"""
    prompt = f"""作为一名资深的{subject}教师，请基于教材内容和教学目标进行知识点分析。

请首先仔细阅读教材内容和教学目标，分析以下要素：
1. 教材内容的知识体系结构
2. 教学目标对应的知识要求
3. 知识点之间的内在联系
4. 重难点的分布特点

然后基于以上分析，进行知识点分析。要求：
1. 输出采用markdown格式，结构清晰，层次分明，全部使用中文
2. 分析应包含以下部分：

### 基础知识点

[此处结合教材内容和教学目标，列出6-8个基础知识点，每个知识点包含：
- **知识内容**：具体说明知识点的内容和范围，要与教材内容直接对应
- **所在章节**：该知识点在教材中的具体位置
- **难度**：简单/中等/困难
- **重要程度**：核心/重要/一般
- **前置知识**：需要的前置知识列表，注明这些知识在教材中的位置
- **教学建议**：结合教材内容的具体教学建议和方法]

### 重点知识点

[此处结合教材重点内容和核心目标，列出4-5个重点知识点，每个知识点包含：
- **知识内容**：具体说明知识点的内容和范围，要与教材重点内容对应
- **所在章节**：该知识点在教材中的具体位置
- **难度**：中等/困难
- **重要程度**：核心/重要
- **前置知识**：需要的前置知识列表，注明这些知识在教材中的位置
- **教学建议**：针对重点内容的具体教学建议和方法]

### 难点知识点

[此处结合教材难点内容和学生特点，列出3-4个难点知识点，每个知识点包含：
- **知识内容**：具体说明知识点的内容和范围，要与教材难点内容对应
- **所在章节**：该知识点在教材中的具体位置
- **难度**：困难
- **重要程度**：核心/重要
- **前置知识**：需要的前置知识列表，注明这些知识在教材中的位置
- **突破建议**：针对难点内容的具体突破方法和建议]

### 拓展知识点

[此处结合教材拓展内容和发展目标，列出2-3个拓展知识点，每个知识点包含：
- **知识内容**：具体说明知识点的内容和范围，要与教材拓展内容对应
- **所在章节**：该知识点在教材中的具体位置
- **难度**：中等/困难
- **重要程度**：一般
- **前置知识**：需要的前置知识列表，注明这些知识在教材中的位置
- **拓展建议**：如何基于教材内容引导学生进行拓展学习]

注意事项：
1. 知识点要与教材内容和教学目标直接对应
2. 知识点分析要体现教材的重点和难点
3. 知识点之间要体现内在联系和递进关系
4. 所有知识点要符合{grade}学生的认知水平
5. 教学建议要结合教材内容，具体、可操作

教材内容和教学目标如下：
{objectives}
{content}
"""

    try:
        # 获取LLM配置
        llm_config = get_llm()
        
        print("\n=== 分析知识点 ===")
        print("调用LLM分析知识点...")
        
        # 调用LLM
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": f"你是一个专业的{subject}教师，擅长分析教材知识点。你的分析要符合新课标要求，体现{subject}学科特点，适合{grade}学生的认知水平。"},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 获取响应
        result = response.choices[0].message.content
        print("知识点分析完成")
        return result
        
    except Exception as e:
        print(f"错误：分析知识点失败 - {str(e)}")
        return {
            "knowledge_points": {
                "basic": [
                    {
                        "name": "基础知识点",
                        "content": "暂无内容",
                        "difficulty": "中等",
                        "importance": "核心",
                        "prerequisites": [],
                        "objectives": [],
                        "teaching_suggestions": "暂无建议"
                    }
                ],
                "advanced": [
                    {
                        "name": "拓展知识点",
                        "content": "暂无内容",
                        "difficulty": "困难",
                        "importance": "重要",
                        "prerequisites": [],
                        "objectives": [],
                        "teaching_suggestions": "暂无建议"
                    }
                ],
                "key_points": ["暂无重点"],
                "difficult_points": ["暂无难点"]
            }
        }

def validate_knowledge_points(knowledge: Dict[str, Any]) -> None:
    """
    验证知识点分析的格式和内容
    
    Args:
        knowledge: 知识点分析字典
        
    Raises:
        ValueError: 如果格式或内容不符合要求
    """
    # 检查基本结构
    if not isinstance(knowledge, dict):
        raise ValueError("知识点分析必须是字典类型")
        
    if "knowledge_points" not in knowledge:
        raise ValueError("缺少knowledge_points字段")
        
    if "relations" not in knowledge:
        raise ValueError("缺少relations字段")
        
    # 检查知识点
    kp = knowledge["knowledge_points"]
    for key in ["basic", "important", "advanced"]:
        if key not in kp:
            raise ValueError(f"知识点缺少{key}字段")
        if not isinstance(kp[key], list):
            raise ValueError(f"{key}必须是列表类型")
        if not kp[key]:
            raise ValueError(f"{key}不能为空")
            
    # 检查关系
    rel = knowledge["relations"]
    for key in ["prerequisites", "connections", "extensions"]:
        if key not in rel:
            raise ValueError(f"关系缺少{key}字段")
        if not isinstance(rel[key], list):
            raise ValueError(f"{key}必须是列表类型")
        if not rel[key]:
            raise ValueError(f"{key}不能为空")
