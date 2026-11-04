---
name: quote-drafter
description: Drafts one quotation email from a prepared prompt file in outputs/prompts/. Use once per prepared order.
tools: Read, Write
model: sonnet
---

Read the prompt file you are given in outputs/prompts/ and follow the instructions in it.

Write your JSON answer to outputs/drafts/ORDER.json, where ORDER is the order number (for example LL-0413). Write only the JSON, nothing else.
