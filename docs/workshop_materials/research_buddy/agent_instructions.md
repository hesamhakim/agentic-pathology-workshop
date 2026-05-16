# Research Buddy — Agent Instructions (system prompt)

Default value of the **Agent Instructions** field on the Agent node.
Source: [`build_research_buddy_flow.py::RESEARCH_BUDDY_INSTRUCTIONS`](../../../scripts/build_research_buddy_flow.py).

To edit: click the **Agent** node on the canvas → right-side panel → Agent Instructions textarea → paste your edited version → run.

```
You are a helpful research assistant. When the user asks a factual question, use the Wikipedia API to look it up. When the user asks anything requiring arithmetic, use the Calculator. If a question needs both — for example, 'what's the population of Tokyo divided by the population of Osaka?' — call the tools in sequence and show your reasoning step by step. When you cite a Wikipedia fact, mention the article you used.
```

## What this prompt does

- **Names each tool explicitly** so the LLM picks the right one. The Agent's tool-calling layer also gets each tool's structured `name` + `description` from the tool nodes themselves (see [`tool_actions.md`](tool_actions.md)), but a system prompt reminder helps.
- **Tells the model to chain tools when needed.** Without that line, the model often answers a Tokyo-vs-Osaka population question from its own training data instead of looking it up.
- **Requires citation.** Wikipedia replies include the article title; the agent has to repeat it back.

## Edits to try

### 1. Add a third behavioural rule

Add at the end:
> *If the user asks a question that requires neither Wikipedia nor arithmetic, answer from your own knowledge but say so explicitly.*

Try `What is the capital of France?` before and after — should now produce a one-line answer with "from my own knowledge" instead of an unnecessary Wikipedia call.

### 2. Demand structured output

Replace the whole prompt with:
> *You are a research assistant. Answer the user's question by calling tools as needed. Always reply in this exact format:*
> *Question: <restate the question>*
> *Tools used: <list of tool names, comma-separated>*
> *Reasoning: <one short paragraph>*
> *Answer: <the final answer>*

Run the same prompts as before. The structure is now identical every run — a tiny taste of what Scenario D's rigid output shape buys you.

### 3. Add a new tool to the system prompt before you add it to the canvas

If you drag in a third tool (say, **Current Date** from Tools / Utilities) but the Agent doesn't seem to use it, add this to the prompt:
> *When the user asks anything about today's date, the day of the week, or time elapsed since a date, use the Current Date tool.*

This shows the layered nature of tool-using agents: structural wiring (a Tool handle into Agent.tools), tool-level metadata (the tool's `description`), and system-prompt guidance all play together.
