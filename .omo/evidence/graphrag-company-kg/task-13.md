# T13. Frontend flow and result compatibility

## 구현

- `AnalyzeCreateView.vue`가 더 이상 `job_id`나 프로필 `cover_letters` 저장에 의존하지 않도록 변경했다.
- 분석 요청 payload를 `company_id`, `job_posting_id`, `submitted_cover_letter`, `selected_interview_types` 중심으로 변경했다.
- 저장된 공고가 없는 direct 분석 생성 대비용으로 `job_posting` 객체도 함께 유지하지만, 일반 UI 흐름에서는 `job_posting_id`가 authoritative row를 가리킨다.
- `StepJobUrl.vue`는 기준 `Job` 매칭이 없어도 선택 기업과 입력 공고를 다음 단계로 넘긴다.
- `StepCoverLetter.vue`는 더 이상 `cover_letters` 이벤트 payload를 내보내지 않고 분석 요청용 text만 전달한다.
- `ProfileView.vue`에서 자기소개서 섹션을 제거했다.
- E2E에서 프로필 저장 요청 없이 자기소개서가 분석 요청에 포함되는지 검증했다.

## 검증

- RED: `.omo/evidence/graphrag-company-kg/wave4-frontend-red-test.txt`
  - `ProfileView must not edit cover letters` 실패
- GREEN: `.omo/evidence/graphrag-company-kg/wave4-frontend-green-test.txt`
  - frontend design verification passed
- Build: `.omo/evidence/graphrag-company-kg/wave4-frontend-build.txt`
  - vite build passed
- E2E: `.omo/evidence/graphrag-company-kg/wave4-frontend-e2e.txt`
  - 6 passed
- Review fix E2E: `.omo/evidence/graphrag-company-kg/review-fix-frontend-e2e.txt`
  - 6 passed
- Final E2E: `.omo/evidence/graphrag-company-kg/final-frontend-e2e.txt`
  - 10 passed

## 판정

완료. 분석 결과 화면 계약은 유지했고, 생성 흐름만 새 company/posting/private evidence 계약으로 전환했다.
