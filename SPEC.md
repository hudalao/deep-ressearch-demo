# 深度研究多 Agent 系统设计

## 概述

一个基于 deepagents 框架构建的多 Agent 深度研究系统，用于复杂问题求解、长链路推理和多源信息整合。

**框架**: deepagents (`create_deep_agent`)
**输出**: Markdown 报告 (`/final_report.md`)

---

## 架构

### 组件

| 组件 | 类型 | 描述 |
|------|------|------|
| Orchestrator | 主 Agent | 任务规划、子 Agent 调度、进度追踪、上下文路由 |
| evidence | 子 Agent | 通过网络搜索获取信息 |
| exploration | 子 Agent | 创新性和深度观点的探索 |
| data-analysis | 子 Agent | 长文本内容的整理与分析 |
| outline | 子 Agent | 报告大纲生成与更新 |
| review | 子 Agent | 大纲与证据的一致性审核 |
| write | 子 Agent | 完整报告生成 |

### Orchestrator 行为驱动

Orchestrator 的行为由其 `system_prompt` 驱动，定义了：
- 何时调用各个子 Agent
- Agent 间如何传递上下文（通过文件 + `task()` 结果）
- outline-review 迭代控制逻辑

---

## 工作流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Orchestrator (主 Agent)                            │
│                                                                      │
│  1. write_todos ──▶ 分解研究任务为待办事项                            │
│                                                                      │
│  2. 并行执行:                                                         │
│     ├─▶ task(evidence) ──▶ write_file(/evidence/)                    │
│     └─▶ task(exploration) ──▶ write_file(/exploration/)             │
│                                                                      │
│  3. task(data-analysis) ──▶ write_file(/analysis/)                   │
│                                                                      │
│  4. task(outline) ──▶ write_file(/outline/)                         │
│                                                                      │
│  5. task(review) ──▶ 决策: 通过 / 失败 + 反馈                        │
│            │                                                          │
│            │ (如果失败, 最多迭代 max_outline_iterations 次)            │
│            └────────────────────────────────────────┐                │
│                                                     ▼                │
│  6. task(write) ──▶ write_file(/final_report.md)                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 迭代机制

outline-review 循环持续执行，直到满足以下条件之一：
- `review` 输出 "PASS"（大纲与证据一致），或
- 达到 `max_outline_iterations` 上限（默认 3 次）

**达到最大迭代次数时的行为**：
- Orchestrator 记录警告
- 使用当前可用的大纲继续进入 `write` 阶段
- 最终报告中标注大纲可能未完全验证

**迭代文件管理**：
- Orchestrator 维护 `/outline/current.md` 作为工作副本
- 每次迭代：Orchestrator 复制 `outline.md` → `current.md`，然后调用 outline
- 历史版本可选保留为 `/outline/v1.md`、`/outline/v2.md` 用于调试

**迭代失败时的处理**：
1. `review` 将反馈写入 `/outline/review_feedback.md`
2. Orchestrator 复制 `/outline/outline.md` → `/outline/current.md`
3. `outline` 读取：`/outline/current.md` + `/outline/review_feedback.md` + 源文件
4. `outline` 生成修订版 `/outline/outline.md`

---

## 子 Agent 详细规格

### 1. evidence（证据获取）

```python
{
    "name": "evidence",
    "description": "通过网络搜索获取研究主题的搜索结果",
    "system_prompt": EVIDENCE_INSTRUCTIONS,
    "tools": [tavily_search, think_tool],
}
```

**职责**：
- 使用 Tavily 执行网络搜索
- 获取完整网页内容
- 返回带引用的结构化发现

**输出文件**: `/evidence/search_results.md`

---

### 2. exploration（探索）

```python
{
    "name": "exploration",
    "description": "对研究主题产生创新性和深度观点",
    "system_prompt": EXPLORATION_INSTRUCTIONS,
    "tools": [tavily_search, think_tool],
}
```

**职责**：
- 进行超出直接搜索结果的探索性研究
- 识别新颖角度、反面观点、新兴趋势
- 发散性思考，挖掘非显而易见的洞察

**输出文件**: `/exploration/insights.md`

---

### 3. data-analysis（数据分析）

```python
{
    "name": "data-analysis",
    "description": "对研究结果中的长文本内容进行整理和分析",
    "system_prompt": DATA_ANALYSIS_INSTRUCTIONS,
    "tools": [read_file, write_file, think_tool],
}
```

**职责**：
- 读取原始证据文件
- 综合和分类发现
- 识别模式、主题和关联
- 为大纲构建做准备的结构化分析

**输出文件**: `/analysis/synthesis.md`

---

### 4. outline（大纲）

```python
{
    "name": "outline",
    "description": "基于研究材料生成或修订报告大纲",
    "system_prompt": OUTLINE_INSTRUCTIONS,
    "tools": [read_file, write_file, edit_file],
}
```

**职责**：
- 读取证据、分析和探索文件
- 生成带章节/子章节的结构化报告大纲
- 根据 review 反馈修订大纲

**输入文件**：
- `/evidence/search_results.md`
- `/analysis/synthesis.md`
- `/exploration/insights.md`
- `/outline/current.md`（上一版本，仅在第一次迭代后存在）
- `/outline/review_feedback.md`（仅在 review 失败时存在）

**输出文件**: `/outline/outline.md`

**迭代处理**：修订时（当存在 review 反馈时），读取之前的大纲和反馈，然后覆盖为改进版本。

---

### 5. review（审核）

```python
{
    "name": "review",
    "description": "审核大纲与证据的一致性并提供反馈",
    "system_prompt": REVIEW_INSTRUCTIONS,
    "tools": [read_file, write_file, think_tool],
}
```

**职责**：
- 对比大纲中的主张与证据
- 识别缺失的主题或不一致之处
- 输出 PASS/FAIL 决策及具体反馈

**输入文件**: `/outline/outline.md`、`/evidence/search_results.md`
**输出文件**: `/outline/review_feedback.md`

**输出格式**（写入文件）：
```
VERDICT: PASS | FAIL
ISSUES: [如果 FAIL，列出具体问题]
SUGGESTIONS: [如果 FAIL，给出具体改进建议]
```

---

### 6. write（写作）

```python
{
    "name": "write",
    "description": "基于大纲和源材料撰写完整报告各章节",
    "system_prompt": WRITE_INSTRUCTIONS,
    "tools": [read_file, write_file],
}
```

**职责**：
- 阅读最终大纲
- 阅读各章节对应的源材料
- 撰写全面、有适当引用的报告

**输出文件**: `/final_report.md`

---

## 子 Agent System Prompt（待实现）

所有子 Agent 的 system prompt 在 `prompts.py` 中定义：

| 常量 | 对应 Agent | 描述 |
|------|------------|------|
| `EVIDENCE_INSTRUCTIONS` | evidence | 网络搜索和内容获取指南 |
| `EXPLORATION_INSTRUCTIONS` | exploration | 创意研究和观点生成 |
| `DATA_ANALYSIS_INSTRUCTIONS` | data-analysis | 内容综合和模式识别 |
| `OUTLINE_INSTRUCTIONS` | outline | 报告结构和章节规划 |
| `REVIEW_INSTRUCTIONS` | review | 一致性检查和反馈 |
| `WRITE_INSTRUCTIONS` | write | 带引用的完整报告生成 |
| `ORCHESTRATOR_WORKFLOW` | orchestrator | 主工作流程和委托逻辑 |

这些常量在 `agent.py` 中创建 agent 时从 `prompts.py` 导入。

---

## 上下文传递机制

遵循 deepagents 参考实现的模式：

1. **Orchestrator 通过 `task()` 工具调用子 Agent**
2. **子 Agent 的输出作为工具结果返回**
3. **Orchestrator 将相关结果写入共享文件**
4. **下游子 Agent 通过 `read_file` 工具读取文件**

示例流程：
```
task(evidence, topic="AI 安全") → 返回结果
write_file("/evidence/ai_safety.md", 结果)
task(data_analysis) → 读取 /evidence/，写入 /analysis/
...
```

---

## 超参数

| 参数 | 默认值 | 描述 |
|------|--------|------|
| `max_outline_iterations` | 3 | outline-review 循环最大迭代次数 |
| `max_researcher_iterations` | 3 | evidence/exploration Agent 的最大搜索迭代次数 |

**注意**：并行执行通过在单个 Orchestrator 响应中发起多个 `task()` 调用实现。Orchestrator 可使用 deepagents 内置工具：`write_todos`、`write_file`、`read_file`、`edit_file`、`ls`、`glob`、`grep`、`execute`、`task()`。

---

## 文件结构

```
deep-research-demo/
├── pyproject.toml
├── .env.example
├── langgraph.json
├── agent.py                    # 主 Agent 工厂
├── prompts.py                  # 所有子 Agent 的 system prompt
├── tools.py                    # 自定义工具（tavily_search 等）
├── orchestrator_prompts.py     # Orchestrator 工作流指令
└── research_demo/
    └──（运行时创建的研究输出文件）
        ├── evidence/
        │   └── search_results.md
        ├── exploration/
        │   └── insights.md
        ├── analysis/
        │   └── synthesis.md
        ├── outline/
        │   ├── outline.md          # 当前工作大纲
        │   ├── current.md          # 前一次迭代的副本
        │   └── review_feedback.md  # Review 输出（如果 FAIL）
        └── final_report.md
```

---

## 报告输出格式

`/final_report.md` 结构：

```markdown
# 标题

## 第一章
内容，包含内联引用 [1][2]...

## 第二章
...

### 来源
[1] 标题: URL
[2] 标题: URL
```

**引用规则**：
- 使用 [1]、[2]、[3] 格式进行内联引用
- 每个唯一 URL 在所有发现中分配一个编号
- 来源按顺序编号，不间断

---

## 实现阶段

### 阶段一：基础搭建
- 建立项目结构
- 定义所有 6 个子 Agent 的规格
- 使用 `create_deep_agent` 实现 `agent.py`

### 阶段二：核心工作流
- 在 prompt 中实现 Orchestrator 工作流
- 实现 outline-review 迭代循环
- 端到端流程测试

### 阶段三：优化增强
- 更精细的 prompt 工程
- 迭代控制优化
- 添加评估指标

---

## 依赖

基于 deepagents 参考实现 + 额外依赖：

```
deepagents>=0.2.6
langchain-anthropic
langchain_tavily
tavily-python
markdownify
httpx
```

---

## 参考

- deepagents 框架：https://github.com/langchain-ai/deepagents
- 参考实现：`deepagents/examples/deep_research/`
