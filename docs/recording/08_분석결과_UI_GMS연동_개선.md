# 분석 결과 페이지 UI 및 GMS 연동 개선

## 배경

기존 분석 결과 페이지는 LLM이 내려준 `timeline_data`를 주차별 할 일 목록처럼 보여주는 구조였다.

```text
분석 생성
-> text_roadmap 저장
-> timeline_data 주차별 tasks 저장
-> 결과 페이지에서 주차별 체크리스트 표시
```

하지만 실제 면접 준비 서비스 관점에서는 단순 주차별 할 일보다 다음 정보가 더 중요하다.

- 채용공고와 사전 구축 직무 DB를 기준으로 어떤 큰 역량 영역이 중요한지
- 각 역량 영역 안에서 어떤 세부 개념을 준비해야 하는지
- 그 개념이 왜 해당 회사/직무/공고에서 중요한지
- 실제 면접에서 어떤 질문과 꼬리질문으로 이어질 수 있는지
- 사용자가 준비한 항목을 체크했을 때 진행률이 실제 준비 항목 기준으로 반영되는지

따라서 분석 결과 페이지는 `주차별 로드맵`보다 `면접 준비 항목` 중심으로 개편하는 것이 적절하다.

## 문제 상황

작업 확인 과정에서 다음 문제가 있었다.

- 분석 결과 페이지 UI 개편이 메인 프로젝트 경로가 아니라 `.worktrees/roadmap-result-revamp`에만 반영되어 있었다.
- 사용자가 실행하는 경로는 `C:\Users\SSAFY\Desktop\t08_project`였기 때문에 UI 변경이 보이지 않았다.
- 이전 worktree의 Vite 프로세스가 로컬 포트에 남아 있어 어떤 경로의 화면을 보고 있는지 혼동이 생길 수 있었다.
- `GMS_KEY`는 정상 로딩되었지만, 실제 `/llm/roadmap` 호출은 고정 `60`초 timeout 때문에 실패할 수 있었다.

## 변경 방향

분석 결과 흐름을 다음처럼 정리했다.

```text
채용공고 + 자기소개서 + 프로필 + 사전 구축 직무 DB
-> LLM 서버에서 GMS gpt-5-nano 호출
-> 큰 카테고리 / 작은 카테고리 기반 JSON 생성
-> Django Analysis에 결과 저장
-> Vue 결과 페이지에서 면접 준비 항목 카드로 표시
-> 사용자가 세부 개념을 체크
-> 진행률 저장 및 새로고침 후 복원
```

주요 변경 목표는 다음과 같다.

| 목표 | 설명 |
|---|---|
| 결과 구조 개선 | 주차별 tasks 대신 category/subtopics 기반 준비 항목 표시 |
| 면접 질문 강화 | 각 세부 개념마다 질문, 답변 방향, 근거, 학습 기준 표시 |
| 진행률 개선 | 실제 subtopic 체크 상태를 기준으로 진행률 계산 |
| 새로고침 복원 | `localStorage`에 체크 상태 저장 |
| GMS 안정화 | `response_format`과 timeout 설정을 명시 |
| 실제 연결 검증 | mock이 아닌 `GMS_KEY` 기반 HTTP 호출 확인 |

## LLM 응답 구조

LLM 서버는 기존 호환 필드인 `competency_gap`, `text_roadmap`, `timeline_data`를 유지하되, `timeline_data` 안의 구조를 면접 준비 항목 중심으로 확장했다.

예상 구조는 다음과 같다.

```json
{
  "competency_gap": {
    "strengths": ["프로젝트 경험"],
    "gaps": ["산업용 통신"],
    "required_competencies": ["로봇 제어", "모션 플래닝"]
  },
  "text_roadmap": "로보틱스와 통신 개념을 프로젝트 근거에 연결합니다.",
  "timeline_data": [
    {
      "category": "로보틱스",
      "summary": "프로젝트와 채용공고의 제어 요구가 겹치는 영역입니다.",
      "sources": ["채용공고", "프로젝트 1"],
      "subtopics": [
        {
          "title": "역기구학",
          "done": true,
          "why": "로봇 팔 제어 경험을 좌표계와 관절 제한까지 연결합니다.",
          "question": "1번 프로젝트에서 역기구학을 어떻게 사용했나요?",
          "answer_guide": "목표 위치 계산과 관절각 산출 흐름을 설명하세요.",
          "evidence": "자기소개서의 로봇 팔 제어 정확도 개선 경험",
          "study_goal": "FK/IK 차이와 특이점 대응을 설명할 수 있어야 합니다.",
          "follow_up_questions": ["관절 제한은 어느 단계에서 반영했나요?"]
        }
      ]
    }
  ]
}
```

## GMS 연동 변경

`llm_server/main.py`의 GMS 호출은 다음 기준으로 정리했다.

| 항목 | 변경 내용 |
|---|---|
| 모델 | `gpt-5-nano` 유지 |
| Gateway | SSAFY GMS chat completions endpoint 사용 |
| 인증 | `Authorization: Bearer {GMS_KEY}` |
| JSON 응답 | `response_format: {"type": "json_object"}` 추가 |
| timeout | `GMS_REQUEST_TIMEOUT_SECONDS` 환경변수 추가, 기본값 `120` |
| mock fallback | `GMS_KEY`가 없으면 개발용 mock 응답 반환 |

기존에는 timeout이 고정 `60`초였다.
실제 로드맵 프롬프트는 GMS 응답이 60초를 넘을 수 있어, 환경변수로 조정 가능하게 변경했다.

```python
GMS_REQUEST_TIMEOUT_SECONDS = float(os.getenv("GMS_REQUEST_TIMEOUT_SECONDS", "120"))
```

## 프론트 결과 페이지 변경

결과 페이지는 다음 구성으로 바뀌었다.

```text
분석 결과 헤더
-> 현재 진행률 카드
-> 역량 분석
-> 직무 역량 매칭도
-> 준비 항목
   -> 큰 카테고리 카드
   -> 세부 개념 카드
   -> 질문 / 답변 방향 / 근거 / 학습 기준 / 꼬리질문
```

새 컴포넌트는 다음 역할을 맡는다.

| 파일 | 역할 |
|---|---|
| `RoadmapTimeline.vue` | category 목록 렌더링 |
| `RoadmapCategoryCard.vue` | 큰 카테고리 카드 표시 |
| `RoadmapSubtopicCard.vue` | 세부 개념, 체크박스, 질문/답변 근거 표시 |
| `useRoadmapProgress.js` | 결과 정규화, 진행률 계산, localStorage 저장/복원 |

## 진행률 저장 방식

체크 상태는 분석 id 기준으로 저장된다.

```text
roadmap-progress:<analysis-id>
```

예시는 다음과 같다.

```json
{
  "0-0": true,
  "0-1": true,
  "1-0": true
}
```

저장된 값은 현재 로드맵에 존재하는 key만 다시 사용한다.
이렇게 하면 LLM 결과가 바뀌거나 세부 개념 수가 달라져도 오래된 key가 진행률에 잘못 반영되지 않는다.

## 분석 API와의 연결

백엔드 분석 결과 저장 구조는 크게 깨지 않았다.

| 결과 | 저장 위치 |
|---|---|
| 역량 gap | `Analysis.competency_gap` |
| 전체 설명 | `Analysis.text_roadmap` |
| 큰 카테고리/세부 개념 | `Analysis.timeline_data` |
| 질문/답변 방향/근거 | `timeline_data[].subtopics[]` |

따라서 기존 분석 상세 API는 그대로 사용할 수 있다.

```http
GET /api/analyze/<analysis_id>/
```

프론트는 응답의 `timeline_data`를 `roadmapItems`로 정규화해 렌더링한다.

## 검증 결과

백엔드 테스트 결과는 다음과 같다.

```text
python -m pytest -q
40 passed
```

LLM 서버 테스트 결과는 다음과 같다.

```text
python -m pytest tests/test_main.py -q
13 passed
```

프론트 빌드와 E2E 결과는 다음과 같다.

```text
npm run build
✓ built

npm run test:e2e
5 passed
```

브라우저 QA 결과는 다음과 같다.

```text
준비 항목 heading visible: true
역기구학 checked: true
모션 플래닝 checked: true
초기 진행률: 40%
EtherCAT 체크 후 진행률: 60%
새로고침 후 EtherCAT checked: true
desktop horizontal overflow: false
mobile horizontal overflow: false
```

실제 GMS HTTP smoke 결과는 다음과 같다.

```text
status_code: 200
is_mock: false
has_competency_gap: true
has_timeline_data: true
first_has_subtopics: true
has_question: true
has_authorization_leak: false
```

## 변경 파일

주요 변경 파일은 다음과 같다.

```text
frontend/src/views/AnalyzeResultView.vue
frontend/src/components/result/CompetencyGap.vue
frontend/src/components/result/RoadmapTimeline.vue
frontend/src/components/result/RoadmapCategoryCard.vue
frontend/src/components/result/RoadmapSubtopicCard.vue
frontend/src/composables/useRoadmapProgress.js
frontend/src/style.css
frontend/playwright.config.js
frontend/tests/e2e/analyze-flow.spec.js
backend/analysis/tests/test_analysis.py
llm_server/main.py
llm_server/roadmap_prompt.py
llm_server/roadmap_mock.py
llm_server/tests/test_main.py
scripts/run-dev-servers.ps1
docs/design-mockups/04-로드맵 분석결과 수정.html
```

## Git 반영

관련 작업은 `main`에 반영하고 GitLab `origin/main`에 push했다.

```text
96df2b3 feat: revamp roadmap result and GMS integration
da1107d chore: add remaining project updates
```

최종 원격 확인 결과는 다음과 같다.

```text
HEAD == origin/main
rev-list HEAD...origin/main: 0 0
```

## 기대 동작

최종적으로 사용자는 다음 흐름을 수행할 수 있다.

1. 채용공고와 자기소개서를 입력한다.
2. 분석을 생성한다.
3. GMS 기반 LLM이 회사/직무/공고/프로필/자소서를 조합해 준비 항목을 만든다.
4. 결과 페이지에서 큰 카테고리와 세부 개념을 확인한다.
5. 각 세부 개념별 예상 질문, 답변 방향, 근거, 학습 기준을 확인한다.
6. 준비한 개념을 체크하면 진행률이 반영된다.
7. 새로고침 후에도 체크 상태와 진행률이 유지된다.

## 향후 개선

- `timeline_data` JSON 일부를 별도 추천 개념/질문 테이블로 정규화
- GMS 응답을 더 엄격한 JSON schema로 검증
- 분석 결과의 체크 상태를 로컬 저장소가 아니라 서버에 저장
- 실제 full-stack `Vue -> Django -> LLM -> DB 저장 -> 결과 페이지` smoke 자동화
- 카테고리별 중요도나 예상 면접 빈도 점수 추가
