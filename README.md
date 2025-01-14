# 教学大纲生成器

用send方法将activity_agent变为mapreduce模式
实现各个agent的流式输出

基于 LangGraph 的智能教学大纲生成系统。

## 项目结构

```
.
├── api/                # 后端 FastAPI 服务
├── lesson-plan-ui/     # 前端 Next.js 应用
└── my_agent/          # LangGraph 智能代理
```

## 启动说明

### 1. 启动前端

```bash
# 进入前端项目目录
cd lesson-plan-ui

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:3000 运行

### 2. 启动后端

```bash
# 进入后端项目目录
cd api

# 安装依赖
pip install -r requirements.txt

# 启动服务器
python main.py
```

后端将在 http://localhost:8000 运行

## 使用说明

1. 打开浏览器访问 http://localhost:3000
2. 上传教材 PDF 文件（可选）
3. 填写课时数量
4. 选择年级
5. 选择学科
6. 点击"生成教学大纲"按钮

## 注意事项

1. 确保已安装 Node.js 和 Python
2. 确保后端的 8000 端口未被占用
3. 如果上传 PDF，需要确保 api/uploads 目录存在
