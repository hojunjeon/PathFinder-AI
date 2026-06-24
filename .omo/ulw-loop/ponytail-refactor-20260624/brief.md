Ponytail principles refactor for GT_PJT.
Deliverable: install/enable Ponytail plugin if CLI supports it, then complete a first-wave low-risk behavior-preserving refactor in this repository.
Constraints: preserve behavior; no new dependencies; do not revert user changes; avoid dirty files unless unavoidable; frontend/backend/llm_server should not be broadly rewritten at once; security/auth/data-loss/accessibility/test stability must not be weakened; use existing helpers and stdlib first.
Success criteria:
C1 install evidence: Ponytail marketplace/plugin setup command result is captured, or the exact blocker and next UI step is captured.
C2 planning evidence: repo survey classifies refactor candidates by impact/risk and selects only low-risk first-wave scope.
C3 behavior evidence: before/after characterization or existing tests prove behavior preserved for touched code.
C4 verification evidence: targeted tests for touched area pass; available broader commands are attempted or blockers captured exactly.
C5 final review evidence: diff is reviewed for Ponytail principles, no user changes reverted, cleanup receipts recorded.
