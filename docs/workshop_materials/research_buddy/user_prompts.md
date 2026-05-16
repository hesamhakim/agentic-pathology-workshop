# Research Buddy — Test prompts

Three prompts that exercise different tool-call patterns. All three
have been verified end-to-end against the workshop VM via the
KeyBroker proxy on 2026-05-16.

## 1. Calculator only

```
What is 23 percent of 7.8 million?
```

The agent should call **only** the Calculator. Expected: `1,794,000`. Run time ~2–4 s.

What to look at: in Playground, before the final answer, you'll see a small "Calling tool: evaluate_expression" expandable card. Open it — you can see the exact expression the agent built (`0.23 * 7800000`) and the raw result it got back.

## 2. Wikipedia only

```
What is the population of Tokyo? Look it up on Wikipedia.
```

The agent should call **only** Wikipedia. The instruction "Look it up on Wikipedia" makes it explicit, but try it without that phrase too — the agent usually still chooses Wikipedia because the question is factual.

The reply should include the article title (e.g., "from the Wikipedia article on Tokyo") because the agent's system prompt requires citation.

## 3. Both tools, in sequence

```
What is the population of Tokyo divided by the population of Osaka? Show your work.
```

The most interesting prompt. The agent should:

1. Call Wikipedia (search: Tokyo) → get the population
2. Call Wikipedia (search: Osaka) → get the population
3. Call Calculator (expression: `<tokyo_pop> / <osaka_pop>`) → get the ratio
4. Compose a final reply showing both numbers and the ratio

Run time ~10–20 s because there are three sequential tool calls.

In Playground you should see three expandable tool-call cards stacked before the final answer. This is the **canonical visual of the agentic pattern** — tool-decide-call-read-decide-call-...-answer.

## Variants for a deeper dive

### Force a single-tool error

```
What is 17 percent of "the population of Osaka"?
```

Watch the agent disambiguate. It may either (a) call Wikipedia first to get the number, then Calculator, or (b) tell you the prompt is ambiguous. Both are reasonable agent responses.

### Tool-not-needed prompt

```
What is the capital of France?
```

Without the system-prompt edit (#1 in [`agent_instructions.md`](agent_instructions.md)), the agent often calls Wikipedia even though it doesn't need to. With the edit, it answers from its own knowledge with an explicit "from my own knowledge" note.

### Three-tool prompt (if you've added Current Date)

After dragging in **Current Date** (Tools / Utilities) and toggling Tool Mode on:

```
How many days until July 4th 2027?
```

The agent should call Current Date, then Calculator. Same pattern, three tools available.

## What "wrong" output looks like

| Symptom | Why |
|---|---|
| Agent answers from training data instead of using a tool | Either the system prompt isn't clear enough, or Tool Mode is OFF on the tool node — re-check the node header |
| `No model selected` error | Click the Agent node, pick OpenAI + `openai/gpt-4o-mini` in the Language Model dropdown |
| Tool call hangs or 401s | Check that the Agent's API Key field is **blank** — pasting a key overrides the broker auth |
| Agent makes up Wikipedia content | The tool call succeeded but the agent paraphrased poorly — adjust the system prompt to require verbatim quotes |
