# Roadmap Button Removal ULW Notepad

## Brief
Remove the separate "기업/직무 DB 연결" action from the roadmap create page. Users must select "지원 기업" through the search/dropdown flow, then proceed through the existing next-step action. The next-step action should perform the existing supported-company/job matching when needed.

## Tier
HEAVY. This is a user-facing frontend flow change on an already modified roadmap page, with e2e and browser-surface proof required by the user-invoked ulw-loop.

## Success Criteria
1. Happy path: no `#match-job-btn` exists; selecting a supported company from the dropdown and clicking `#next-step-btn` reaches the cover-letter step after matching.
2. Edge/regression: unsupported/free-typed company text cannot bypass dropdown selection and cannot proceed.
3. Visual surface: desktop and mobile screenshots of `/analyze/new` show the company search/dropdown path without the removed DB-connection button and without overlapping or clipped text.

## QA Channels
- Playwright e2e stdout for criteria 1 and 2.
- Browser screenshot artifacts for criterion 3.

## Exclusions
Do not stage unrelated `.gitignore` or `stop-dev.bat` changes unless the user explicitly asks.
