# Agent log

| date | who | task | prompt | what the agent did | what broke | fix |
|------|-----|------|--------|--------------------|------------|-----|
| 2026-11-19 | Ana-Maria | A1 scaffold | Asked for a plan first, then scaffold 24 files | Proposed plan, created files after approval with 3 changes (gitignore, ANTHROPIC_API_KEY, screenshots folder) | - | - |
| 2026-11-19 | Ana-Maria | A1 commit | Commit and push | Staged 24 files | Commit failed: "Author identity unknown" | Set global git name and noreply email, committed and pushed |
| 2026-11-19 | Ana-Maria | B1 API key test | Write scripts/test_api.py: load .env, send "Say hello in one sentence" to Haiku, print reply and token counts; run it | Wrote scripts/test_api.py (claude-haiku-5-5, low effort, error handling) and ran it: passed, 17 in / 14 out tokens | - | - |
| 2026-11-19 | Ana-Maria | B2 AGENTS.md review | Read AGENTS.md, list anything unclear or worth changing, no code yet | Reviewed v1 and listed 19 points: schema and table gaps, missing town, demo clock, contact field, status values, keyword net too broad, judge model. Then checked v2 and confirmed the points were resolved | v1 said "temperature 0 where supported", but Haiku 5.5 rejects non-default temperature with a 400, so every extractor call would have failed. Caught in review before any code was written | v2 removes temperature, keeps low effort, and relies on prompts and the schema check for consistency |
