# Agent log

| date | who | task | prompt | what the agent did | what broke | fix |
|------|-----|------|--------|--------------------|------------|-----|
| 2026-11-19 | Ana-Maria | A1 scaffold | Asked for a plan first, then scaffold 24 files | Proposed plan, created files after approval with 3 changes (gitignore, ANTHROPIC_API_KEY, screenshots folder) | - | - |
| 2026-11-19 | Ana-Maria | A1 commit | Commit and push | Staged 24 files | Commit failed: "Author identity unknown" | Set global git name and noreply email, committed and pushed |
