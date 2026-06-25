# Scoped Review: Loading and SALT PNG Icons

## Verdict
PASS

## Scope
- `DESIGN.md`
- `frontend/src/components/analyze/StepCoverLetter.vue`
- `frontend/src/components/result/CompetencyGap.vue`
- `frontend/vite.config.js`
- `frontend/tests/e2e/loading-salt-icons.spec.js`

## Programming Check
- No `as any`, `@ts-ignore`, or `@ts-expect-error`.
- `StepCoverLetter.vue` current pure LOC: 241, below the 250-line ceiling after removing the extra dot animation.
- New test file `loading-salt-icons.spec.js` current pure LOC: 88.
- `CompetencyGap.vue` was already oversized; the change is intentionally minimal and localized to existing result icon render points. Extracting a one-use icon component would add indirection without reducing the existing component risk.

## Remove-AI-Slops Check
- No new dependency, parser, abstraction, factory, or speculative config.
- Loading UI uses existing state flow from `AnalyzeCreateView.vue` and existing design tokens.
- SALT icons map directly to the user-requested `docs/images/S.png`, `A.png`, `L.png`, and `T.png`.
- Vite dev-server file access is scoped to `.` and `../docs/images`, not the repo root.
- E2E checks assert browser-loaded images with `naturalWidth > 0`; they do not only check static strings.

## Evidence
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/frontend-e2e-loading-salt-analyze.txt`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/frontend-build.txt`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/frontend-design-test.txt`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/loading-desktop.png`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/loading-mobile.png`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/salt-icons-desktop.png`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/salt-icons-mobile.png`
