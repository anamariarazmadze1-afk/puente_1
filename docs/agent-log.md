# Agent log

| date | who | task | prompt | what the agent did | what broke | fix |
|------|-----|------|--------|--------------------|------------|-----|
| 2026-11-19 | Ana-Maria | A1 scaffold | Asked for a plan first, then scaffold 24 files | Proposed plan, created files after approval with 3 changes (gitignore, ANTHROPIC_API_KEY, screenshots folder) | - | - |
| 2026-11-19 | Ana-Maria | A1 commit | Commit and push | Staged 24 files | Commit failed: "Author identity unknown" | Set global git name and noreply email, committed and pushed |
| 2026-11-19 | Ana-Maria | B1 API key test | Write scripts/test_api.py: load .env, send "Say hello in one sentence" to Haiku, print reply and token counts; run it | Wrote scripts/test_api.py (claude-haiku-5-5, low effort, error handling) and ran it: passed, 17 in / 14 out tokens | - | - |
