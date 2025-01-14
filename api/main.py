from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from typing import Optional
import os
import sys

# 添加父目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from my_agent.agent import TeachingAgent
from langchain_core.messages import HumanMessage

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许的源
    allow_credentials=True,
    allow_methods=["*"],  # 允许的HTTP方法
    allow_headers=["*"],  # 允许的HTTP头
)

@app.post("/generate")
async def generate_outline(
    pdf: Optional[UploadFile] = None,
    total_hours: int = Form(...),
    grade: str = Form(...),
    subject: str = Form(...)
):
    try:
        # 如果上传了PDF文件，保存它
        pdf_path = ""
        if pdf:
            pdf_path = f"uploads/{pdf.filename}"
            os.makedirs("uploads", exist_ok=True)
            with open(pdf_path, "wb") as f:
                f.write(await pdf.read())
        
        # 准备配置
        config = {
            "pdf_path": pdf_path,
            "total_hours": total_hours,
            "grade": grade,
            "subject": subject
        }
        
        # 创建消息
        message = HumanMessage(content=json.dumps(config, ensure_ascii=False))
        
        # 初始化教学代理
        agent = TeachingAgent()
        
        # 运行代理
        result = agent.run({"messages": [message]})
        
        return result
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 