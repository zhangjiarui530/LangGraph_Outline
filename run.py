<<<<<<< HEAD
import os
import sys
from datetime import datetime
from my_agent.agent import TeachingAgent

# 默认教材路径
DEFAULT_TEXTBOOK_PATH = r"C:\Users\Intel\Desktop\Dase2025\4_OpenTeacherAssistant\langgraphoutline\textbooks\普通高中教科书·语文必修 下册.pdf"

def main():
    """主函数"""
    print("\n=== 教学大纲生成器 ===")
    
    # 获取PDF路径
    pdf_path = DEFAULT_TEXTBOOK_PATH
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(pdf_path):
        print(f"错误：文件 {pdf_path} 不存在")
        return
        
    # 固定总课时为16
    total_hours = 16
    
    print(f"\n=== 配置信息 ===")
    print(f"教材文件：{pdf_path}")
    print(f"总课时：{total_hours}")
    print("\n=== 开始处理 ===")
    
    # 创建代理并运行
    try:
        print("1. 初始化教学代理...")
        agent = TeachingAgent()
        
        print("2. 开始处理教材...")
        result = agent.run(pdf_path=pdf_path, total_hours=total_hours)
        
        print("3. 处理完成，输出日志...")
        # 打印处理日志
        print("\n=== 处理日志 ===")
        for message in result.get("messages", []):
            if isinstance(message, dict):
                role = message.get("role", "system")
                content = message.get("content", "")
                msg_type = message.get("type", "message")
                
                if msg_type == "error":
                    print(f"\n错误 - {role}: {content}")
                else:
                    print(f"{role}: {content}")
            else:
                print(f"系统: {str(message)}")
            
        # 检查结果
        print("\n=== 结果验证 ===")
        if not result.get("teaching_objectives"):
            print("警告：未生成教学目标")
        if not result.get("knowledge_points"):
            print("警告：未生成知识点")
        if not result.get("teaching_activities"):
            print("警告：未生成教学活动")
        if not result.get("assessment_plan"):
            print("警告：未生成评估方案")
            
        print("\n=== 生成完成 ===")
        print("教学大纲已保存到output目录")
        
    except Exception as e:
        print(f"\n错误：程序执行失败 - {str(e)}")
        import traceback
        print(traceback.format_exc())
        
=======
from my_agent.agent import main

>>>>>>> c4972e73ce82ab596751226cd0a07e233d3db998
if __name__ == "__main__":
    main() 