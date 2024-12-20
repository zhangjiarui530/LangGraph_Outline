from typing import TypedDict, Sequence, Annotated, List, Union, Any, Callable
from langchain_core.messages import BaseMessage
import operator
from functools import partial

def binary_last_value(a: Any, b: Any) -> Any:
    """二元操作：返回后一个非空值"""
    return b if b is not None else a

def binary_merge_lists(a: list | None, b: list | None) -> list:
    """二元操作：合并两个列表"""
    result = []
    if a is not None:
        result.extend(a)
    if b is not None:
        result.extend(b)
    return result

def binary_merge_dicts(a: dict | None, b: dict | None) -> dict:
    """二元操作：合并两个字典"""
    result = {}
    if a is not None:
        result.update(a)
    if b is not None:
        result.update(b)
    return result

def binary_first_value(a: Any, b: Any) -> Any:
    """二元操作：返回第一个非空值（用于输入值）"""
    return a if a is not None else b

class AgentState(TypedDict):
    """状态类型定义"""
    messages: Annotated[List[BaseMessage], operator.add]  # 消息列表使用add合并
    teaching_objectives: Annotated[str | None, binary_last_value]  # 使用二元操作
    knowledge_points: Annotated[list[str] | None, binary_merge_lists]  # 使用二元操作
    teaching_activities: Annotated[list[dict] | None, binary_merge_lists]  # 使用二元操作
    assessment_plan: Annotated[dict | None, binary_merge_dicts]  # 使用二元操作
    next_step: Annotated[str, binary_last_value]  # 使用二元操作
    final_output: Annotated[str | None, binary_last_value]  # 使用二元操作
    file_content: Annotated[str | None, binary_first_value]  # 输入值使用first_value
    progress_status: Annotated[str | None, binary_last_value]  # 使用二元操作
    total_hours: Annotated[int, binary_first_value]  # 输入值使用first_value
    hours_per_section: Annotated[dict | None, binary_merge_dicts]  # 使用二元操作
    is_scanned: Annotated[bool, binary_first_value]  # 输入值使用first_value
    error_msg: Annotated[str | None, binary_last_value]  # 错误信息使用last_value