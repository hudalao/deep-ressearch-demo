# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) for working with this repository.

## Project Overview

**deep-research-demo** is a multi-agent deep research system built on the deepagents framework, designed for complex problem solving, long-chain reasoning, and multi-source information integration.

## Setup

### 1. Install Dependencies

```bash
cd deep-research-demo
uv sync
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Required keys in `.env`:
- `ANTHROPIC_API_KEY` - Currently used for MiniMax API (configure base URL in agent.py)
- `TAVILY_API_KEY` - Tavily API Key (required, for web search - get one at https://app.tavily.com)
- `GOOGLE_API_KEY` - Google API Key (optional, for Gemini model)
- `LANGSMITH_API_KEY` - LangSmith API Key (optional, for tracing)

### 3. Install langgraph-cli (for local dev server)

```bash
source .venv/bin/activate
uv pip install "langgraph-cli[inmem]"
```

Note: If you encounter a lock timeout during installation, wait a few seconds and retry (another uv process may be holding a lock).

## Running

### Option 1: LangGraph Dev Server (Recommended)

```bash
source .venv/bin/activate
langgraph dev
```

Server starts at `http://localhost:5433` with LangGraph Studio UI.

### Option 2: Direct Python Script

```bash
source .venv/bin/activate
uv run python run_query.py
```

Note: Uses `agent.invoke()` mode for compatibility with MiniMax API.

## Project Structure

```
deep-research-demo/
├── agent.py                 # Main agent factory
├── prompts.py              # All sub-agent system prompts
├── tools.py                # Custom tools
├── research_agent/          # Runtime output directory
│   ├── evidence/           # Search results
│   ├── exploration/         # Insights
│   ├── analysis/           # Synthesis
│   ├── outline/            # Report outline
│   └── final_report.md     # Final output
├── pyproject.toml          # Project config
├── .env.example            # Env template
└── langgraph.json          # LangGraph config
```

## Key Files

- [agent.py](agent.py) - Agent initialization and model configuration
- [prompts.py](prompts.py) - System prompts for all sub-agents
- [tools.py](tools.py) - Custom tool definitions

## Customization

### Change Model

Current configuration uses **MiniMax-M2.5** (200K context) via OpenAI-compatible API.

To switch models, edit `agent.py` and modify the model initialization:

```python
# Current: MiniMax via OpenAI-compatible API
model = ChatOpenAI(
    model="MiniMax-M2.5",
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    base_url="https://api.minimaxi.com/v1",
    temperature=0.0,
)

# Alternative: Use Anthropic Claude
# from langchain_anthropic import ChatAnthropic
# model = ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0.0)

# Alternative: Use OpenAI
# from langchain_openai import ChatOpenAI
# model = ChatOpenAI(model="gpt-4o", temperature=0.0)
```

### Custom Model Providers

You can register custom model providers to use local LLM servers (Ollama, vLLM, LM Studio, etc.) or other OpenAI-compatible APIs.

#### Built-in Providers

**MiniMax** - Anthropic-compatible API (Anthropic SDK)

```python
from deepagents_cli.custom_providers import (
    register_custom_provider,
    MiniMaxProvider,
)
from deepagents import init_chat_model

# Register MiniMax (uses ANTHROPIC_API_KEY env var)
provider = MiniMaxProvider()
register_custom_provider(provider)

# Use in init_chat_model
model = init_chat_model("minimax:MiniMax-M2.7", temperature=0.0)
```

**OpenAI-Compatible Providers** (Ollama, vLLM, LM Studio, etc.)

```python
from deepagents_cli.custom_providers import (
    register_custom_provider,
    OpenAICompatibleProvider,
)
from deepagents import init_chat_model

# Register Ollama
provider = OpenAICompatibleProvider(
    name="ollama",
    base_url="http://localhost:11434/v1",
)
register_custom_provider(provider)

# Use it in init_chat_model
model = init_chat_model("ollama:llama3", temperature=0.0)
```

#### Using with deepagents CLI

After registering a custom provider, you can use it with the CLI:

```bash
deepagents --model ollama:llama3
```

#### Creating a Custom Provider

For fully custom model sources, implement the `CustomModelProvider` abstract class:

```python
from deepagents_cli.custom_providers import (
    register_custom_provider,
    CustomModelProvider,
)
from langchain_core.language_models import BaseChatModel

class MyCustomProvider(CustomModelProvider):
    @property
    def name(self) -> str:
        return "myprovider"

    def create_model(
        self,
        model_name: str,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        model_kwargs: dict | None = None,
    ) -> BaseChatModel:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model_name,
            base_url=base_url or "http://localhost:8000/v1",
            api_key=api_key or "EMPTY",
            **(model_kwargs or {}),
        )

register_custom_provider(MyCustomProvider())
```

### Modify System Prompts

Edit [prompts.py](prompts.py) - all sub-agent instructions are defined there.

### Add Custom Tools

Add new tools in [tools.py](tools.py) and import them in `agent.py`.

### Hyperparameters Configuration

Key configuration parameters in `agent.py`:

```python
max_outline_iterations = 3      # Maximum outline-review iterations
max_researcher_iterations = 3   # Maximum search iterations per researcher
enable_review = False           # Enable/disable review step (default: disabled)
```

When `enable_review=False` (default), the workflow skips the review step to reduce iteration overhead. Outline goes directly to report writing.

## Architecture

### Multi-Agent Workflow

The system uses an Orchestrator pattern with 6 specialized sub-agents:

```
                    ┌─→ evidence (parallel) ──┐
                    │                          │
                    └─→ exploration (parallel) ┘
                                │
                                ↓
                        data-analysis
                                │
                                ↓
                            outline
                                │
                                ↓ (if enable_review=True)
                            review ←──┐
                                │      │ (max 3 iterations)
                                └──────┘
                                │
                                ↓
                            write
                                │
                                ↓
                        final_report.md
```

### Sub-Agent Responsibilities

- **Orchestrator**: Coordinates workflow, calls sub-agents via `task()` tool
- **evidence**: Web search and information retrieval (uses Tavily)
- **exploration**: Generates innovative insights and novel perspectives
- **data-analysis**: Synthesizes and categorizes research findings
- **outline**: Creates structured report outline
- **review**: Validates outline-evidence consistency (optional, disabled by default)
- **write**: Generates final report with proper citations

### Context Passing

Agents communicate through filesystem:
1. Orchestrator calls sub-agent via `task()`
2. Sub-agent writes results to files (e.g., `/evidence/search_results.md`)
3. Downstream agents read via `read_file` tool
4. All outputs stored in `research_agent/` directory

## Development Commands

### Run Linting

```bash
source .venv/bin/activate
uv run ruff check .
```

### Run Type Checking

```bash
source .venv/bin/activate
uv run mypy .
```

### Install Development Dependencies

```bash
uv sync --extra dev
```
