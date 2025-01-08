import os
import PyPDF2
from typing import Dict, Any
from my_agent.utils.exceptions import PDFExtractionError, FileOperationError

def is_valid_pdf(file_path: str) -> bool:
    """检查PDF文件是否有效"""
    try:
        if not os.path.exists(file_path):
            return False
            
        if not file_path.lower().endswith('.pdf'):
            return False
            
        # 尝试打开PDF文件
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if len(reader.pages) == 0:
                return False
                
        return True
        
    except Exception as e:
        print(f"验证PDF文件失败: {str(e)}")
        return False

def extract_text_from_pdf(file_path: str) -> Dict[str, Any]:
    """从PDF文件中提取文本内容"""
    try:
        if not is_valid_pdf(file_path):
            raise PDFExtractionError(f"无效的PDF文件: {file_path}")
            
        content = {
            "title": "",
            "chapters": [],
            "pdf_path": file_path
        }
        
        # 打开PDF文件
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # 提取文件名作为标题
            content["title"] = os.path.splitext(os.path.basename(file_path))[0]
            
            # 提取每一页的内容
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                
                # 将页面内容添加到章节
                chapter = {
                    "page_number": page_num + 1,
                    "content": text.strip()
                }
                content["chapters"].append(chapter)
                
        return content
        
    except PDFExtractionError:
        raise
    except Exception as e:
        print(f"提取PDF内容失败: {str(e)}")
        raise PDFExtractionError(f"提取PDF内容失败: {str(e)}")

def get_pdf_metadata(file_path: str) -> Dict[str, Any]:
    """获取PDF文件的元数据"""
    try:
        if not is_valid_pdf(file_path):
            raise PDFExtractionError(f"无效的PDF文件: {file_path}")
            
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            metadata = reader.metadata
            
            return {
                "title": metadata.get("/Title", ""),
                "author": metadata.get("/Author", ""),
                "subject": metadata.get("/Subject", ""),
                "keywords": metadata.get("/Keywords", ""),
                "creator": metadata.get("/Creator", ""),
                "producer": metadata.get("/Producer", ""),
                "creation_date": metadata.get("/CreationDate", ""),
                "modification_date": metadata.get("/ModDate", ""),
                "page_count": len(reader.pages)
            }
            
    except PDFExtractionError:
        raise
    except Exception as e:
        print(f"获取PDF元数据失败: {str(e)}")
        raise PDFExtractionError(f"获取PDF元数据失败: {str(e)}") 
    
def has_table_of_contents(content: Dict[str, Any]) -> bool:
    """检查内容是否包含目录
    
    通过检查文本内容的前几页，查找常见的目录标识来判断是否存在目录。
    
    Args:
        content: 包含章节内容的字典，格式为：
                {
                    "title": str,
                    "chapters": [
                        {
                            "page_number": int,
                            "content": str
                        },
                        ...
                    ]
                }
        
    Returns:
        bool: 是否包含目录
    """
    try:
        if not content or not isinstance(content, dict):
            return False
            
        chapters = content.get("chapters", [])
        if not chapters:
            return False
            
        # 检查前5页
        max_pages = min(5, len(chapters))
        
        # 目录的常见标识（与extract_toc_content保持一致）
        toc_indicators = [
            "目\s*录",
            "contents",
            "table\s+of\s+contents",
            "章\s*节\s*目\s*录",
            "教\s*材\s*目\s*录",
            "目\s*次"
        ]
        
        import re
        # 检查每一页
        for chapter in chapters[:max_pages]:
            text = chapter.get("content", "").strip()
            if not text:
                continue
                
            # 按行检查
            for line in text.split('\n'):
                line = line.strip().lower()
                if not line:
                    continue
                    
                # 使用正则表达式匹配
                for indicator in toc_indicators:
                    if re.search(indicator.lower(), line):
                        print(f"检测到目录标识：{line}")
                        return True
                    
        return False
        
    except Exception as e:
        print(f"检查目录失败: {str(e)}")
        return False

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