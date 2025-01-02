<<<<<<< HEAD
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
=======
from PyPDF2 import PdfReader
import os
import pytesseract
from pdf2image import convert_from_path
import warnings
from .exceptions import FileFormatError, ContentExtractionError

# 忽略 PyPDF2 的特定警告
warnings.filterwarnings('ignore', category=UserWarning, module='PyPDF2._cmap')

def is_scanned_pdf(pdf_path: str) -> bool:
    """判断是否为扫描版PDF（纯图片版）"""
    try:
        reader = PdfReader(pdf_path)
        # 检查第一页是否包含可提取的文本
        first_page = reader.pages[0]
        text = first_page.extract_text().strip()
        # 如果提取的文本很少，认为是扫描版
        return len(text) < 50
    except Exception:
        return True

def extract_text_from_scanned_pdf(pdf_path: str) -> str:
    """从扫描版PDF中提取文本（使用OCR）"""
    try:
        # 将PDF转换为图片
        images = convert_from_path(pdf_path)
        text = ""
        
        # 对每一页进行OCR
        for image in images:
            # 使用pytesseract进行中文OCR
            page_text = pytesseract.image_to_string(image, lang='chi_sim')
            text += page_text + "\n"
            
        return text
    except Exception as e:
        raise ContentExtractionError(f"OCR处理失败: {str(e)}")

def extract_pdf_content(pdf_path: str, section: str = None) -> tuple[str, bool]:
    """
    从PDF文件中提取内容
    
    Returns:
        tuple[str, bool]: (提取的内容, 是否为扫描版PDF)
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(pdf_path):
            return """示例文本...""", False
            
        # 检查文件格式
        if not pdf_path.lower().endswith('.pdf'):
            raise FileFormatError("仅支持PDF格式的教材文件")
        
        # 判断PDF类型并提取文本
        content = ""
        is_scanned = is_scanned_pdf(pdf_path)
        
        if is_scanned:
            print("检测到扫描版PDF，正在进行OCR处理...")
            content = extract_text_from_scanned_pdf(pdf_path)
        else:
            print("检测到文字版PDF，正在提取文本...")
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                content += page.extract_text()
        
        # 检查是否成功提取内容
        if not content.strip():
            raise ContentExtractionError("无法从PDF文件中提取内容")
        
        # 打印前100个字符，帮助调试
        print(f"提取的文本开头：{content[:100]}")
        
        return content, is_scanned
        
    except (FileFormatError, ContentExtractionError) as e:
        raise e
    except Exception as e:
        raise ContentExtractionError(f"提取内容时发生错误: {str(e)}") 
>>>>>>> c4972e73ce82ab596751226cd0a07e233d3db998
