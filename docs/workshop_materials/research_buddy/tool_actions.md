# Research Buddy — Tool actions visible to the Agent

What the Agent's LLM call actually sees for each tool. When you toggle
Tool Mode on a component, LangFlow surfaces one or more **actions** —
each action is a function with a name, a description, and a JSON-schema
argument spec. The agent picks which action to call based on the
descriptions.

Source: pre-built into the flow JSON by [`build_research_buddy_flow.py::enable_tool_mode`](../../../scripts/build_research_buddy_flow.py).

## Wikipedia tool

| Field | Value |
|---|---|
| **Action name** | `fetch_content` |
| **Description** | *WikipediaComponent. fetch_content() - Search Wikipedia and return article summaries. Use this for factual lookups: people, places, populations, definitions, etc.* |
| **Arguments** | `input_value: string` — search query for Wikipedia |

When the agent decides to use Wikipedia, it generates a JSON-schema-valid function call like:

```json
{"name": "fetch_content", "arguments": {"input_value": "Tokyo population"}}
```

The Wikipedia component runs the search, fetches the top articles, and returns the content back to the agent as the tool result.

You can edit the action name and description in the **Actions** section of the Wikipedia node's right-side panel — useful if you want to give the LLM a more specific hint (e.g., rename to `lookup_factual_info` for a more general-purpose research agent).

## Calculator tool

| Field | Value |
|---|---|
| **Action name** | `evaluate_expression` |
| **Description** | *CalculatorComponent. evaluate_expression() - Perform basic arithmetic operations on a given expression.* |
| **Arguments** | `expression: string` — the arithmetic expression to evaluate (e.g., `'4*4*(33/22)+12-20'`) |

When the agent decides to use the Calculator, it generates:

```json
{"name": "evaluate_expression", "arguments": {"expression": "0.23 * 7800000"}}
```

The Calculator runs the expression through a safe arithmetic evaluator (no `eval()`, no arbitrary Python — just `+ - * / ( )` and decimals) and returns the result.

## Why descriptions matter

This is the lever that decides which tool gets called. If the descriptions are vague (e.g., a Wikipedia tool described as just *"search the internet"* and a Calculator described as *"do math"*) the agent will sometimes call the wrong one. The descriptions baked into the build script are deliberately concrete and example-rich.

Edit the descriptions in the node's **Actions** field if you want to:

- Steer the agent toward (or away from) a particular tool on edge-case prompts
- Narrow a tool's scope ("use this ONLY for population queries")
- Document a quirk ("note: Wikipedia article summaries may be 2–3 years old")

After editing, the change applies on the next run — same edit-and-rerun loop as the system prompt.

## Adding more tools

The same pattern works for any LangFlow component that supports tool mode. Useful additions:

| Component | Category | What it gives the agent |
|---|---|---|
| **Current Date** | Tools / Utilities | "What's today's date?" / "How many days since…" |
| **URL** | Tools / Data Source | "Fetch and summarize this URL" |
| **DuckDuckGo Search** | Tools / DuckDuckGo | Open-ended web search (no API key needed) |
| **ArXiv Search** | Tools / ArXiv | "Find recent papers on…" — for a research-paper agent |

For each: drag the component onto the canvas, toggle Tool Mode on, edit the action name + description if you want, then wire the `Tool` output handle into the Agent's `Tools` input. Update the Agent Instructions ([`agent_instructions.md`](agent_instructions.md)) to mention when the new tool should be used.
