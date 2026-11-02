# Graph / Index Tool Adoption by Evidence

Before adopting ANY structural or semantic indexing tool as standing infrastructure - a code
graph, a knowledge/file graph, a vector index, a RAG layer - **measure its token delta vs plain
grep+Read on the actual target corpus, and adopt only on evidence.** Never adopt on a vendor's
headline number ("71.5× token reduction") or on faith.

This rule generalizes `code-review-graph-usage.md` (when to use the code graph) to the whole class
of "should we stand up this index?" decisions.

## The two costs the decision must weigh (not one)

A naive "does a query through the tool use fewer tokens than grep" measurement is incomplete.
Standing adoption has TWO costs:

- **(A) Build + refresh.** What does it cost to build the index, and to keep it fresh as the
  corpus changes? If the tool routes content through an LLM to ingest (most knowledge/doc graphs
  do for prose/markdown/PDF), that's a **recurring paid-API cost** on every refresh of a changing
  corpus - a standing liability.
- **(B) Per-query token win.** Does a query through the tool actually beat grep+Read?

Adopt only if **(B) clearly outweighs (A)**. A tool that wins per-query but needs a recurring
paid build over a corpus grep searches for free is usually a net loss.

## Corpus heuristics (when grep already wins)

- **Small corpora** (< ~100 files): plain search is faster; structural navigation adds nothing.
- **Prose / markdown corpora**: grep + Read pinpoints the 1-2 relevant files cheaply, and you
  must read the file to answer anyway - a structural subgraph doesn't save that. The headline
  graph numbers come from large **code** repos where caller/callee/impact navigation matters.
- **Frequently-changing corpora**: refresh cost dominates; a graph stale within days is a paid
  rebuild treadmill.

Structural/semantic indexes earn their cost on **large, slow-changing CODE repos**. They rarely
earn it on small, well-named, fast-changing prose.

## The decision procedure (free measurement first, paid only if justified)

1. **Free baseline.** Pick 1-2 real queries representative of how the corpus is actually used.
   Answer each via plain grep+Read; record the actual tokens (grep output + bytes of each file
   read). This is the bar.
2. **Capability probe (free).** Install the tool; check whether it can build over your corpus
   **without** a paid LLM backend (some have a no-LLM/structural mode; some hard-require a key).
3. **Gate:** if a **free** build path exists → build, run the same queries through the tool,
   compute the real delta. If the build **requires recurring paid API** AND the baseline is cheap
   → **NO-GO without spending a dime** (the tool can't meaningfully beat an already-cheap query and
   adds a recurring cost). Only spend on a one-time bounded paid build if the free baseline shows
   the tool could plausibly win big.
4. **Commit a threshold up front** (e.g. "GO only if ≥40% per-query reduction AND a free/one-time
   build path") so the result isn't rationalized after the fact.
5. **Document the go/no-go with numbers**, not vibes. On NO-GO, uninstall and leave no footprint.

## Why this rule exists

A real pilot is cheaper than a standing mistake. Adopting an index tool that doesn't pay back
means a recurring build cost, a stale-answer hazard, and config sprawl - for a problem grep
already solved. Measure first; the measurement itself is usually a 15-minute, zero-cost grep pass.

Related: `code-review-graph-usage.md` (the code-graph instance - when the code graph earns its
cost).
