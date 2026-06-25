# Scoped Frontend Vite FS Allow Security Code Review

## Verdict

PASS.

codeQualityStatus: CLEAR  
recommendation: APPROVE

## Scope Reviewed

- `frontend/src/components/analyze/StepCoverLetter.vue`
- `frontend/src/components/result/CompetencyGap.vue`
- `frontend/tests/e2e/analyze-flow.spec.js`
- `frontend/vite.config.js`

No external evidence path or notepad path was supplied. Review was based on the live scoped diff and local workspace inspection.

## Skill Perspective Check

- `omo:remove-ai-slops`: loaded and consulted before judging test relevance/maintainability. No HIGH/CRITICAL slop blocker found. The added E2E image checks include filename/order assertions that partially mirror the current asset mapping, but they also verify observable image loading and do not create a security blocker.
- `omo:programming`: loaded and consulted before judging test relevance/maintainability. No HIGH/CRITICAL issue under the programming perspective. No untyped production boundary expansion or unnecessary validation/parsing was introduced.

## Security Assessment

The security-relevant diff is `frontend/vite.config.js:7-10`, which adds:

```js
server: {
  fs: {
    allow: ['..'],
  },
},
```

This resolves to the repo root from the frontend package. It is needed by `frontend/src/components/result/CompetencyGap.vue:285-290`, which imports repo-local PNG assets from `docs/images/*.png` using `new URL(..., import.meta.url)`.

I do not consider this an unacceptable security risk for this local dev app because:

- It affects Vite's dev server only; production build behavior bundles the PNG assets and does not expose a Vite file server.
- Vite's resolved config keeps `server.fs.strict: true`.
- Vite 8.0.16 default `server.fs.deny` has higher priority than `allow` and blocks `.env`, `.env.*`, `*.{crt,pem}`, and `**/.git/**`.
- Local Vite API verification with normalized paths showed:
  - repo PNG under `docs/images/S.png`: allowed
  - root `.env`: denied
  - `.git/config`: denied
  - file outside repo root: denied
- The project launcher starts Vite with `--host 127.0.0.1` in `scripts/run-dev-servers.ps1:426-429`.
- Playwright starts Vite with `--host 127.0.0.1` in `frontend/playwright.config.js:12-14`.
- Plain `npm run dev` is still `vite` in `frontend/package.json:6-9`; Vite's installed default host is `localhost`, not a wildcard network bind.
- The launcher removes `GMS_KEY` and `LLM_INTERNAL_TOKEN` before starting the frontend process in `scripts/run-dev-servers.ps1:422-426`.
- Vite default CORS is limited to localhost/loopback origins, not arbitrary web origins.

## Findings

### CRITICAL

None.

### HIGH

None.

### MEDIUM

None.

### LOW

None blocking. A future hardening option would be narrowing `server.fs.allow` to only `../docs/images` if no other repo-root imports are expected, but the current repo-local, localhost-only setup is acceptable.

## Test Relevance

The added E2E checks in `frontend/tests/e2e/analyze-flow.spec.js:64-71` verify that four stat icons are rendered and image resources load. The loading-state test at `frontend/tests/e2e/analyze-flow.spec.js:174-197` verifies a user-visible pending state. These tests are relevant to the UI diff but are not treated as security proof for the Vite allow-list decision.

`git diff --check` was run on the scoped files; it reported only existing LF-to-CRLF warnings, no whitespace errors. Full build/E2E tests were not run because this was a read-only security review and those commands can create artifacts.

## Blockers

None.
