Ponytail refactor final notepad - 2026-06-24

Scope completed:
- Installed Ponytail plugin: ponytail@ponytail version 4.8.3.
- First-wave refactor executed only in llm_server processing code.
- Split llm_server/main.py responsibilities:
  - main.py: FastAPI routes, auth middleware, request/response models, GMS calls, parse boundary.
  - roadmap_processing_competency.py: competency gap normalization.
  - roadmap_processing_values.py: timeline value normalization.
  - roadmap_processing_timeline.py: timeline responsibility mapping, repair target selection, repair merge, quality checks.
- Added characterization test in tests/test_roadmap_processing_values.py.
- Added repair branch regression in tests/test_roadmap_repair_branch.py after code review caught missing _timeline_repair_targets import.

Fresh verification:
- cd llm_server; python -m pytest -q -> 29 passed in 0.75s.
- cd backend; .\venv\Scripts\python.exe -m pytest -q -> 84 passed in 46.60s.
- cd frontend; npx playwright test -> 16 passed in 10.8s.
- py_compile on changed llm_server Python files -> pass.
- git diff --check on changed llm_server files -> pass, CRLF warning only.

Size receipts:
- llm_server/main.py pure_loc=238.
- llm_server/roadmap_processing_values.py pure_loc=126.
- llm_server/roadmap_processing_timeline.py pure_loc=231.
- llm_server/roadmap_processing_competency.py pure_loc=181.
- llm_server/tests/test_roadmap_processing_values.py pure_loc=32.
- llm_server/tests/test_roadmap_repair_branch.py pure_loc=64.

Cleanup:
- Verification commands exited normally.
- No tmux session, browser context, container, bound port, or temp dir remains from this work.
