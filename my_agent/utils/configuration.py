from dataclasses import dataclass
from typing import Optional
import os

DEFAULT_PDF_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "textbooks",
    "普通高中教科书·语文必修 下册.pdf"
)

@dataclass(kw_only=True)
class Configuration:
    """教学大纲生成器的配置参数"""
    
    # 教材文件路径
    pdf_path: str = DEFAULT_PDF_PATH
    
    # 课程基本信息
    total_hours: int = 16
    grade: str = "7年级"
    subject: str = "语文"
    
    @classmethod
    def from_cli_args(cls, args: list) -> "Configuration":
        """从命令行参数创建配置实例"""
        values = {}
        
        # 解析命令行参数
        if len(args) > 1:
            values["pdf_path"] = args[1]
        if len(args) > 2:
            values["total_hours"] = int(args[2])
        if len(args) > 3:
            values["grade"] = args[3]
        if len(args) > 4:
            values["subject"] = args[4]
            
        # 使用环境变量覆盖默认值
        for field in ["pdf_path", "total_hours", "grade", "subject"]:
            env_value = os.environ.get(f"TEACHING_PLAN_{field.upper()}")
            if env_value is not None:
                if field == "total_hours":
                    values[field] = int(env_value)
                else:
                    values[field] = env_value
                    
        return cls(**values)
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "pdf_path": self.pdf_path,
            "total_hours": self.total_hours,
            "grade": self.grade,
            "subject": self.subject
        }
    
    def print_config(self) -> None:
        """打印配置信息"""
        print(f"\n=== 配置信息 ===")
        print(f"教材文件：{self.pdf_path}")
        print(f"总课时：{self.total_hours}")
        print(f"年级：{self.grade}")
        print(f"学科：{self.subject}") 