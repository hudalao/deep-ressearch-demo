"""深度研究多 Agent 系统 - 主 Agent 工厂。

基于 deepagents 框架创建包含 6 个子代理的深度研究系统。
"""

from datetime import datetime

from langchain.chat_models import init_chat_model

from deepagents import create_deep_agent

from prompts import (
    DATA_ANALYSIS_INSTRUCTIONS,
    EVIDENCE_INSTRUCTIONS,
    EXPLORATION_INSTRUCTIONS,
    ORCHESTRATOR_WORKFLOW,
    OUTLINE_INSTRUCTIONS,
    REVIEW_INSTRUCTIONS,
    WRITE_INSTRUCTIONS,
)
from tools import tavily_search, think_tool

# 超参数
max_outline_iterations = 3
max_researcher_iterations = 3

# 获取当前日期
current_date = datetime.now().strftime("%Y-%m-%d")

# 合并 Orchestrator 指令
orchestrator_instructions = (
    ORCHESTRATOR_WORKFLOW.format(
        max_outline_iterations=max_outline_iterations,
        max_researcher_iterations=max_researcher_iterations,
    )
)

# ============================================================
# 子代理定义
# ============================================================

# 1. evidence 子代理 - 信息检索
evidence_sub_agent = {
    "name": "evidence",
    "description": "通过网络搜索获取研究主题的搜索结果",
    "system_prompt": EVIDENCE_INSTRUCTIONS.format(date=current_date),
    "tools": [tavily_search, think_tool],
}

# 2. exploration 子代理 - 创新观点探索
exploration_sub_agent = {
    "name": "exploration",
    "description": "对研究主题产生创新性和深度观点",
    "system_prompt": EXPLORATION_INSTRUCTIONS.format(date=current_date),
    "tools": [tavily_search, think_tool],
}

# 3. data-analysis 子代理 - 数据整理分析
data_analysis_sub_agent = {
    "name": "data-analysis",
    "description": "对研究结果中的长文本内容进行整理和分析",
    "system_prompt": DATA_ANALYSIS_INSTRUCTIONS.format(date=current_date),
    "tools": [think_tool],  # 使用 deepagents 内置的 read_file, write_file
}

# 4. outline 子代理 - 报告大纲生成
outline_sub_agent = {
    "name": "outline",
    "description": "基于研究材料生成或修订报告大纲",
    "system_prompt": OUTLINE_INSTRUCTIONS.format(date=current_date),
    "tools": [think_tool],  # 使用 deepagents 内置的 read_file, write_file, edit_file
}

# 5. review 子代理 - 大纲审核
review_sub_agent = {
    "name": "review",
    "description": "审核大纲与证据的一致性并提供反馈",
    "system_prompt": REVIEW_INSTRUCTIONS.format(date=current_date),
    "tools": [think_tool],  # 使用 deepagents 内置的 read_file, write_file
}

# 6. write 子代理 - 报告撰写
write_sub_agent = {
    "name": "write",
    "description": "基于大纲和源材料撰写完整报告各章节",
    "system_prompt": WRITE_INSTRUCTIONS.format(date=current_date),
    "tools": [],  # 使用 deepagents 内置的 read_file, write_file
}

# 所有子代理列表
subagents = [
    evidence_sub_agent,
    exploration_sub_agent,
    data_analysis_sub_agent,
    outline_sub_agent,
    review_sub_agent,
    write_sub_agent,
]

# ============================================================
# 模型初始化
# ============================================================

# 使用 Claude Sonnet 4.5
model = init_chat_model(model="anthropic:claude-sonnet-4-5-20250929", temperature=0.0)

# ============================================================
# 创建 Agent
# ============================================================

agent = create_deep_agent(
    model=model,
    tools=[tavily_search, think_tool],
    system_prompt=orchestrator_instructions,
    subagents=subagents,
)
