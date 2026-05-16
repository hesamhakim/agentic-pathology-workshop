# Scenario 0 — General Chatbot

A deliberately generic chatbot — the workshop's warm-up baseline. Three
nodes: Chat Input → General Chatbot → Chat Output. The General Chatbot
node accepts file attachments via the Playground's paperclip and passes
their contents to a single LLM call together with your typed prompt.

## How to run

1. Sign in to the workshop VM and open `0_general_chatbot` from "My Projects."
2. Click **Playground**.
3. Click the paperclip icon and attach the **four AML PDFs** listed in [`inputs.md`](inputs.md).
4. Paste one of the prompts from [`user_prompts.md`](user_prompts.md) into the chat input.
5. Press send. Wait ~10–30 seconds for the reply.

## What to look at in the reply

The point of this exercise is to feel what a generic chatbot *misses* before seeing what the agentic workflow adds. Ask yourself:

- Which of the four PDFs supports each sentence?
- Did **DNMT3A** land in the **diagnosis line** or the **prognostic notes**?
- Run the same prompt again — how much does the structure change?
- If a downstream LIS needed this as JSON, what would it parse?

## Materials

| File | What it is |
|---|---|
| [`inputs.md`](inputs.md) | Links to the four AML PDFs |
| [`system_prompt.md`](system_prompt.md) | The chatbot's own system prompt (read-only, embedded in the component) |
| [`user_prompts.md`](user_prompts.md) | Sample prompts to try |

## Editing this flow

The chatbot's behaviour comes from a single `system_prompt` field on the **General Chatbot** node. Click the node on the canvas → right-side panel → System Prompt textarea. The default is in [`system_prompt.md`](system_prompt.md).

For deeper edits, the component source is at [`langflow_flows/components/api_scenario_zero/general_chatbot.py`](../../../langflow_flows/components/api_scenario_zero/general_chatbot.py).
