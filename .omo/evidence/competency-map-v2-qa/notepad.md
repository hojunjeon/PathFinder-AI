# competency-map-v2 QA notepad

Tier: LIGHT - read-only QA over existing UI/prompt implementation; no new module/security/schema/external integration changes performed in this turn.

Skills:
- browser:control-in-app-browser - required for browser-facing route validation.
- omo:visual-qa - required for responsive UI screenshot and overflow validation.
- ponytail - active by instruction; QA only, no implementation.

Success criteria:
1. /analyze/99 renders the new competency map/action planner and strategy toggle is visible.
2. /analyze/99 has no horizontal overflow at 1280, 768, and 375 px viewports.
3. Existing analyze flow still works using the existing E2E scenario or faithful browser/API evidence.
4. PASS items must have non-empty artifacts; blockers listed for any failure.

Scenarios planned:
- S1 browser route /analyze/99 at 1280x900: verify competency map/action planner and strategy toggle visible.
- S2 browser route /analyze/99 at 1280/768/375 widths: verify document horizontal overflow false.
- S3 existing analyze flow regression: validate prior E2E evidence and rerun light existing flow check if feasible.

Completed scenarios: S0 PASS, S1 PASS, S2 PASS, S3 PASS, AHTTP1 PASS, AFLOW1 PASS, ARESP1 PASS.
Limitation: live backend has no analyses.id=99, so browser render used supported mocked API route from existing E2E pattern.
Cleanup: ports 5173/8080/8081 released.
