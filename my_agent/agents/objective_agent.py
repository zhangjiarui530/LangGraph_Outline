<<<<<<< HEAD
from typing import Dict, Any, List
from my_agent.config import get_llm
from my_agent.utils.exceptions import LLMGenerationError
from my_agent.utils.types import AgentState
import json

def design_objectives(content: str, total_hours: int) -> Dict[str, Any]:
    """设计教学目标"""
    try:
        # 验证输入
        if not content:
            raise ValueError("内容为空")
            
        if not isinstance(total_hours, (int, float)) or total_hours <= 0:
            raise ValueError(f"总课时格式错误: {total_hours}")
            
        # 获取LLM配置
        llm_config = get_llm()
        
        # 构建提示词
        prompt = f"""作为教学设计专家，请基于以下内容设计教学目标。总课时为{total_hours}学时。

内容概要：
{content[:2000]}  # 限制内容长度，避免token超限

请设计以下几个方面的教学目标：
1. 知识目标：学生应该掌握的具体知识点
2. 能力目标：学生应该培养的能力
3. 素养目标：学生应该形成的素养

请按以下格式输出：
{{
    "teaching_objectives": {{
        "知识": ["目标1", "目标2", ...],
        "能力": ["目标1", "目标2", ...],
        "素养": ["目标1", "目标2", ...]
    }}
}}"""

        print("\n=== 生成教学目标 ===")
        print(f"内容长度: {len(content)}")
        print("调用LLM生成目标...")
        
        # 调用LLM
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": "你是一个专业的教学设计专家，擅长设计教学目标。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        # 解析响应
        result = response.choices[0].message.content
        if not isinstance(result, dict):
            import json
            result = json.loads(result)
            
        # 验证结果
        if not isinstance(result, dict):
            raise ValueError(f"结果格式错误: {type(result)}")
            
        if "teaching_objectives" not in result:
            raise ValueError("缺少teaching_objectives字段")
            
        objectives = result["teaching_objectives"]
        if not isinstance(objectives, dict):
            raise ValueError(f"teaching_objectives格式错误: {type(objectives)}")
            
        for key in ["知识", "能力", "素养"]:
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
        
    if "teaching_objectives" not in objectives:
        raise ValueError("缺少teaching_objectives字段")
        
    if "teaching_suggestions" not in objectives:
        raise ValueError("缺少teaching_suggestions字段")
        
    # 检查教学目标
    obj = objectives["teaching_objectives"]
    for key in ["knowledge", "ability", "quality"]:
        if key not in obj:
            raise ValueError(f"教学目标缺少{key}字段")
        if not isinstance(obj[key], list):
            raise ValueError(f"{key}必须是列表类型")
        if not obj[key]:
            raise ValueError(f"{key}不能为空")
            
    # 检查教学建议
    sug = objectives["teaching_suggestions"]
    for key in ["key_points", "strategies", "time_allocation"]:
        if key not in sug:
            raise ValueError(f"教学建议缺少{key}字段")
        if not isinstance(sug[key], str):
            raise ValueError(f"{key}必须是字符串类型")
        if not sug[key].strip():
            raise ValueError(f"{key}不能为空") 

def generate_objectives(textbook_content: Dict[str, Any]) -> Dict[str, Any]:
    """生成教学目标"""
    try:
        # 验证输入
        if not isinstance(textbook_content, dict):
            raise ValueError(f"教材内容格式错误: {type(textbook_content)}")
            
        # 获取LLM配置
        llm_config = get_llm()
        
        # 构建提示词
        content_json = json.dumps(textbook_content, indent=2, ensure_ascii=False)
        template = """作为教学目标设计专家，请基于以下教材内容生成教学目标。

教材内容：
{content}

请生成教学目标，要求：
1. 目标要具体、可测量、可实现
2. 包含知识目标、能力目标和情感目标三个维度
3. 每个维度的目标要有层次性，从低到高
4. 目标要与教材内容紧密相关

请按以下格式输出：
{{
    "objectives": {{
        "knowledge": [
            {{
                "level": "记忆/理解/应用/分析/评价/创造",
                "description": "目标描述",
                "evaluation": "达成标准"
            }}
        ],
        "ability": [
            {{
                "level": "模仿/操作/熟练/创新",
                "description": "目标描述",
                "evaluation": "达成标准"
            }}
        ],
        "emotion": [
            {{
                "level": "感知/响应/形成/内化",
                "description": "目标描述",
                "evaluation": "达成标准"
            }}
        ]
    }}
}}"""

        prompt = template.format(content=content_json)

        print("\n=== 生成教学目标 ===")
        print("调用LLM生成目标...")
        
        # 调用LLM
        response = llm_config.client.chat.completions.create(
            model=llm_config.model,
            messages=[
                {"role": "system", "content": "你是一个专业的教学目标设计专家，擅长设计教学目标。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        # 解析响应
        result = response.choices[0].message.content
        if isinstance(result, str):
            result = json.loads(result)
            
        # 验证结果
        if not isinstance(result, dict):
            raise ValueError(f"结果格式错误: {type(result)}")
            
        if "objectives" not in result:
            raise ValueError("缺少objectives字段")
            
        objectives = result["objectives"]
        if not isinstance(objectives, dict):
            raise ValueError(f"objectives格式错误: {type(objectives)}")
            
        required_fields = ["knowledge", "ability", "emotion"]
        for field in required_fields:
            if field not in objectives:
                raise ValueError(f"缺少{field}目标")
            if not isinstance(objectives[field], list):
                raise ValueError(f"{field}目标格式错误")
            if not objectives[field]:
                raise ValueError(f"{field}目标不能为空")
                
        # 验证每个目标的格式
        for field in required_fields:
            for obj in objectives[field]:
                if not isinstance(obj, dict):
                    raise ValueError(f"{field}目标项格式错误")
                for key in ["level", "description", "evaluation"]:
                    if key not in obj:
                        raise ValueError(f"{field}目标缺少{key}字段")
                    if not isinstance(obj[key], str):
                        raise ValueError(f"{field}目标的{key}字段必须是字符串")
                        
        print("目标生成完成")
        return result
        
    except Exception as e:
        print(f"错误：生成教学目标失败 - {str(e)}")
        raise LLMGenerationError(f"生成教学目标失败: {str(e)}") 
=======
from typing import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from my_agent.config import get_llm
from my_agent.utils.types import AgentState
from my_agent.utils.exceptions import LLMGenerationError

def analyze_objectives(state: AgentState) -> AgentState:
    """分析教学目标的代理"""
    try:
        print("\n=== 开始分析教学目标 ===")
        state["progress_status"] = "正在分析教学目标..."
        
        system_prompt = """你是一位资深的教育专家和课程设计师，拥有丰富的教学大纲编写经验。
        你的任务是分析教材内容，提炼出清晰、可衡量的教学目标。

        请遵循以下原则：
        1. 目标应该具体、可测量、可实现、相关且有时限
        2. 需要涵盖知识、能力和素养三个维度
        3. 使用布鲁姆教育目标分类法的动词
        4. 确保目标与课程难度和学生水平相适应
        5. 每个维度的目标应该相互关联，形成完整的学习体系
        6. 考虑到总课时{state['total_hours']}的限制，设定合理的目标数量

        输出格式要求：
        1. 知识目标：（使用理解、记忆、应用等动词）
           - 目标应该清晰具体，避免模糊表述
           - 每个目标都应该可以通过评估来验证

        2. 能力目标：（使用分析、评价、创造等动词）
           - 重点关注高阶思维能力的培养
           - 目标应该与实际应用场景相结合

        3. 素养目标：（关注学科素养和核心素养的培养）
           - 体现学科特色和育人价值
           - 与学生的生活经验和未来发展相联系
        """
        
        user_prompt = f"""
        请基于以下教材内容，分析并提炼教学目标。
        注意：这是一个{state['total_hours']}课时的教学单元。

        教材内容：
        {state['file_content']}

        请确保你的分析：
        1. 准确把握教材重点和难点
        2. 考虑学生的认知水平和学习特点
        3. 体现教材的育人价值和学科特色
        """
        
        llm = get_llm(is_scanned=state["is_scanned"])
        print("正在调用 AI 分析教学目标...")  # 添加提示
        response = llm.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        content = response.choices[0].message.content
        print("教学目标分析完成")  # 添加提示
        
        if not content:
            raise LLMGenerationError("生成的教学目标为空")
        
        print("=== 教学目标分析完成 ===\n")  # 添加提示
        
        # 确保所有字段都有有效值
        new_state = {
            **state,
            "teaching_objectives": content,
            "next_step": "generate_knowledge_points",
            "messages": [],
            "knowledge_points": state.get("knowledge_points", []),
            "teaching_activities": state.get("teaching_activities", []),
            "assessment_plan": state.get("assessment_plan", {}),
            "final_output": state.get("final_output", ""),
            "progress_status": "已生成教学目标",
            "error_msg": None
        }
        return new_state
        
    except Exception as e:
        return {
            **state,
            "error_msg": str(e),
            "next_step": "error",
            "progress_status": "生成失败",
            "messages": [],
            "teaching_objectives": None,
            "knowledge_points": [],
            "teaching_activities": [],
            "assessment_plan": {},
            "final_output": ""
        } 
>>>>>>> c4972e73ce82ab596751226cd0a07e233d3db998
