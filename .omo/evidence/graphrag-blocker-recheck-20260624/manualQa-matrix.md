manualQa:
  surfaceEvidence:
    - scenarioId: GQB-001
      criterionRef: C1 no duplicate JobPosting for manual-posting->analyze via job_posting_id
      surface: Django HTTP API + DB verification
      exactInvocation: curl.exe -s -i POST /api/job-postings/manual/?page_size=10, then curl.exe -s -i POST /api/analyze/ with company_id and returned job_posting_id, then manage.py shell count query
      verdict: PASS
      artifactRefs: [A1, A2, A3, A4]
    - scenarioId: GQB-002
      criterionRef: C2 user deletion removes private candidate claim
      surface: Django HTTP API + DB verification
      exactInvocation: curl.exe -s -i POST /api/analyze/ with unique private job_posting marker, then manage.py shell checks private claim count before and after User.delete()
      verdict: PASS
      artifactRefs: [A5, A6, A7]
    - scenarioId: GQB-003
      criterionRef: C3 no profile cover_letters API/model
      surface: Django HTTP API + Django model introspection + pytest
      exactInvocation: curl.exe -s -i -X PUT /api/profile/ with cover_letters payload, manage.py shell Profile._meta field check, pytest accounts/tests/test_auth.py::test_profile_api_ignores_cover_letters_as_profile_data
      verdict: PASS
      artifactRefs: [A8, A4, A9]
    - scenarioId: GQB-004
      criterionRef: C4 job_id rejected
      surface: Django HTTP API + pytest
      exactInvocation: curl.exe -s -i POST /api/analyze/ with job_id only, pytest analysis/tests/test_analysis.py::test_analysis_create_rejects_legacy_job_id
      verdict: PASS
      artifactRefs: [A10, A9]
    - scenarioId: GQB-005
      criterionRef: C5 prompt injection fenced
      surface: LLM prompt builder pytest + assertion excerpt
      exactInvocation: python -m pytest tests/test_main.py::test_prompt_injection_in_posting_is_quoted_not_obeyed tests/test_main.py::test_cover_letter_injection_is_only_inside_private_evidence_block -vv
      verdict: PASS
      artifactRefs: [A11, A12]
    - scenarioId: GQB-006
      criterionRef: C1 frontend sends job_posting_id and not job_id
      surface: Playwright browser E2E mocked network assertion
      exactInvocation: npx playwright test "tests/e2e/analyze-flow.spec.js" --grep "analyze flow saves manual posting" --reporter=line
      verdict: PASS
      artifactRefs: [A13, A14]
  adversarialCases:
    - scenarioId: GQB-A01
      criterionRef: C1
      adversarialClass: duplicate creation after prior manual posting exists
      expectedBehavior: analyze reuses existing job_posting_id and leaves one JobPosting for the user/company
      verdict: PASS
      artifactRefs: [A2, A3, A4, A9]
    - scenarioId: GQB-A02
      criterionRef: C2
      adversarialClass: private user candidate claim survives account deletion
      expectedBehavior: user_private_candidate claim count drops from 1 to 0 after deleting the owning user
      verdict: PASS
      artifactRefs: [A6, A7, A9]
    - scenarioId: GQB-A03
      criterionRef: C3
      adversarialClass: client tries to write legacy cover_letters into profile
      expectedBehavior: API response omits cover_letters and Profile model has no cover_letters field
      verdict: PASS
      artifactRefs: [A8, A4, A9]
    - scenarioId: GQB-A04
      criterionRef: C4
      adversarialClass: legacy job_id payload attempts old analyze contract
      expectedBehavior: /api/analyze/ returns 400 and requires company_id plus job_posting instead
      verdict: PASS
      artifactRefs: [A10, A9]
    - scenarioId: GQB-A05
      criterionRef: C5
      adversarialClass: prompt injection in posting or cover letter attempts to override instructions
      expectedBehavior: injected text appears only inside private-evidence fenced block and JSON output instruction remains present
      verdict: PASS
      artifactRefs: [A11, A12]
  artifactRefs:
    - id: A1
      kind: text
      description: live API setup for duplicate reuse scenario
      path: .omo/evidence/graphrag-blocker-recheck-20260624/live-api-rerun-setup.txt
    - id: A2
      kind: curl
      description: manual posting live HTTP 201 response with returned job_posting.id
      path: .omo/evidence/graphrag-blocker-recheck-20260624/curl-rerun-manual-posting-response.txt
    - id: A3
      kind: curl
      description: analyze live HTTP 201 response using job_posting_id
      path: .omo/evidence/graphrag-blocker-recheck-20260624/curl-rerun-analyze-via-job-posting-id-response.txt
    - id: A4
      kind: text
      description: DB verification showing one JobPosting, no Profile.cover_letters field, and analysis linked to same posting id
      path: .omo/evidence/graphrag-blocker-recheck-20260624/live-api-rerun-db-verification.txt
    - id: A5
      kind: text
      description: live API setup for deletion cascade scenario
      path: .omo/evidence/graphrag-blocker-recheck-20260624/live-delete-cascade-setup.txt
    - id: A6
      kind: curl
      description: analyze live HTTP 201 response creating private candidate claim marker
      path: .omo/evidence/graphrag-blocker-recheck-20260624/curl-delete-private-claim-analyze-response.txt
    - id: A7
      kind: text
      description: DB verification showing private claim count 1 before user delete and 0 after
      path: .omo/evidence/graphrag-blocker-recheck-20260624/live-delete-cascade-db-verification.txt
    - id: A8
      kind: curl
      description: profile PUT live HTTP 200 response omitting cover_letters despite cover_letters request
      path: .omo/evidence/graphrag-blocker-recheck-20260624/curl-rerun-profile-cover-letters-response.txt
    - id: A9
      kind: pytest
      description: targeted backend blocker pytest run, 4 passed
      path: .omo/evidence/graphrag-blocker-recheck-20260624/backend-targeted-blockers-pytest.txt
    - id: A10
      kind: curl
      description: legacy job_id live HTTP 400 response
      path: .omo/evidence/graphrag-blocker-recheck-20260624/curl-rerun-job-id-rejected-response.txt
    - id: A11
      kind: pytest
      description: targeted LLM prompt injection pytest run, 2 passed
      path: .omo/evidence/graphrag-blocker-recheck-20260624/llm-prompt-injection-pytest.txt
    - id: A12
      kind: text
      description: LLM prompt injection assertion excerpt showing private-evidence fence checks
      path: .omo/evidence/graphrag-blocker-recheck-20260624/llm-injection-test-excerpt.txt
    - id: A13
      kind: playwright
      description: targeted frontend E2E run, 1 passed
      path: .omo/evidence/graphrag-blocker-recheck-20260624/frontend-manual-posting-e2e-rerun.txt
    - id: A14
      kind: text
      description: frontend assertion excerpt showing job_id absent and job_posting_id sent
      path: .omo/evidence/graphrag-blocker-recheck-20260624/frontend-manual-posting-test-excerpt.txt
