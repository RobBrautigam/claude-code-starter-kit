# Verify Before Done: Evidence Is the Exercised Surface

"It works", "done" and "fixed" are claims. A claim needs evidence, and the evidence is the thing a
real user would touch, exercised and captured: the rendered page, the real response, the row that
landed in the database, the message that arrived. Code that looks right is not evidence. Neither is
a green test nobody has ever seen fail.

## FORBIDDEN

- Claiming "works", "done" or "fixed" from code that looks right, a build that succeeded, a log
  line, or a thumbnail.
- Counting a NEW test as evidence before you have seen it fail. Break the code it guards on purpose
  (flip a condition, delete the line), run the test, watch it go red, put the code back byte for
  byte, watch it go green. A test that has never been red may be testing nothing.
- Presenting an assumption as a fact, or leaving placeholder text ("TBD", "~X users") in anything a
  person will forward or act on.
- Doing the easy 70% and handing the human the verification 30%.
- Calling a page "verified" because the URL answered 200. Many apps answer 200 with their shell for
  a path that does not exist, and a private route answers an unauthenticated request with the login
  page. Pull the real content back and find a sentence only the new version has.

## REQUIRED

- **Drive the real surface as a real user.** Click every control you changed and confirm the
  downstream effect: "Published" means nothing until the post exists at its destination.
- **Front-end changes:** check the states you touched (empty, loading, error, full) at phone and
  desktop widths, with the browser console and network panel clean. Look at the actual rendered
  theme, not the mockup.
- **Compute a claim about your own numbers before you write it.** "All totals reconcile", "every
  rounding favors the customer", "three of five tests" are exactly the sentences a sharp reader
  checks. Write the number next to the command that produced it.
- **Read the whole source before you answer about it.** A link, a document, a repository the user
  points at is read in full, not skimmed from a snippet. For a repository, count the files you read
  against its file tree and say what you skipped ("41 of 43 files read whole; 2 lockfiles skipped").
- **Say what was not covered.** "Verified on desktop Chrome; not checked on Safari" beats
  "everything verified".
- **Re-check what describes a thing when the thing changes.** If a message summarizes a document and
  the document changes, re-read the message line by line before sending it again.
- **A finished request is checked by someone who did not do the work.** When an agent says it
  finished something you asked for, a fresh reviewer (a new agent with no stake in the work) opens
  the real result and reads it against your original words, never against the agent's own summary,
  and answers met or short. A summary written by the worker reads its own work generously; a
  quantity you named ("all 200 pages") is counted, not assumed.
- **Fix the shared path once.** Before changing a function to fix a bug, find every caller; a bug in
  a shared helper is fixed in the helper, not patched at each call site.

## Rules are verified too

A rule is a claim that something will not happen again. A new line in `rules/` names, the same day,
the check that refuses its miss: a hook, a script, a lint or a test, listed in one register beside
the rules (the rule, the check, the file it lives in). When no check can be written yet, the change
that adds the rule says so and owes the check by name. A rules folder that grows every week with
no checks behind it is an application problem, and more prose makes it worse.

## Why this rule exists

The most expensive agent failure is not a crash, it is a confident "done" on work that is not done:
the user ships it, a customer finds it, and every later "done" is trusted less. Capturing the
evidence costs minutes; the false claim costs the trust that makes delegation work at all.

Related: `tdd-loop-discipline.md` (which tests to run while iterating), `use-gha-not-local-ci.md`
(where the full suite runs).
