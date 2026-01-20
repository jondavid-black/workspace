# Agent Instructions

This project uses **bd** (beads) for issue tracking. Run `bd onboard` to get started.

## Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --status in_progress  # Claim work
bd close <id>         # Complete work
bd sync               # Sync with git
```

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds

## Standard Process
1. **Plan** - Write one or more features or bugs in bd defining the work. Decompose into tasks.  Always provide a description for each feature, bug, and task.
2. **Engineer** - Create and update the SysML v2 engineering baseline in the 'mbse' directory.  Ensure all Parts are defined and decomposes with appropriate Requirement, Port, and Connection definitions.
3. **Implement** Execute work. New code MUST have unit tests. New features should have BDD acceptance tests.
4. **Verify** - Write automated acceptance tests for Requirement.  Write automated unit tests to ensure correct implementtion of all features, tasks, and bugs where needed.  Ensure that every requirement is covered by an acceptanct test. Run the automated tests and correct any errors.
5. **Document** - Write user and design documentation as markdown files in the 'docs' directory.  Update existing documentaiton to capture changes.
6. Track: Update status in bd as you work. Commit and push when complete.
