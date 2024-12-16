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