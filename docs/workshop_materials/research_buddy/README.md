# Research Buddy — build it yourself

A tiny agentic flow you build from scratch in about seven minutes. Five standard LangFlow nodes, four wires, no custom Python. The smallest possible demo of an LLM that picks tools at runtime.

```
[Chat Input]  ──►  [ Agent ]  ──►  [Chat Output]
                    ▲    ▲
                    │    │
          [Wikipedia]  [Calculator]
          (tool mode)  (tool mode)
```

## Build it from scratch

1. From the **Input/Output** sidebar, drag in **Chat Input** and **Chat Output**.
2. From **Models & Agents**, drag in **Agent**.
3. From the components panel, drag in **Wikipedia** (under "Wikipedia") and **Calculator** (under "Utilities"). On each of these two nodes, toggle **Tool Mode** ON — the small wrench icon in the node header.
4. Draw four edges:
   - Chat Input → Agent (Input)
   - Wikipedia → Agent (Tools)
   - Calculator → Agent (Tools)
   - Agent → Chat Output
5. Click the **Agent** node. In **Language Model**, pick **OpenAI** and then `openai/gpt-4o-mini`. Leave **API Key** blank — the workshop's KeyBroker token is wired through the container env.
6. Paste the **Agent Instructions** below into the Agent's Agent Instructions field.
7. Click **Playground**. Try one of the test prompts.

Stuck? The completed `Research_Buddy` flow is already in your account — open it and compare your wiring side by side.

## Agent Instructions (paste into the Agent node)

```
You are a helpful research assistant. When the user asks a factual question, use the Wikipedia API to look it up. When the user asks anything requiring arithmetic, use the Calculator. If a question needs both — for example, 'what's the population of Tokyo divided by the population of Osaka?' — call the tools in sequence and show your reasoning step by step. When you cite a Wikipedia fact, mention the article you used.
```

That's the whole system prompt. Three rules: prefer Wikipedia for facts, prefer Calculator for math, chain them when both are needed.

## Test prompts

Try these in Playground. Each exercises a different tool-call pattern.

### Calculator only

```
What is 23 percent of 7.8 million?
```

Expected: `1,794,000`. Run time ~2–4 seconds. You'll see one expandable "Calling tool: evaluate_expression" card in the chat before the final answer.

### Wikipedia only

```
What is the population of Tokyo? Look it up on Wikipedia.
```

The reply should cite the article (e.g., "from the Wikipedia article on Tokyo") because the system prompt requires it.

### Both tools, in sequence

```
What is the population of Tokyo divided by the population of Osaka? Show your work.
```

The most interesting prompt. The agent should call Wikipedia twice (Tokyo, then Osaka), then call Calculator with the ratio, then compose the answer. Run time ~10–20 seconds. Three tool-call cards stack up in the Playground before the final reply — this is the canonical visual of the agentic pattern.

## Two things that catch people out

**Tool Mode must be ON.** Without it, the Wikipedia and Calculator components only expose a regular JSON output, not the `Tool` handle the Agent needs. The toggle is in the node header.

**Don't paste an OpenAI API key.** The Agent's API Key field stays blank. The workshop's KeyBroker proxy is wired via the container's `OPENAI_API_KEY` env var, which gives you rate-limit protection. Pasting your own key overrides the broker.

## Edits worth trying

Quick experiments once your build works.

Add a third behavioural rule to the Agent Instructions:
> *If the user asks a question that requires neither Wikipedia nor arithmetic, answer from your own knowledge but say so explicitly.*

Try `What is the capital of France?` before and after. Watch the tool-call cards disappear after the edit.

Demand structured output. Replace the whole system prompt with:
> *You are a research assistant. Answer the user's question by calling tools as needed. Reply in this exact format:*
> *Question: <restate>*
> *Tools used: <comma-separated names>*
> *Reasoning: <one short paragraph>*
> *Answer: <final answer>*

Run the same test prompts. The structure is now identical every run — a small taste of what Scenario D's rigid output shape buys you.

## More on the tools (optional)

The Agent decides between tools using each tool's **action name** and **description**. See [`tool_actions.md`](tool_actions.md) for what those look like for Wikipedia and Calculator, plus a list of other stock tools you can wire in (Current Date, URL, DuckDuckGo Search, ArXiv).
