class LessonPlanError(Exception):
    """教学大纲生成相关错误的基类"""
    pass

class FileFormatError(LessonPlanError):
    """文件格式错误"""
    pass

class ContentExtractionError(LessonPlanError):
    """内容提取错误"""
    pass

class PDFExtractionError(Exception):
    """PDF提取错误"""
    pass

class LLMGenerationError(Exception):
    """LLM生成错误"""
    pass

class ValidationError(Exception):
    """验证错误"""
    pass

class FileOperationError(Exception):
    """文件操作错误"""
    pass 