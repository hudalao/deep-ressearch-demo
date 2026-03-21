"""自定义工具模块。

提供搜索和内容处理工具，供研究子 Agent 使用。
"""

import httpx

from langchain_core.tools import InjectedToolArg, tool
from markdownify import markdownify
from tavily import TavilyClient
from typing_extensions import Annotated, Literal

# Token 估算：中文1字≈1token，英文1词≈1.3token
def estimate_tokens(text: str) -> int:
    """估算文本的 token 数量。

    Args:
        text: 要估算的文本

    Returns:
        估算的 token 数量
    """
    # 简单估算：中文按字符数，英文按单词数 * 1.3
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    english_words = sum(1 for w in text.split() if w.isascii())
    other_chars = len(text) - chinese_chars - sum(len(w) for w in text.split() if w.isascii())

    return int(chinese_chars + english_words * 1.3 + other_chars * 0.4)

# Lazy initialization of tavily_client
_tavily_client = None

def _get_tavily_client():
    global _tavily_client
    if _tavily_client is None:
        # Bypass proxy for Tavily API
        import os
        os.environ['NO_PROXY'] = 'api.tavily.com'
        os.environ['no_proxy'] = 'api.tavily.com'
        _tavily_client = TavilyClient()
    return _tavily_client


def fetch_webpage_content(url: str, timeout: float = 10.0) -> str:
    """获取网页内容并转换为 Markdown 格式。

    Args:
        url: 要获取的 URL
        timeout: 请求超时时间（秒）

    Returns:
        网页内容的 Markdown 格式
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = httpx.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return markdownify(response.text)
    except Exception as e:
        return f"Error fetching content from {url}: {str(e)}"


@tool(parse_docstring=True)
def tavily_search(
    query: str,
    max_results: Annotated[int, InjectedToolArg] = 3,
    topic: Annotated[
        Literal["general", "news", "finance"], InjectedToolArg
    ] = "general",
) -> str:
    """在给定查询主题上搜索网络信息。

    使用 Tavily 发现相关 URL，然后获取并返回完整网页内容作为 Markdown。

    Args:
        query: 要执行的搜索查询
        max_results: 返回的最大结果数（默认 3）
        topic: 主题过滤器 - 'general'、'news' 或 'finance'（默认 'general'）

    Returns:
        包含完整网页内容的格式化搜索结果
    """
    search_results = _get_tavily_client().search(
        query,
        max_results=max_results,
        topic=topic,
    )

    result_texts = []
    for result in search_results.get("results", []):
        url = result["url"]
        title = result["title"]

        content = fetch_webpage_content(url)

        result_text = f"""## {title}
**URL:** {url}

{content}

---
"""
        result_texts.append(result_text)

    response = f"""🔍 找到 {len(result_texts)} 条关于 '{query}' 的结果：

{chr(10).join(result_texts)}"""

    return response


@tool(parse_docstring=True)
def log_warning(message: Annotated[str, "警告消息"]) -> str:
    """记录警告日志。

    当输入过大需要跳过某些步骤时使用。

    Args:
        message: 警告消息内容

    Returns:
        确认日志已记录
    """
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [WARN] {message}"
    print(log_entry, flush=True)
    return f"警告已记录: {message}"


@tool(parse_docstring=True)
def estimate_tokens_tool(text: Annotated[str, "要估算的文本"]) -> str:
    """估算文本的 token 数量。

    用于在调用子代理前检查输入大小，避免上下文溢出。

    规则：
    - 中文：1字符 ≈ 1 token
    - 英文：1单词 ≈ 1.3 tokens
    - 标点/空格：0.4 tokens

    Args:
        text: 要估算的文本

    Returns:
        估算的 token 数量
    """
    count = estimate_tokens(text)
    return f"估算 token 数: {count}"


@tool(parse_docstring=True)
def think_tool(reflection: str) -> str:
    """用于研究进展和决策的战略反思工具。

    在每次搜索后使用此工具分析结果并系统地规划下一步。
    这会在研究工作流中创建一个深思熟虑的暂停以进行质量决策。

    使用场景：
    - 收到搜索结果后：发现了哪些关键信息？
    - 决定下一步前：我是否有足够的信息来全面回答问题？
    - 评估研究差距：我还在缺少哪些关键信息？
    - 得出研究结论前：我现在能提供完整答案吗？

    反思应包括：
    1. 当前发现分析 - 我收集到了哪些具体信息？
    2. 差距评估 - 还在缺少哪些关键信息？
    3. 质量评估 - 我是否有足够的证据/示例来给出好的答案？
    4. 战略决策 - 我应该继续搜索还是提供答案？

    Args:
        reflection: 关于研究进展、发现、差距和下一步的详细反思

    Returns:
        确认反思已被记录以供决策使用
    """
    return f"反思已记录: {reflection}"


@tool(parse_docstring=True)
def log_agent_io(
    agent_name: Annotated[str, "子代理名称（如 evidence, exploration, write 等）"],
    input_data: Annotated[str, "输入给子代理的任务描述或数据"],
    output_data: Annotated[str, "子代理的输出或响应"],
    stage: Annotated[str, "当前阶段（如 task_start, task_complete, tool_call 等）"] = "info",
) -> str:
    """记录子代理的输入和输出，用于调试和追踪工作流。

    在 sub-agent 被调用时记录输入，完成时记录输出。
    这使得工作流的每个步骤都可追踪和可视化。

    Args:
        agent_name: 子代理名称（evidence, exploration, data-analysis, outline, write, review）
        input_data: 输入给子代理的任务描述或数据
        output_data: 子代理的输出或响应
        stage: 阶段标识 - 'task_start'（任务开始）, 'task_complete'（任务完成）, 'tool_call'（工具调用）

    Returns:
        确认日志已写入
    """
    import datetime
    import os

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    # 构建日志目录
    log_dir = os.path.join(os.path.dirname(__file__), "research_agent", "logs")
    os.makedirs(log_dir, exist_ok=True)

    # 写入按时间排序的详细日志
    log_file = os.path.join(log_dir, "agent_io.log")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*80}\n")
        f.write(f"[{timestamp}] [{stage.upper()}] {agent_name}\n")
        f.write(f"{'='*80}\n")
        f.write(f"--- INPUT ---\n{input_data}\n")
        f.write(f"\n--- OUTPUT ---\n{output_data}\n")
        f.write(f"\n")

    # 写入按 agent 分类的日志
    agent_log_file = os.path.join(log_dir, f"{agent_name}.log")
    with open(agent_log_file, "a", encoding="utf-8") as f:
        f.write(f"\n[{timestamp}] [{stage.upper()}]\n")
        f.write(f"INPUT:\n{input_data[:500]}..." if len(input_data) > 500 else f"INPUT:\n{input_data}\n")
        f.write(f"\nOUTPUT:\n{output_data[:500]}..." if len(output_data) > 500 else f"\nOUTPUT:\n{output_data}\n")
        f.write(f"\n{'-'*40}\n")

    # 控制台也输出
    print(f"[{timestamp}] [{agent_name}] {stage.upper()}", flush=True)
    print(f"  INPUT: {input_data[:200]}..." if len(input_data) > 200 else f"  INPUT: {input_data}", flush=True)

    return f"日志已写入: {agent_name}.log"
