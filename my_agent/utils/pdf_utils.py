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
            "chapters": []
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