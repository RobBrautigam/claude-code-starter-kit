# Session Loose-Ends Audit (every session close)

Before any session ends - at handoff/ship time, BEFORE delivering the terminal starter prompt - produce a **loose-ends audit**: a complete accounting of every idea, request, comment, or aside raised during the session, each tagged with its disposition. Nothing said gets silently dropped.

This rule exists because of a recurring failure: you bring up an idea mid-session, the agent works the main thread, and the aside evaporates at session close - lost until you re-raise it days or weeks later, sometimes repeatedly. The cost of the audit is one table; the cost of NOT doing it is you having to be the system's memory.

## When it runs

Every session that closes with a handoff, a ship, or a "we're done here." It is part of the close sequence, positioned:

1. ... all in-session work complete ...
2. **Loose-ends audit** (this rule)
3. Roadmap table (if the work spans multiple sessions)
4. Terminal starter prompt (per `rules/session-handoffs-required.md`)
5. Ship / version bump

If you explicitly ask for the audit mid-session, produce it then too - but it still runs again (or is confirmed still-current) at close.

## What to capture

Walk back through EVERY user message in the session - not just the formal task. Capture:

- Explicit requests ("build X", "add Y")
- Ideas and asides ("maybe we could...", "it would be cool if...", "down the road...")
- Questions that imply work ("why aren't we using X?")
- Preferences and constraints stated in passing
- "Future project" mentions (these are the most-dropped class)
- Anything the agent proposed that the user approved

## The disposition tags

Every captured item gets exactly one honest tag:

| Tag | Meaning |
|---|---|
| ✅ **Implemented** | Built + shipped this session |
| ⚠️ **Partial** | Some of it done; name the specific gap |
| 📋 **Queued** | Carried into the starter prompt / a follow-up - name where |
| 🌱 **Spun off** | Belongs to a separate project - state whether it was **tracked** (a project record / issue created) or only **mentioned** (not tracked yet) |
| 🔍 **Surfaced** | Diagnosed/raised for a decision, not actioned |
| 🔁 **Reframed** | Intentionally not done as literally stated; explain why + where it actually lives |
| ❌ **Dropped** | Consciously not doing it - say so explicitly so the user can veto |

## Honesty requirements (non-negotiable)

- **Tracking is binary.** If an idea is worth tracking, either a record exists (tracked) or it does not (mentioned only). Never imply "captured" when only a sentence in a starter prompt exists. State it plainly: "NOT tracked - mentioned only."
- **Name the gap on every ⚠️ Partial.** "Mostly done" is not a disposition. What exactly is missing?
- **Lead with the hardest misses.** End the audit by naming the 1-3 items most likely to be forgotten or most divergent from what was asked. Don't bury them.
- **Offer to close the high-value open items now** before handing off, when cheap (e.g., create the spun-off project record; run the quick check that was only estimated).

## Format

A table grouped by disposition tag (✅ / ⚠️ / 📋 / 🌱 / 🔍 / 🔁 / ❌), columns: "What was said" | "Disposition / where it lives". Then a one-paragraph "hardest misses" callout. Then an offer to action the cheap open items.

## Why this exists

The goal is to make sure ideas raised in passing are not completely forgotten. There are repeated instances, across many tools, where a user brings up an idea and the agent does not remember it at the end of the session. This audit is the structural fix.

Composes with: a multi-session roadmap table (strategic phases - run alongside this at close), `rules/session-handoffs-required.md` (the starter prompt is where 📋 Queued items live).
