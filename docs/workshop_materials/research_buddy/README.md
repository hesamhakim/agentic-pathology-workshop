# Research Buddy — build it yourself

The workshop's "build it yourself" reference flow. **Five standard
LangFlow nodes, four wires, no custom Python.** Demonstrates the
agentic pattern (an LLM that picks tools at runtime) with the smallest
possible footprint.

## Topology

```
[Chat Input]  ──►  [ Agent ]  ──►  [Chat Output]
                    ▲    ▲
                    │    │
          [Wikipedia]  [Calculator]
          (tool mode)  (tool mode)
```

The Agent receives the user's question, decides which tool (or both!) to call, reads each tool's result, and composes a final reply.

## How to run

1. Sign in to the workshop VM and open `Research_Buddy` from "My Projects."
2. Click **Playground**.
3. Paste any prompt from [`user_prompts.md`](user_prompts.md). Press send.
4. Watch the agent's reasoning — LangFlow surfaces each tool call inline in the chat (you'll see "Calling tool: evaluate_expression…" and "Calling tool: fetch_content…" before the final answer).

## How to build from scratch (the workshop exercise)

1. From the **Input/Output** sidebar, drag in **Chat Input** and **Chat Output**.
2. From **Models & Agents**, drag in **Agent**.
3. From **Tools / Wikipedia**, drag in **Wikipedia**. Toggle **Tool Mode** on (icon in the node header).
4. From **Tools / Utilities**, drag in **Calculator**. Toggle **Tool Mode** on.
5. Wire the four edges:
   - Chat Input → Agent (Input)
   - Wikipedia → Agent (Tools)
   - Calculator → Agent (Tools)
   - Agent → Chat Output
6. Click the Agent node. Set **Language Model** to **OpenAI** + `openai/gpt-4o-mini`. Leave **API Key** blank (the workshop's KeyBroker token is wired via the container env).
7. Paste the contents of [`agent_instructions.md`](agent_instructions.md) into the **Agent Instructions** field.
8. Click **Playground**. Try a prompt from [`user_prompts.md`](user_prompts.md).

If you get stuck, the completed reference flow is already imported into your account — open `Research_Buddy` and compare your wiring side by side.

## Materials

| File | What it is |
|---|---|
| [`agent_instructions.md`](agent_instructions.md) | The Agent's system prompt — copy-paste ready |
| [`user_prompts.md`](user_prompts.md) | Three verified test prompts that exercise Calculator only, Wikipedia only, and both in sequence |
| [`tool_actions.md`](tool_actions.md) | What the Agent "sees" for each tool — name, description, args — so you understand how the LLM chooses between them |

## Two notes that catch people out

1. **Tool Mode must be ON** for Wikipedia and Calculator. Without it, the components only expose a regular JSON output, not the `Tool` handle the Agent needs. The toggle is in the node header (looks like a small wrench / "Tool" icon).
2. **Don't paste an OpenAI API key.** The workshop's KeyBroker proxy is wired via the container's `OPENAI_API_KEY` env var, so the Agent's API Key field stays blank. If you do paste a key, you'll override the broker and lose rate-limit protection.
