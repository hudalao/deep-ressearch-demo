"""手动触发 write 阶段生成报告"""
import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from deepagents.backends import FilesystemBackend

# 加载 .env
load_dotenv()

# 初始化模型和后端
model = ChatOpenAI(
    model='MiniMax-M2.5',
    api_key=os.environ.get('ANTHROPIC_API_KEY'),
    base_url='https://api.minimaxi.com/v1',
    temperature=0.0,
)
backend = FilesystemBackend(
    root_dir=os.path.abspath('research_agent'),
    virtual_mode=True
)

# 读取所有源材料
print("=== Reading source materials ===")

with open('research_agent/outline/outline.md', 'r') as f:
    outline = f.read()
print(f'Outline: {len(outline)} chars')

evidences_content = ""
for f in os.listdir('research_agent/evidence'):
    if f.endswith('.md'):
        with open(f'research_agent/evidence/{f}', 'r') as fp:
            evidences_content += fp.read() + "\n\n"
print(f'Evidence: {len(evidences_content)} chars')

explorations_content = ""
for f in os.listdir('research_agent/exploration'):
    if f.endswith('.md'):
        with open(f'research_agent/exploration/{f}', 'r') as fp:
            explorations_content += fp.read() + "\n\n"
print(f'Exploration: {len(explorations_content)} chars')

synthesis_content = ""
for f in os.listdir('research_agent/analysis'):
    if f.endswith('.md'):
        with open(f'research_agent/analysis/{f}', 'r') as fp:
            synthesis_content += fp.read() + "\n\n"
print(f'Synthesis: {len(synthesis_content)} chars')

# 构建写作 prompt
write_prompt = f"""你是一个专业报告写作助手，负责根据大纲和源材料撰写完整报告。

任务：基于最终大纲和对应的源材料，撰写一份全面、专业的深度研究报告。

写作原则：
1. 专业性：像专业研究员一样写作
2. 全面性：每个部分都要有实质性内容
3. 清晰性：使用清晰的标题和段落结构
4. 引用：所有主张都需要引用支持
5. 连贯性：章节之间要有逻辑衔接

引用规则：
- 使用 [1]、[2]、[3] 格式进行内联引用
- 每个唯一 URL 在所有发现中分配一个编号
- 来源按顺序编号，不间断
- 在报告末尾的 ### 来源 部分列出所有来源

禁止事项：
- 不要使用自我参照语言（"我发现了..."，"我研究了..."）
- 不要写元评论（"本报告旨在..."）
- 不要只有要点而没有详细解释

========== 报告大纲 ==========
{outline}

========== 证据资料 ==========
{evidences_content}

========== 探索观点 ==========
{explorations_content}

========== 综合分析 ==========
{synthesis_content}

请撰写完整报告。
"""

print("\n=== Starting report generation ===")
print(f"Prompt length: {len(write_prompt)} chars")

# 调用模型
result = model.invoke(write_prompt)
report_content = result.content

print(f"Generated report: {len(report_content)} chars")

# 写入 final_report.md
async def write_report():
    await backend.awrite('/final_report.md', report_content)
    print("Report written to /final_report.md")

asyncio.run(write_report())
print("\n=== Report generation complete ===")
