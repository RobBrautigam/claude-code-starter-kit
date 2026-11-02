# Starter Prompt Code-Block Integrity

Every copy-paste artifact delivered to the user - starter prompts, multi-line scripts, copy-paste templates - MUST render as ONE intact fenced code block in the conversation. Never two. Never three. Never with mid-prompt seams where the outer fence broke.

This is a non-negotiable rendering rule.

## The bug this prevents

Markdown code fences close at the first matching fence of the same length. If you wrap a prompt in ``` and the prompt body contains ``` (e.g., an embedded `````python` block), the outer fence closes at the inner one and the rest of the prompt renders as plain markdown. The result: the user sees the prompt as 2-3 separate code blocks with prose seams between them, and copy-paste loses the heading structure they wanted.

## The rule

When delivering any copy-paste artifact that contains its own code fences inside:

- **Use a 4-backtick fence for the outer wrapper** (`````` ) when the body contains any ``` inner fences. The 4-tick fence only closes on another 4-tick line, so 3-tick inner blocks render normally inside.
- **Default to 4-tick outer fences for ALL starter prompts**, even ones you think have no inner ```. Cheap insurance. Costs nothing if there's no inner fence.
- **Alternative:** wrap with `~~~` (tildes) instead of backticks. Tildes never collide with backtick fences. Acceptable but less common; 4-tick is the preferred default.
- **Never** ship a starter prompt wrapped in only 3 backticks unless you've verified zero ``` exist anywhere in the body.

## Pre-send validation (do this every time)

Before sending a copy-paste artifact:

1. Count the fence-opens and fence-closes in your draft.
2. If the body contains any ``` lines, the outer wrapper MUST be `````` (4 ticks) or `~~~`.
3. Visualize: would the entire artifact render as a single fenced block? If you have any doubt, upgrade to 4-tick.

## Scope

Applies to:
- Starter prompts at session close (the main offender)
- Multi-step setup instructions the user is asked to paste somewhere
- Code snippets that contain other code blocks (rare but real)
- Any "here's the thing to copy" delivery

Does NOT apply to:
- Regular conversational responses with isolated code samples (those use normal 3-tick fences)
- Code blocks in your own markdown notes that aren't meant for copy-paste
