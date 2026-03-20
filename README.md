# 深度研究多 Agent 系统

基于 deepagents 框架构建的多 Agent 深度研究系统，用于复杂问题求解、长链路推理和多源信息整合。

## 系统架构

### 组件

| 组件 | 类型 | 描述 |
|------|------|------|
| Orchestrator | 主 Agent | 任务规划、子 Agent 调度、进度追踪 |
| evidence | 子 Agent | 通过网络搜索获取信息 |
| exploration | 子 Agent | 创新性和深度观点的探索 |
| data-analysis | 子 Agent | 长文本内容的整理与分析 |
| outline | 子 Agent | 报告大纲生成与更新 |
| review | 子 Agent | 大纲与证据的一致性审核 |
| write | 子 Agent | 完整报告生成 |

## 快速开始

### 前置要求

安装 [uv](https://docs.astral.sh/uv/) 包管理器：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 安装

```bash
cd deep-research-demo
uv sync
```

### 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的 API key：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
- `ANTHROPIC_API_KEY` - Anthropic API Key（必需）
- `TAVILY_API_KEY` - Tavily API Key（必需，用于网络搜索）
- `GOOGLE_API_KEY` - Google API Key（可选，用于 Gemini 模型）
- `LANGSMITH_API_KEY` - LangSmith API Key（可选，用于追踪）

### 运行方式

#### 方式一：LangGraph 服务器

启动本地 LangGraph 服务器：

```bash
langgraph dev
```

服务器将在 `http://localhost:5433` 启动，并打开 LangGraph Studio 界面。

#### 方式二：Jupyter Notebook

运行交互式 Notebook：

```bash
uv run jupyter notebook research_agent.ipynb
```

## 项目结构

```
deep-research-demo/
├── pyproject.toml           # 项目配置
├── .env.example             # 环境变量示例
├── langgraph.json           # LangGraph 配置
├── agent.py                 # 主 Agent 工厂
├── prompts.py               # 所有子 Agent 的系统提示词
├── tools.py                 # 自定义工具
├── README.md                # 本文件
├── SPEC.md                  # 设计规格文档
└── research_agent/          # 运行时目录（研究输出）
    ├── evidence/
    │   └── search_results.md
    ├── exploration/
    │   └── insights.md
    ├── analysis/
    │   └── synthesis.md
    ├── outline/
    │   ├── outline.md
    │   ├── current.md
    │   └── review_feedback.md
    └── final_report.md
```

## 工作流程

```
                    ┌─→ exploration (并行)
                    │
evidence ──→ data-analysis ──→ outline ──→ review ──→ [迭代] ──→ write
```

1. **并行研究**：evidence 和 exploration 同时启动
2. **数据整理**：data-analysis 整理证据
3. **大纲生成**：outline 基于所有材料生成大纲
4. **审核迭代**：review 审核，outline 修订（最多 3 次）
5. **报告撰写**：write 生成最终报告

## 自定义

### 修改模型

默认使用 `claude-sonnet-4-5-20250929`。在 `agent.py` 中修改：

```python
from langchain.chat_models import init_chat_model

model = init_chat_model(model="anthropic:claude-sonnet-4-5-20250929", temperature=0.0)
```

### 修改系统提示词

编辑 `prompts.py` 中的各个指令常量。

### 添加自定义工具

在 `tools.py` 中添加新工具，并在 `agent.py` 中引入。

## 参考

- [deepagents 框架](https://github.com/langchain-ai/deepagents)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [深度研究课程](https://academy.langchain.com/courses/deep-research-with-langgraph)
