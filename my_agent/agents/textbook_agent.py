from typing import Dict, Any
import json
import time
import re
from my_agent.utils.pdf_utils import extract_text_from_pdf, is_valid_pdf, has_table_of_contents, extract_toc_content

def process_textbook(pdf_path: str, total_hours: int) -> Dict[str, Any]:
    """处理教材内容
    
    Args:
        pdf_path: PDF文件路径
        total_hours: 总课时数
        
    Returns:
        Dict[str, Any]: 处理结果
    """
    start_time = time.time()
    try:
        print("\n=== 处理教材内容 ===")
        
        # 验证PDF文件
        if not is_valid_pdf(pdf_path):
            print("未提供有效的PDF文件，将使用空教材内容继续运行")
            return {
                "messages": ["使用空教材内容继续运行"],
                "textbook_content": {},
                "total_hours": total_hours,
                "toc_content": "",
                "units": [],
                "unit_count": 6,  # 默认单元数
                "has_toc": False
            }
        
        # 提取教材内容
        print("正在提取PDF内容...")
        textbook_content = extract_text_from_pdf(pdf_path)
        print("PDF内容提取完成")
        
        # 验证总课时
        if not isinstance(total_hours, int) or total_hours <= 0:
            raise ValueError(f"总课时格式错误: {total_hours}")
            
        if total_hours % 4 != 0:
            raise ValueError(f"总课时必须是4的倍数: {total_hours}")
            
        # 验证教材内容
        if not isinstance(textbook_content, dict):
            raise ValueError(f"教材内容格式错误: {type(textbook_content)}")
            
        # 检查是否为纯图片版本
        if textbook_content.get("chapters"):
            total_text = "".join(chapter.get("content", "") for chapter in textbook_content["chapters"])
            if len(total_text.strip()) < 100:  # 如果提取的文本内容太少，认为是纯图片版本
                return {
                    "messages": ["检测到纯图片版本的教材，处理终止"],
                    "textbook_content": textbook_content,
                    "total_hours": total_hours,
                    "next": "END"  # 直接结束处理
                }

        # 检查是否包含目录
        print("检查教材是否包含目录...")
        has_toc = has_table_of_contents(textbook_content)
        print(f"目录检查结果：{'包含目录' if has_toc else '未包含目录'}")

        # 提取目录内容
        print("正在提取目录内容...")
        toc_content = extract_toc_content(textbook_content) if has_toc else ""
        if not toc_content:
            print("未找到目录内容，将使用完整内容...")
            toc_content = json.dumps(textbook_content, ensure_ascii=False, indent=2)
        
        print(f"成功提取目录内容，长度：{len(toc_content)}")
        
        # 计算单元数量
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
            
        elapsed_time = time.time() - start_time
        print(f"教材内容处理完成，耗时：{elapsed_time:.2f}秒")
        return {
            "messages": ["教材内容处理完成"],
            "textbook_content": textbook_content,
            "total_hours": total_hours,
            "toc_content": toc_content,  # 添加目录内容到状态
            "units": units,  # 添加单元列表到状态
            "unit_count": unit_count,  # 添加单元数量到状态
            "has_toc": has_toc  # 添加是否包含目录的标志
        }
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"错误：处理教材内容失败 - {str(e)}")
        print(f"失败耗时：{elapsed_time:.2f}秒")
        raise ValueError(f"处理教材内容失败: {str(e)}") 