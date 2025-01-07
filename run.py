import os
import sys
from datetime import datetime
from my_agent.agent import TeachingAgent
from my_agent.utils.configuration import Configuration

def main():
    """主函数"""
    print("\n=== 教学大纲生成器 ===")
    
    # 从命令行参数创建配置
    config = Configuration.from_cli_args(sys.argv)
    
    # 检查文件是否存在
    if not os.path.exists(config.pdf_path):
        print(f"错误：文件 {config.pdf_path} 不存在")
        return
    
    # 打印配置信息
    config.print_config()
    print("\n=== 开始处理 ===")
    
    # 创建代理并运行
    try:
        print("1. 初始化教学代理...")
        agent = TeachingAgent()
        
        print("2. 开始处理教材...")
        result = agent.run(**config.to_dict())
        
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
        if not result.get("objectives"):
            print("警告：未生成教学目标")
        if not result.get("knowledge_points"):
            print("警告：未生成知识点")
        if not result.get("activities"):
            print("警告：未生成教学活动")
        if not result.get("assessment"):
            print("警告：未生成评估方案")
            
        print("\n=== 生成完成 ===")
        print("教学大纲已保存到output目录")
        
    except Exception as e:
        print(f"\n错误：程序执行失败 - {str(e)}")
        import traceback
        print(traceback.format_exc())
        
if __name__ == "__main__":
    main() 