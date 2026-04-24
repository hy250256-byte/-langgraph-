# RS-100 吊挂系统客服 Agent

基于 LangGraph 的智能客服系统，专门为 RS-100 吊挂系统提供技术支持。

## 功能特性

- ✅ 意图分类（闲聊、技术问题、转人工）
- ✅ 文档检索（自动查询用户手册相关章节）
- ✅ 多轮对话
- ⚠️ 对话记忆（开发中）
- 🔄 LangSmith Studio 集成

## 项目结构

```
customer-service/
├── my-app/                      # LangGraph 应用目录
│   ├── my_agent/
│   │   ├── __init__.py
│   │   ├── agent.py            # Graph 定义
│   │   └── utils/
│   │       ├── state.py        # State 定义
│   │       ├── nodes.py        # 节点实现
│   │       └── tools.py        # 工具定义
│   ├── langgraph.json          # LangGraph 配置
│   └── pyproject.toml          # Python 项目配置
├── docs/
│   ├── knowledge base/         # 原始 Word 文档
│   ├── database/RS-100/        # 转换后的 Markdown 文档
│   │   ├── *.md
│   │   └── assets/images/      # 提取的图片
│   └── superpowers/
│       ├── specs/              # 设计文档
│       └── plans/              # 实施计划
├── convert_docs.py            # Word 转 Markdown 工具
└── README.md
```

## 快速开始

### 前置条件

- Python 3.10+
- 豆包 API Key（或其他 OpenAI 兼容 API）

### 安装依赖

```bash
cd my-app
pip install -e .
```

### 配置环境变量

在 `my-app` 目录下创建 `.env` 文件：

```env
ARK_API_KEY=your_api_key_here
DOUBAO_MODEL=doubao-seed-2-0-mini-260215
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

### 启动开发服务器

```bash
cd my-app
langgraph dev --port 2025
```

### 在 LangSmith Studio 中使用

启动后，在浏览器中访问显示的 Studio URL，即可开始对话。

## 使用说明

### 支持的对话类型

1. **闲聊** - 日常问候、简单聊天
2. **技术问题** - 关于 RS-100 吊挂系统的使用问题
3. **转人工** - 需要人工客服支持

### 示例对话

```
用户：你好
Agent：你好！很高兴为你服务。

用户：怎么设置非本位？
Agent：[查询手册后回答]

用户：那怎么取消呢？
Agent：[理解上下文后回答]
```

## 开发计划

详见 [项目更新路线图](docs/superpowers/plans/项目更新路线图.md)

### 当前优先级

1. **最高** - 修复 Agent 记忆问题（对话上下文理解）
2. **高** - 实现图片显示功能
3. **中** - 实现主动追问澄清功能

## 工具说明

### convert_docs.py

将 Word 文档转换为 Markdown 格式，并提取图片。

```bash
python convert_docs.py
```

## 技术栈

- LangGraph - Agent 框架
- LangChain - LLM 应用开发
- 豆包 API - 大语言模型
