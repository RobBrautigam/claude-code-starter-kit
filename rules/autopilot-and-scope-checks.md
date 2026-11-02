# Autopilot Mode and Scope-Change Checks

This rule defines the shared vocabulary around autonomous execution ("autopilot") and establishes the non-negotiable anomaly checks that apply even when autopilot is authorized.

## Glossary

**Autopilot (or "full autopilot", "auto-pilot mode", "run it to the end").**
A permission level where the user authorizes Claude to execute a defined scope of work without pausing for per-step confirmation. Autopilot applies to tactical decisions *inside* the already-agreed scope (which file to edit first, which helper to extract, which test to write next, whether to retry a flaky network call). Autopilot does NOT apply to scope changes, destructive actions, or emergencies - those always require a brief confirmation even under autopilot.

**Scope.**
The specific plan, project, spec, task list, or roadmap agreed to at the start of the session. Scope is established by the project record in your tracker, the plan file, the spec file, the brainstorming conclusion, or any explicit "let's work on X" instruction. Scope is not the same as "whatever the user mentioned most recently" - scope is the agreed assignment.

**Scope change.**
Any instruction that would cause Claude to work on something *outside* the established scope. Examples: switching from project A to project B, pivoting from one plan to another, changing the definition of "done", adding a significant new subsystem, removing a pre-agreed deliverable. Scope changes are NOT emergencies by themselves - they are user decisions - but they require confirmation even under autopilot.

**Emergency.**
A situation where continuing autopilot execution would cause an unacceptable negative outcome. The operating definition: **anything that, if you continue without pausing, is likely to produce a result the user will want reverted**. Emergencies always warrant a pause for a brief check-in, even when autopilot is explicitly authorized. They include but are not limited to:

- **Scope anomaly** - The next instruction or observed state implies a different project than the one agreed. 180° assignment changes are the canonical example.
- **Destructive action with ambiguous intent** - About to delete, force-push, reset, drop a table, cancel a record, overwrite a published artifact, and the instruction is ambiguous about whether the user actually wanted that.
- **Data integrity risk** - About to run a script that could corrupt data if a hidden assumption is wrong (wrong database, wrong destination, etc.).
- **Credential or access mismatch** - Noticed that the current session's credentials point at a different account than the work implies.
- **Precondition violation** - A task is about to run but its stated preconditions aren't met (dependency not shipped, schema column missing, feature flag off, tests red).
- **External service boundary** - About to send a message, post to a channel, trigger a webhook, publish content, or otherwise affect a system outside the local machine, and there's any ambiguity about whether the user explicitly authorized that specific action.
- **Conflict with prior authorization** - The current instruction contradicts something the user said earlier in the same session without acknowledgement of the change.

Emergencies override autopilot. The phrase "unless there's an emergency" in an autopilot instruction is not decorative - it is a specific carve-out that Claude must actively use.

**Confirmation (under autopilot).**
A single short message flagging the anomaly and asking for one yes/no answer. The format: state what you observed, state why it looks like an emergency, state what you were about to do, ask if you should proceed. Then wait for a yes/no. If yes, proceed. If no, reassess.

## Operating rules for autopilot mode

When the user authorizes autopilot:

1. **State the scope out loud before starting execution.** The first message after autopilot authorization MUST restate, in one sentence, exactly what plan / project is about to execute and where it lives (file path or project ID). This gives the user a last-chance correction window before any files are touched.

2. **Treat scope anomalies as emergencies.** If at any point during execution the next instruction or observed state is inconsistent with the established scope, STOP and send a one-sentence confirmation. "No further questions" does NOT suppress emergency confirmations - it only suppresses tactical clarifications *within* the agreed scope.

3. **Ambiguity in a sentence that could change scope always resolves toward pausing.** English pronoun resolution is genuinely ambiguous in messages that mix topics with file paths or short references. When there's even a 20% chance that a sentence could mean "work on something different", the cost of a one-sentence confirmation is always lower than the cost of working on the wrong thing for an hour.

4. **Destructive and externally-visible actions always get a confirmation.** Even under autopilot. Even if the action was implied by the plan.

5. **Log the emergency-check outcome.** When Claude does raise an emergency confirmation and the user resolves it (either direction), briefly note the resolution in the next message so the reasoning is preserved in conversation history.

## Canonical patterns and their correct response

| Observed pattern | Emergency? | Correct response |
|---|---|---|
| User says "full autopilot" then gives tactical instructions within the agreed plan | No | Proceed without pausing |
| User mentions a file path for a completely different project mid-autopilot-authorization | **YES** (scope anomaly) | Pause, one-sentence confirmation, wait |
| User says "ignore that, do X instead" where X is obviously within the existing plan | No | Proceed with the reordered work |
| User's new instruction contradicts something he said 30 messages ago | **YES** (conflict with prior authorization) | Pause, flag the contradiction, ask which stands |
| Claude is about to run a script that writes to production | **YES** (data integrity risk) if there's any ambiguity about whether the production write was authorized | Confirm the write target explicitly |
| A dependency task failed and autopilot was going to continue past it | **YES** (precondition violation) | Stop, surface the failure, ask how to proceed |
| A subagent returned a result that implies a different scope | **YES** (scope anomaly) | Re-verify scope before adopting the subagent's path |
| User gave a specific file path as context, surrounded by an instruction about a different topic | **YES** (scope anomaly due to ambiguous reference) | Pause before pivoting to that file |

## Session-start behavior for plan execution

When entering execution mode on a plan:

1. Read the plan file fully before starting.
2. Send a restatement message:
   > "Starting execution of [plan title]. Plan file: [path]. Scope: [one-sentence summary of what will be built]. First task: [task 1 title]. I'll proceed unless you stop me in the next few seconds."
3. Wait briefly for any interjection (not a blocking wait - the user might be AFK, so proceed after one message round-trip).
4. Dispatch the first task.
5. After each task completes, include the next task's title in the status update so the user can course-correct between tasks without halting.

This gives the user multiple correction windows without slowing execution meaningfully.
