분석 결과 페이지를 docs/mockups/competency_map_v2.html 및 docs/mockups/competency_map_v2_guide.md를 참고해 프로젝트에 맞는 UI/UX, 기능, 답변 품질로 개편한다.

Tier: HEAVY. 이유: 사용자 요청이 UI/UX와 기능, LLM 응답 품질까지 포함하고 기존 분석 결과 화면과 LLM 계약을 함께 바꿀 수 있는 다층 변경이다.

성공 기준:
C1 UI: /analyze/:id 결과 페이지가 기존 분석 응답으로 역량 지도, 상태별 준비 보드, 질문/답변 전략 토글을 렌더링한다. Scenario: Playwright로 실제 페이지를 열어 데스크톱 1280과 모바일 375 스크린샷을 캡처하고, "역량 지도", "어필 가능", "답변 전략" 텍스트 및 토글 패널 노출을 확인한다. Evidence: .omo/ulw-loop/evidence/competency-map-ui.txt plus screenshots.
C2 Contract: LLM/mock 응답이 역량 지도에 필요한 상태, 점수 근거, 질문 전략 데이터를 제공하거나 프론트가 기존 응답에서 안전하게 파생한다. Scenario: llm_server/backend/frontend targeted tests or a focused parser/normalizer check fails before and passes after. Evidence: .omo/ulw-loop/evidence/competency-map-contract.txt.
C3 Regression/quality: 기존 analyze flow와 빌드가 깨지지 않는다. Scenario: npm run build, frontend design check, and available targeted tests run. Evidence: .omo/ulw-loop/evidence/competency-map-regression.txt.
C4 Visual QA/review: 실제 브라우저 스크린샷에서 CJK 줄바꿈/오버플로/상태 인터랙션이 통과하고 post-implementation review가 unconditional approval을 준다. Evidence: .omo/ulw-loop/evidence/competency-map-review.txt.
