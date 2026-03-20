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
- `ANTHROPIC_API_KEY` - Anthropic API Key (required)
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

### Option 2: Jupyter Notebook

```bash
source .venv/bin/activate
uv run jupyter notebook research_agent.ipynb
```

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

Edit `agent.py` and modify the `init_chat_model` call:

```python
model = init_chat_model(model="anthropic:claude-sonnet-4-5-20250929", temperature=0.0)
```

### Modify System Prompts

Edit [prompts.py](prompts.py) - all sub-agent instructions are defined there.

### Add Custom Tools

Add new tools in [tools.py](tools.py) and import them in `agent.py`.
