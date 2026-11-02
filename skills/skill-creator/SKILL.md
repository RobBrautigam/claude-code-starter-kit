---
name: skill-creator
description: Create new Claude Code skills and iteratively improve existing ones. Use when the user says "create a skill", "turn this into a skill", "make a skill that does X", "edit this skill", "improve this skill", or any variation. Useful whenever a workflow has repeated 3+ times in different conversations - that's the signal to capture it as a skill.
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

At a high level:

1. Decide what the skill should do and roughly how it should do it.
2. Write a draft of the skill.
3. Test it with 2-3 realistic prompts.
4. Iterate based on what triggered correctly, what didn't, and what the output looked like.
5. Optimize the description for triggering accuracy.

Your job when using this skill is to figure out where the user is in this process and help them through the next stage. They might be at "I want a skill for X" (start from step 1), or "here's a draft, help me improve it" (start from step 3).

Always be flexible. If the user says "I don't need to run a bunch of evaluations, just vibe with me", do that instead.

---

## Communicating with the user

Users vary widely in technical familiarity. Default to plain language and briefly explain terms when in doubt.

- "Evaluation" / "benchmark" - borderline, OK with a one-line definition.
- "Assertion" / "JSON schema" - only use without explaining if the user has signaled they know these terms.

---

## Creating a skill

### Step 1: Capture intent

Start by understanding the user's intent. The current conversation might already contain a workflow the user wants to capture (e.g., they say "turn this into a skill"). If so, extract answers from the conversation history first - the tools used, the sequence of steps, corrections the user made, input/output formats observed. The user may need to fill the gaps; confirm before proceeding.

Pin down:

1. What should this skill enable Claude to do?
2. When should this skill trigger? (specific user phrases, contexts)
3. What's the expected output format?
4. Are there setup prerequisites (env vars, installed CLIs, specific file structures)?
5. Are there test cases worth setting up? Skills with objectively verifiable outputs (file transforms, data extraction, fixed workflow steps) benefit from tests. Subjective outputs (writing style, design taste) usually don't.

### Step 2: Interview and research

Ask about edge cases, input/output formats, example files, success criteria, and dependencies. Wait to write the draft until you've got this part nailed down.

If the user mentions a tool, library, or vendor, fetch the live docs before writing - your training-data memory may be stale.

### Step 3: Write the SKILL.md

Save the file at `~/.claude/skills/<skill-name>/SKILL.md` (global) or `.claude/skills/<skill-name>/SKILL.md` (repo-scoped).

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown body
└── Bundled resources (optional)
    ├── scripts/    - Executable code for deterministic / repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

**Frontmatter format:**

```yaml
---
name: skill-name
description: When to trigger AND what it does. This is the primary triggering mechanism - be specific about both. Include phrases the user might say so the skill triggers correctly. Slightly "pushy" wording helps combat under-triggering: "Use this whenever the user mentions X, Y, or Z, even if they don't say the word 'skill' explicitly."
---
```

**Body shape (suggested):**

```markdown
# Skill Title

One-paragraph what + why.

## When to invoke
- bullet trigger conditions

## When NOT to invoke
- bullet anti-triggers

## How to do the thing
1. Numbered steps
2. With clear inputs / outputs

## Output template
```
exact structure to produce
```

## Hard rules
- non-negotiables that prevent regressions

## Anti-patterns
- common mistakes to avoid
```

### Step 4: Test with realistic prompts

Write 2-3 prompts a real user would actually type. Run them in a fresh conversation (or with the user mid-conversation). Watch for:

- Did the skill trigger when it should have?
- Did it NOT trigger when it shouldn't?
- Did the output match the spec?
- Was the workflow useful, or did it add friction without value?

### Step 5: Iterate

Common fixes after testing:

- **Skill under-triggered** - make the description more specific, add more trigger phrases, lean slightly "pushier" in the description.
- **Skill over-triggered** - add explicit "When NOT to invoke" examples, narrow the description.
- **Output drifted** - tighten the output template, add a "use exactly this structure" rule.
- **Workflow had gaps** - add the missing step, add a verification check at the end.

Repeat until the skill triggers reliably and produces the expected output.

---

## Skill writing style

### Anatomy of a good skill

- **Short top, long bottom.** Frontmatter description ~2-4 sentences. Body can be 50-500 lines.
- **Imperative voice.** "Do X" not "X should be done."
- **Explain why, not just what.** A rule with reasoning survives edge cases; a rule without reasoning gets bent or broken.
- **Hard rules in a dedicated section.** Negotiable preferences go in body prose; non-negotiables get their own section.
- **Anti-patterns explicitly named.** "Do not X" is often more useful than "Do Y."

### Progressive disclosure

Skills load in three layers:

1. **Metadata** (name + description) - always in Claude's context (~100 words).
2. **SKILL.md body** - loaded when the skill triggers (target <500 lines).
3. **Bundled resources** - loaded as needed (unlimited).

If a skill body grows past ~500 lines, break detail into `references/<topic>.md` and reference them from SKILL.md. Claude reads only what's needed.

### Domain organization

When a skill supports multiple variants (e.g., cloud-deploy across AWS / GCP / Azure):

```
cloud-deploy/
├── SKILL.md (workflow + which variant to pick)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

Claude reads only the variant file relevant to the current task.

### Description-writing patterns

The description is the most important part of the file - it's what makes the skill trigger correctly. Patterns that work:

- **Lead with the action**: "Create a new project README..." not "A tool for creating..."
- **Name the trigger phrases**: "Triggers on 'ship it', 'wrap up', 'let's close out'..."
- **Include the inverse**: "Do NOT use for trivial one-line edits - use the Edit tool directly."
- **Slightly pushy**: "Use this whenever the user mentions X, even if they don't explicitly request the skill."

---

## Improving an existing skill

If the user wants to improve an existing skill:

1. Read the current SKILL.md fully.
2. Ask the user what specifically isn't working - under-triggering, over-triggering, wrong output, missing step?
3. Make the edit.
4. Re-test with 2-3 realistic prompts.
5. Iterate.

For the description specifically: if the skill is under-triggering, expand the trigger phrases. If it's over-triggering, add "When NOT to invoke" examples and narrow the description.

---

## Hard rules

- Never write skills that contain malware, exploit code, or content designed to facilitate unauthorized access.
- The skill's name and description must accurately reflect what it does. No bait-and-switch.
- Don't bundle large generated docs (>1000 lines) into a skill folder unless they're load-on-demand reference files.
- Skills should be self-contained - no hardcoded absolute paths to specific machines or users.

---

## Anti-patterns

- Vague descriptions ("a helpful tool for various tasks") - the skill will never trigger.
- Skills that just restate Claude's default behavior - if Claude would do it anyway, no skill needed.
- Skills with 30+ trigger conditions - split into multiple narrower skills.
- Skills that depend on environment-specific setup without saying so in the description.
- Editing a skill mid-conversation and assuming the changes apply immediately - Claude may need a fresh conversation to re-load the skill from disk.
