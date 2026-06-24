# T12. Privacy, deletion, and no-leakage guards

## 구현

- 사용자 입력 공고와 자기소개서는 분석 단위 private evidence로만 저장한다.
- public KG 테이블(`company_knowledge_claims`, `company_knowledge_facts`)에 submitted cover letter/private posting marker가 기록되지 않는 테스트를 추가했다.
- 사용자 삭제 시 `Analysis`, `CoverLetter` private records가 함께 제거되는 테스트를 추가했다.
- `ProfileSerializer`와 `Profile` 모델에서 `cover_letters`를 제거하고 `accounts.0002_remove_profile_cover_letters` migration을 추가해 프로필 API/DB로 일반 자소서를 저장/노출하지 않도록 했다.

## 검증

- RED: `.omo/evidence/graphrag-company-kg/wave4-backend-red-pytest.txt`
  - `test_profile_api_excludes_cover_letters` 실패
  - `test_manual_job_posting_accepts_supported_company_with_no_jobs` 실패
- GREEN: `.omo/evidence/graphrag-company-kg/wave4-backend-green-pytest.txt`
  - 4 passed
- 회귀: `.omo/evidence/graphrag-company-kg/wave4-backend-regression-pytest.txt`
  - 70 passed
- Review blocker fix: `.omo/evidence/graphrag-company-kg/review-fix-profile-cover-letter-pytest.txt`
  - 3 passed
- Final regression: `.omo/evidence/graphrag-company-kg/final-backend-pytest.txt`
  - 70 passed

## 판정

완료. private evidence는 public KG fact/chunk로 승격되지 않으며, 프로필 DB/API에서 자소서가 빠졌다.
