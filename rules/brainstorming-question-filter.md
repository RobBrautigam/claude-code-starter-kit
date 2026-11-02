# Brainstorming Question Filter

When invoked in brainstorming mode (via `superpowers:brainstorming` or any creative-design conversation), follow this question filter when asking the user anything.

## The rule

Every question to the user during brainstorming must:

1. **Lead with a recommendation and reasoning.** Not "what do you think about A vs B?" but "I recommend A because [reason]."
2. **Name 1-2 real alternatives if relevant.** Brief, with one-line trade-offs.
3. **Explain what changes if the user picks a non-recommended option.** This shows the cost/value of the alternative so they can decide quickly.

Never present pure-options questions ("A vs B vs C, what do you think?"). Never ask wide-open technical questions ("which database should we use?"). The default posture is to make the call and surface it for redirect, not to delegate the call.

## When to ask technical questions

Technical questions can come to the user when their judgment genuinely matters:

- Cost trade-offs (paid vs free tier, API spend implications)
- Future flexibility (does this lock us into a vendor or pattern?)
- Brand fit (does this affect how the product feels?)
- Operational reality (the user knows ops constraints you don't)

Even then, frame as a recommendation with the alternative explained, not as an open question.

## When the user explicitly engages

If they engage on a technical topic by asking a technical follow-up, proposing a specific approach, or saying "let me think about this with you", drop the recommendation-only posture and discuss as peers. The recommendation-only default applies to opening questions, not to explicit engagement.

In peer-discussion mode:
- Surface trade-offs honestly, not just confirmations of the user's leaning.
- If their proposed approach has a real flaw, name it directly.
- Once the discussion converges, lock the decision and move.

## How to ASK - inline by default, popup only for narrow cases

**Default: inline conversational text.** Ask the question directly in your chat output. Use a markdown bullet list for the 1-2 alternatives. The user types a one-line reply (or a redirect) and the conversation continues. This is the right shape for nearly every brainstorming question.

**Use the `AskUserQuestion` tool only when ALL of the following are true:**

1. The user faces a genuine multi-option choice where the rendered options layout adds clarity over inline bullets.
2. The choice is mutually exclusive (or you explicitly enable multi-select).
3. Side-by-side preview adds value (`AskUserQuestion` supports a `preview` field for ASCII mockups / code snippets).
4. It's an end-of-section checkpoint, not a mid-flow tactical question.

If those four conditions aren't all true, ask inline.

**Hard ceilings:**
- One `AskUserQuestion` per brainstorming session, maximum.
- Never use `AskUserQuestion` to ask the user to confirm a recommendation you've already made - that's a yes/no, inline.
- Never use `AskUserQuestion` when the user explicitly engaged on a topic. Peer discussion mode is inline only.

## Why this rule exists

Without it, brainstorming sessions degrade into "Claude lists options, user picks." That delegates synthesis to the user instead of doing it for them - and burns time on questions only the assistant should be answering.
