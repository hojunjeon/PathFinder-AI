# Gate Review: run-dev-servers frontend secret inheritance

## recommendation
APPROVE

## blockers
None.

## originalIntent
Perform a read-only gate review of the current workspace at `C:/Users/SSAFY/Desktop/t08_project-roadmap-result-revamp`, focused on `scripts/run-dev-servers.ps1` and whether `GMS_KEY` or `LLM_INTERNAL_TOKEN` can leak into the Vue/Vite frontend process.

## desiredOutcome
The launcher may use `GMS_KEY` and `LLM_INTERNAL_TOKEN` for Django/FastAPI coordination, but the Vue/Vite frontend child process must be started only after those environment variables are removed from the parent PowerShell environment. Health checks should use the local runtime token variable, not a frontend-inheritable environment variable.

## userOutcomeReview
PASS. The current script keeps the runtime token and GMS key in PowerShell variables, scopes environment-variable exposure around the backend and LLM server starts, and removes both `GMS_KEY` and `LLM_INTERNAL_TOKEN` before launching the Vue/Vite frontend process.

Because `Start-Process` inherits the parent process environment at launch time, the relevant question is the parent environment state immediately before each `Start-Process`. The current file shows `GMS_KEY` removed before migrations/backend/frontend, `GMS_KEY` set only immediately before the FastAPI LLM server start, and both secrets removed immediately before the frontend start.

## checkedArtifactPaths
- `C:/Users/SSAFY/Desktop/t08_project-roadmap-result-revamp/scripts/run-dev-servers.ps1`
- `C:/Users/SSAFY/Desktop/t08_project-roadmap-result-revamp/.omo/evidence/roadmap-analysis-revamp-code-review.md`
- `C:/Users/SSAFY/Desktop/t08_project-roadmap-result-revamp/.omo/evidence/re-review-previous-blockers-current-code-review.md`
- `C:/Users/SSAFY/Desktop/t08_project-roadmap-result-revamp/.omo/evidence/roadmap-analysis-revamp-security-gate-review.md`

## lineEvidence
- `scripts/run-dev-servers.ps1:292-295`: saves prior environment values in `$oldToken`/`$oldGmsKey`, creates local `$runtimeToken`, and stores the LLM-only key in local `$gmsKeyForLlm`.
- `scripts/run-dev-servers.ps1:301-303`: before Django migrations, removes `Env:\GMS_KEY` and sets only `LLM_INTERNAL_TOKEN` to `$runtimeToken`.
- `scripts/run-dev-servers.ps1:310-313`: after migrations, removes `Env:\LLM_INTERNAL_TOKEN`.
- `scripts/run-dev-servers.ps1:317-326`: before starting Django backend, removes `Env:\GMS_KEY`, sets `Env:\LLM_INTERNAL_TOKEN` to `$runtimeToken`, then starts backend.
- `scripts/run-dev-servers.ps1:328-340`: removes backend token exposure, sets `Env:\GMS_KEY` from `$gmsKeyForLlm` only for the FastAPI LLM server, sets `Env:\LLM_INTERNAL_TOKEN`, then starts the LLM process.
- `scripts/run-dev-servers.ps1:342-351`: removes both `Env:\GMS_KEY` and `Env:\LLM_INTERNAL_TOKEN` before starting Vue/Vite frontend with Node.
- `scripts/run-dev-servers.ps1:353-355`: `Wait-Http` calls the LLM health check with header `X-Internal-Token = $runtimeToken`, not `$env:LLM_INTERNAL_TOKEN`.
- `scripts/run-dev-servers.ps1:380-389`: original caller environment values are restored only during shutdown after server processes are stopped.

## slopAndOverfitPass
- `remove-ai-slops` was loaded and applied as a read-only focused pass over the env-leak diff. No deletion-only tests, tautological tests, implementation-mirroring tests, or unnecessary production extraction were found in this focused scope.
- `programming` was loaded and consulted as a maintainability/test-quality lens. No TypeScript/Python/Go/Rust code was changed by this focused launcher check.
- Existing code-review coverage was inspected. `.omo/evidence/roadmap-analysis-revamp-code-review.md:10-13` explicitly records `remove-ai-slops` and `programming` coverage. `.omo/evidence/re-review-previous-blockers-current-code-review.md:14-16` records the later current-workspace re-review for the previous code-quality blockers.
- `.omo/evidence/roadmap-analysis-revamp-security-gate-review.md` is stale for this specific launcher issue: it describes an older file state where the frontend was started before env cleanup. Current `scripts/run-dev-servers.ps1:342-351` shows that blocker has been addressed.

## exactEvidenceGaps
- No live launcher child-process environment capture was run. This gate is based on direct source inspection and PowerShell `Start-Process` environment inheritance semantics.
- No source files were edited for this review.
