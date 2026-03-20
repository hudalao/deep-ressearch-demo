"""自定义工具模块。

提供搜索和内容处理工具，供研究子 Agent 使用。
"""

import httpx

from langchain_core.tools import InjectedToolArg, tool
from markdownify import markdownify
from tavily import TavilyClient
from typing_extensions import Annotated, Literal

tavily_client = TavilyClient()


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
    search_results = tavily_client.search(
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
