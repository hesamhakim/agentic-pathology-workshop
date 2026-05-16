# Scenario 0 — General Chatbot system prompt

Default value of the `system_prompt` field on the **General Chatbot** node.
Source: [`general_chatbot.py`](../../../langflow_flows/components/api_scenario_zero/general_chatbot.py).

To edit: click the General Chatbot node → right-side panel → System Prompt textarea → paste your edited version → run.

```
You are a helpful AI assistant. The user may
attach one or more files (PDFs, text documents, or similar) for context.
Read any provided files carefully and use their content to answer the
user's questions accurately and concisely. If the user asks something
that cannot be answered from the provided files, say so plainly. Do
not invent facts. Match the user's tone and depth of detail.
```

That is intentionally generic. The whole point of Scenario 0 is to compare *this* against Scenario D's structured, multi-stage prompt set. Don't expect lane discipline, evidence trace, or a fixed report structure from a six-sentence system prompt.

## Suggested edits to try

These edits don't make the chatbot agentic — they just stress-test how much you can squeeze out of a single LLM call by tightening one prompt:

1. **Add an output structure.** Append:
   > *Reply in five sections: Patient · Per-modality summary · Discordances and how you resolved them · Final integrated diagnosis · Prognostic notes.*

2. **Add a lane-discipline rule.** Append:
   > *DNMT3A is a prognostic variant in AML, not a classifying one. Do NOT include it in the diagnosis line; place it only in prognostic notes.*

3. **Demand citations.** Append:
   > *For every claim, name which of the attached PDF filenames supported it. If you cannot, say "no support."*

Run the same user prompt before and after each edit and watch what improves — and what still slips through. This is the motivation for Scenario D.
