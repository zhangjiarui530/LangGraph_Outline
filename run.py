import os
import sys
import json
from datetime import datetime
from my_agent.agent import TeachingAgent, TeachingInputState
from my_agent.utils.configuration import Configuration
from langchain_core.messages import HumanMessage

def get_user_input() -> TeachingInputState:
    """获取用户输入的基本配置"""
    print("\n=== 请输入基本配置信息 ===")
    
    # 设置默认值
    default_pdf = os.path.join("textbooks", "普通高中教科书·语文必修 下册.pdf")
    default_hours = 16
    default_grade = "7年级"
    default_subject = "语文"
    
    # 获取用户输入
    pdf_path = input(f"请输入教材PDF路径 (默认: {default_pdf}): ").strip() or default_pdf
    # # 规范化路径
    # pdf_path = os.path.normpath(pdf_path)
    # # 转换为绝对路径
    # if not os.path.isabs(pdf_path):
    #     pdf_path = os.path.abspath(pdf_path)
    # print(f"使用PDF路径: {pdf_path}")
    
    total_hours = int(input(f"请输入总课时数 (默认: {default_hours}): ").strip() or default_hours)
    grade = input(f"请输入年级 (默认: {default_grade}): ").strip() or default_grade
    subject = input(f"请输入学科 (默认: {default_subject}): ").strip() or default_subject
    
    # 构造配置字典
    config_dict = {
        "pdf_path": pdf_path,
        "total_hours": total_hours,
        "grade": grade,
        "subject": subject
    }
    print(f"配置信息: {json.dumps(config_dict, ensure_ascii=False, indent=2)}")
    
    # 创建HumanMessage
    message = HumanMessage(content=json.dumps(config_dict, ensure_ascii=False))
    
    # 返回TeachingInputState
    return TeachingInputState(messages=[message])

def main():
    """主函数"""
    print("\n=== 教学大纲生成器 ===")
    
    # 获取用户输入的基本配置
    config = get_user_input()
    
    # 获取LLM配置
    llm_config = Configuration.from_cli_args(sys.argv)
    
    # 解析配置信息
    input_config = json.loads(config["messages"][0].content)
    
    # 打印配置信息
    print("\n=== 基本配置信息 ===")
    print(f"教材文件：{input_config['pdf_path']}")
    if not os.path.exists(input_config["pdf_path"]):
        print("警告：PDF文件不存在，将使用空教材内容继续运行")
    print(f"总课时：{input_config['total_hours']}")
    print(f"年级：{input_config['grade']}")
    print(f"学科：{input_config['subject']}")
    llm_config.print_config()
    
    print("\n=== 开始处理 ===")
    
    # 创建代理并运行
    try:
        print("1. 初始化教学代理...")
        agent = TeachingAgent()
        
        print("2. 开始处理教材...")
        # 直接传递TeachingInputState
        result = agent.run(config)
        
        # 打印处理日志
        print("\n=== 处理日志 ===")
        messages = result.get("messages", [])
        # 只打印最后一条消息
        if messages:
            print(f"系统: {messages[-1]}")
            
        print("\n=== 生成完成 ===")
        print("教学大纲已保存到output目录")
        
    except Exception as e:
        print(f"\n错误：程序执行失败 - {str(e)}")
        import traceback
        print(traceback.format_exc())
        
if __name__ == "__main__":
    main() 