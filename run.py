import os
import sys
from datetime import datetime
from my_agent.agent import TeachingAgent
from my_agent.utils.configuration import Configuration

def get_user_input() -> dict:
    """获取用户输入的基本配置"""
    print("\n=== 请输入基本配置信息 ===")
    
    # 设置默认值
    default_pdf = os.path.join("textbooks", "普通高中教科书·语文必修 下册.pdf")
    default_hours = 16
    default_grade = "7年级"
    default_subject = "语文"
    
    # 获取用户输入
    pdf_path = input(f"请输入教材PDF路径 (默认: {default_pdf}): ").strip() or default_pdf
    total_hours = int(input(f"请输入总课时数 (默认: {default_hours}): ").strip() or default_hours)
    grade = input(f"请输入年级 (默认: {default_grade}): ").strip() or default_grade
    subject = input(f"请输入学科 (默认: {default_subject}): ").strip() or default_subject
    
    return {
        "pdf_path": pdf_path,
        "total_hours": total_hours,
        "grade": grade,
        "subject": subject
    }

def main():
    """主函数"""
    print("\n=== 教学大纲生成器 ===")
    
    # 获取用户输入的基本配置
    config_dict = get_user_input()
    
    # 获取LLM配置
    llm_config = Configuration.from_cli_args(sys.argv)
    
    # 检查文件是否存在
    if not os.path.exists(config_dict["pdf_path"]):
        print(f"错误：文件 {config_dict['pdf_path']} 不存在")
        return
    
    # 打印配置信息
    print("\n=== 基本配置信息 ===")
    print(f"教材文件：{config_dict['pdf_path']}")
    print(f"总课时：{config_dict['total_hours']}")
    print(f"年级：{config_dict['grade']}")
    print(f"学科：{config_dict['subject']}")
    llm_config.print_config()
    
    print("\n=== 开始处理 ===")
    
    # 创建代理并运行
    try:
        print("1. 初始化教学代理...")
        agent = TeachingAgent()
        
        print("2. 开始处理教材...")
        result = agent.run(**config_dict)
        
        # 打印处理日志
        print("\n=== 处理日志 ===")
        for message in result.get("messages", []):
            print(f"系统: {message}")
            
        print("\n=== 生成完成 ===")
        print("教学大纲已保存到output目录")
        
    except Exception as e:
        print(f"\n错误：程序执行失败 - {str(e)}")
        import traceback
        print(traceback.format_exc())
        
if __name__ == "__main__":
    main() 