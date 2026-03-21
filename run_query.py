"""运行深度研究 Agent 的脚本 - 带详细实时调试输出"""
import os
import sys
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

print("[DEBUG] Environment loaded", flush=True)
print(f"[DEBUG] ANTHROPIC_API_KEY present: {bool(os.environ.get('ANTHROPIC_API_KEY'))}", flush=True)
print(f"[DEBUG] TAVILY_API_KEY present: {bool(os.environ.get('TAVILY_API_KEY'))}", flush=True)

from agent import agent
print("[DEBUG] Agent imported successfully", flush=True)
print(f"[DEBUG] Agent type: {type(agent)}", flush=True)

# 定义研究主题
query = "请帮我整理下目前全球具身智能发展的技术路线，以及各个路线的代表性公司，需要包括这些公司的技术路径，产品进度，商业化进度，融资情况，团队情况"

print(f"\n[INFO] Starting research on: {query}", flush=True)
print("=" * 60, flush=True)

# 使用 invoke 模式执行完整研究流程
# 注意: stream 模式在 deepagents 中与 MiniMax API 存在兼容性问题，会导致 write 子 agent 挂起
print("[DEBUG] Using invoke mode for complete research flow...", flush=True)
try:
    result = agent.invoke({"messages": [{"role": "user", "content": query}]})
    print("[DEBUG] Research completed successfully!", flush=True)
    print(f"[DEBUG] Result type: {type(result)}", flush=True)
    if isinstance(result, dict):
        for key, value in result.items():
            print(f"  {key}: {type(value).__name__}", flush=True)
except Exception as e:
    print(f"[ERROR] Exception during research: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.stdout.flush()

print("\n" + "=" * 60, flush=True)
print("[INFO] Research complete!", flush=True)