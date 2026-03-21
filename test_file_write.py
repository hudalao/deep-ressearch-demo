"""测试 deepagents task() 是否会自动写入文件"""
from dotenv import load_dotenv
load_dotenv()

import os
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent

# 创建测试 agent
model = ChatOpenAI(
    model='MiniMax-M2.7',
    api_key=os.environ.get('ANTHROPIC_API_KEY'),
    base_url='https://api.minimax.chat/v1',
    temperature=0.0,
)

# 带 write_file 工具的子代理
test_subagent = {
    "name": "test_writer",
    "description": "Test subagent",
    "system_prompt": """你是一个测试助手。请将以下内容写入 /tmp/test_output.txt：

# 测试报告

这是测试内容。

""",
    "tools": [],  # 应该使用 deepagents 内置的 write_file
}

agent = create_deep_agent(
    model=model,
    tools=[],
    system_prompt="请调用 test_writer 子代理，让它写入文件。",
    subagents=[test_subagent],
)

# 运行
print("Starting test...")
result = agent.invoke({"messages": [{"role": "user", "content": "请调用 test_writer 子代理，让它写入文件。"}]})
print(f"Result: {result}")

# 检查文件是否存在
if os.path.exists('/tmp/test_output.txt'):
    print("SUCCESS: File was written!")
    with open('/tmp/test_output.txt') as f:
        print(f"Content: {f.read()}")
else:
    print("FAILED: File was NOT written")