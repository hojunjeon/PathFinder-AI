# 로드맵 생성 기업 검색 및 기준 직무 미매칭 처리

## 배경

> 현재 구현에서는 기준 직무가 없을 때 더 이상 fallback `Job` row를 생성하지 않는다. 사용자가 입력한 채용공고는 `job_postings`에 저장하고, 분석은 `company_id + job_posting` 계약으로 진행한다. GraphRAG/KG 설계의 전체 기준은 `docs/10_GraphRAG_기업_KG_구현.md`를 따른다.

로드맵 생성 화면은 사용자가 채용공고를 직접 입력한 뒤, 지원 기업을 DB에 있는 회사와 연결하고 다음 단계에서 자기소개서와 분석 요청을 이어가는 흐름이다.

이번 작업 전에는 다음 두 가지 사용성 문제가 있었다.

1. 사용자가 별도의 `기업/직무 DB 연결` 버튼을 눌러야 다음 단계로 갈 수 있었다.
2. DB에 회사는 있지만 연결 가능한 기준 직무가 없으면 `선택한 회사에 연결할 수 있는 기준 직무가 없습니다.` 문구가 나오며 진행이 막혔다.

사용자 관점에서는 지원 기업이 DB에 존재하는지가 핵심 조건이고, 입력한 직무명이 기존 기준 직무명과 정확히 맞는지는 로드맵 생성의 필수 조건이 아니다. 따라서 회사 검색 선택을 기준으로 흐름을 단순화하고, 기준 직무가 없는 회사도 입력한 채용공고를 바탕으로 분석을 진행할 수 있어야 한다.

## 변경 방향

로드맵 생성 Step 1의 입력 흐름을 다음처럼 정리했다.

```text
지원 기업 검색어 입력
-> DB에 있는 회사 드롭다운 후보 선택
-> 채용공고/직무 정보 입력
-> 다음 버튼 클릭
-> 수동 채용공고 저장 API 호출
-> 회사가 지원 대상이면 다음 단계로 진행
```

`기업/직무 DB 연결` 버튼은 제거하고, 회사 선택 여부가 다음 단계 진입 조건이 되도록 했다.

직무 매칭은 다음 정책을 따른다.

| 상황 | 동작 |
|---|---|
| 회사가 DB에 없거나 roadmap 지원 대상이 아님 | 기존처럼 진행 불가 |
| 회사가 DB에 있고 기존 Job이 있음 | 직무명 키워드가 맞으면 참고용 `matched_job`을 반환할 수 있음 |
| 회사가 DB에 있지만 기존 Job이 없음 | fallback `Job`을 만들지 않고 `matched_job: null`, `jobs: []`로 응답하며 입력 공고 기반으로 진행 |

## 백엔드 변경

`POST /api/job-postings/manual/`에서 회사는 지원 대상이지만 연결 가능한 Job이 하나도 없는 경우를 더 이상 오류로 처리하지 않는다.

기존 흐름은 다음과 같았다.

```text
회사 매칭 성공
-> Job 매칭 결과 없음
-> 400 Bad Request
-> "선택한 회사에 연결할 수 있는 기준 직무가 없습니다."
```

현재 흐름은 다음과 같다.

```text
회사 매칭 성공
-> Job 매칭 결과 없음
-> JobPosting 저장
-> matched_job: null, jobs: []
-> 201 Created
```

이 방식은 직무명 일치를 강제하지 않으면서도 사용자가 입력한 공고를 분석의 1차 근거로 유지한다. 유사 직무명으로 기술스택이나 담당 업무를 임의 추론하지 않기 위해 fallback `Job` 생성은 제거했다.

## 프론트엔드 검증

E2E 테스트에 회사만 DB에 있고 기준 직무가 없는 시나리오를 추가했다.

검증 시나리오는 다음과 같다.

```text
1. 로드맵 생성 화면 진입
2. DB 회사 후보 선택
3. 기존 기준 직무에 없는 직무명 입력
4. 다음 버튼 클릭
5. 기준 직무 없음 문구가 화면에 없어야 함
6. 자기소개서 입력 단계가 보여야 함
```

기존의 임의 회사명 입력 방지 테스트는 유지했다. 따라서 DB에 없는 회사를 직접 입력해서 진행하는 경로는 여전히 막힌다.

## 개발 서버 및 fixture 보강

실제 로드맵 생성 화면에서 회사 검색 드롭다운을 바로 확인할 수 있도록 개발 실행 스크립트도 보강했다.

`scripts/run-dev-servers.ps1`은 Django migration 후 기본 DB에 회사 데이터가 없으면 `backend/companies/fixtures/companies.json` fixture를 적재한다. 새 SQLite DB를 처음 만드는 경우에도 회사 검색 후보가 비어 있지 않도록 하기 위한 처리다.

`.codegraph/`는 로컬 인덱스 산출물이므로 `.gitignore`에 추가했다.

## 검증 결과

이번 변경은 다음 명령과 브라우저 QA로 검증했다.

```text
cd backend
.\venv\Scripts\python.exe -m pytest companies/tests/test_companies.py
16 passed
```

```text
cd frontend
npx playwright test tests/e2e/analyze-flow.spec.js
4 passed
```

```text
cd frontend
npm run build
build passed
```

브라우저 QA에서는 데스크톱과 모바일 화면 모두에서 다음 조건을 확인했다.

```text
forbidden copy count: 0
cover letter step visible: true
```

ULW loop 기준으로는 8개 goal과 24개 success criteria가 모두 완료 처리됐다.

## 변경 파일

주요 변경 파일은 다음과 같다.

```text
backend/companies/views.py
backend/companies/tests/test_companies.py
frontend/tests/e2e/analyze-flow.spec.js
scripts/run-dev-servers.ps1
backend/companies/fixtures/companies.json
.gitignore
```

증적과 작업 기록은 `.omo/evidence/`, `.omo/plans/`, `.omo/ulw-loop/` 아래에 남겼다.

## 기대 동작

최종적으로 사용자는 다음 흐름으로 로드맵 생성을 진행할 수 있다.

1. `지원 기업` 검색어를 입력한다.
2. DB에서 검색된 회사 후보를 선택한다.
3. 직무명과 채용공고 내용을 입력한다.
4. 별도 연결 버튼 없이 `다음`을 누른다.
5. 선택한 회사가 DB에 있으면 기존 기준 직무명과 정확히 일치하지 않아도 자기소개서 단계로 이동한다.
6. DB에 없는 회사는 후보 선택이 되지 않으므로 기존처럼 진행할 수 없다.

## Git 반영 대상

이 문서는 과거 `feat/roadmap-page` 작업 기록을 현재 GraphRAG 설계에 맞게 정정한 것이다. 현재 GraphRAG 구현 작업 브랜치는 `codex/graphrag-plan`이다.
