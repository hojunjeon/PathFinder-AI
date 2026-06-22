# Work Log

Date: 2026-06-05
Project: new_pjt / PathFinder AI
Status: completed

## Summary

- Fixed two separate requests:
  - Global Codex/CCTS repeated log suppression under `C:\Users\user\.codex`.
  - Project-local one-click dev server launcher for PathFinder AI.
- Used specialist review passes for global skill loader diagnosis, PowerShell launcher design, and QA acceptance checks.

## Files Changed

- `run-dev.bat`
- `scripts/run-dev-servers.ps1`
- `backend/config/urls.py`
- `frontend/public/health`
- `C:\Users\user\.codex\skills\codex-token-saver\SKILL.md`
- `C:\Users\user\.codex\hooks.json`

## Files Removed

- `fix-codex-token-saver-skill.bat`
- `scripts/repair-codex-token-saver-skill.ps1`

## Global Codex Log Fix

- Diagnosed `C:\Users\user\.codex\skills\codex-token-saver\SKILL.md` as beginning with UTF-8 BOM bytes before YAML frontmatter.
- Rewrote that file as UTF-8 without BOM so the first bytes are `2D 2D 2D`.
- Removed only the CCTS hook `statusMessage` from `C:\Users\user\.codex\hooks.json`.
- Left the CCTS PostToolUse command and trusted state entry in place.
- Backups created:
  - `C:\Users\user\.codex\skills\codex-token-saver\SKILL.md.bak-20260605161328`
  - `C:\Users\user\.codex\hooks.json.bak-20260605161702`

## Dev Launcher

- Added `run-dev.bat` as the project-local one-click launcher.
- Added `scripts/run-dev-servers.ps1` to:
  - run Django migrations,
  - generate `LLM_INTERNAL_TOKEN` if missing,
  - start backend on `127.0.0.1:8080`,
  - start LLM sidecar on `127.0.0.1:8081`,
  - start Vite frontend on `127.0.0.1:5173`,
  - write logs under `logs/dev-servers`,
  - stop launched process trees during cleanup.
- Added Django health endpoint `/api/health/`.
- Added frontend static health response at `/health`.

## Commands Run

- `rg -n "fix-codex-token-saver-skill|repair-codex-token-saver-skill" .`
- `backend\venv\Scripts\python.exe manage.py check`
- `backend\venv\Scripts\python.exe -m pytest -q`
- `llm_server\venv\Scripts\python.exe -m pytest -q`
- `frontend: npm test`
- `frontend: npm run build`
- Launcher smoke via hidden `cmd /c run-dev.bat` with explicit `LLM_INTERNAL_TOKEN`.

## Verification Evidence

- Global skill file:
  - `SkillStartsWithFrontmatter=True`
  - `SkillHasBom=False`
- Global hooks:
  - `hooks.json` parses as JSON.
  - `HookHasStatusMessage=False`
- Backend:
  - `manage.py check` passed.
  - `pytest -q` passed with `28 passed`.
- LLM sidecar:
  - `pytest -q` passed with `9 passed` and one third-party `TestClient` deprecation warning.
- Frontend:
  - `npm test` passed.
  - `npm run build` passed.
- Launcher smoke:
  - `http://127.0.0.1:8080/api/health/` returned 200.
  - `http://127.0.0.1:8081/health` returned 200 with `X-Internal-Token`.
  - `http://127.0.0.1:5173/health` returned 200.
  - Ports 8080, 8081, and 5173 were released after process-tree stop.

## Sensitive Information

- No real secrets were printed or written.
- Launcher smoke used a disposable local `LLM_INTERNAL_TOKEN` value only for verification.

## Notes

- `GMS_KEY` is still optional for server startup. If absent, the app starts, but roadmap generation reports service unavailable until `GMS_KEY` is set.
- Automated verification used process-tree termination for cleanup. The launcher script also implements cleanup in `finally` for normal console interruption such as Ctrl+C.
