# Public Repositories Carry Nothing Private

When you open-source something you built inside a private setup, the private setup leaks unless a
check stops it: client names in a test fixture, a company name in a session report, your machine's
home path in a config example, an internal hostname in a commit message. Once a name reaches a
public repository it is there for good: forks, clones and caches keep it after you delete it.

## Before the first write

Read the repository's visibility: `gh repo view --json visibility -q .visibility`. If it says
`PUBLIC`, everything below applies to every file, commit message, pull request title and body,
issue, release note and repository description.

## FORBIDDEN in a public repository

- Names of clients, partners, employers, companies you work for, and real people (other than a
  maintainer's public handle where you choose to show it).
- Private paths (your home folder, your machine name, mounted drives), internal hostnames, account
  ids, project ids, keys and tokens, real email addresses.
- Session records, briefings, handoff notes, internal task numbers and anything that describes
  private work. Keep those in a private repository and point at the public one from there.
- Test fixtures copied from real data. Use `example.com`, invented names and made-up numbers that
  echo nothing real.

## REQUIRED

- **A denylist kept OUTSIDE every repository**, one pattern per line: your companies, clients,
  machine names, private hostnames. Never copy it into a public repository, not even "for
  reference".
- **A check at the moment of publishing.** The kit's `hooks/git/public_repo_guard.py` is a git
  `pre-push` hook that reads every commit a push would publish (messages, added lines, added paths)
  and refuses the push when any of it matches the denylist. It treats a repository whose
  visibility cannot be read as public, and it fails closed.
- **Neutral commit messages and PR bodies.** Say what the change does, never who it was for.
- **Scrub before you port.** When you copy a pattern from private work, rewrite it as a general
  lesson; if a piece cannot be generalized, it stays home.
- **When a refusal fires, take the text out.** Amend or rebase the unpushed commits. Never
  `--no-verify`.

## If something already leaked

Deleting the file in a new commit does not remove it: the old commit still holds it. Removing it
means rewriting history (or recreating the repository), which breaks every clone and fork. Decide
that with the repository's owner; rotate any leaked key immediately either way.

## Why this rule exists

A rule in prose is read and then forgotten at the exact moment it matters; a check at the moment of
action is not. A denylist hook costs one minute to set up and is the difference between "public by
design" and "public by accident".
