Created At: 2026-06-24T08:12:42Z
Completed At: 2026-06-24T08:12:42Z
File Path: `file:///C:/Users/SSAFY/Desktop/t08_project/DESIGN.md`
Total Lines: 104
Total Bytes: 6285
Showing lines 1 to 104
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Design
2: 
3: ## Source of truth
4: - Status: Active
5: - Last refreshed: 2026-06-24
6: - Primary product surfaces: 분석 생성, 역량 분석 결과, 면접 준비 항목
7: - Evidence reviewed: `frontend/src/views/AnalyzeResultView.vue`, `frontend/src/components/result/*`, `frontend/src/composables/useRoadmapProgress.js`, `llm_server/roadmap_prompt.py`, `docs/09_분석결과_페이지_가독성_개선.md`, `docs/13_면접_예상질문_AI_결과_설계.md`
8: 
9: ## Brand
10: - Personality: 신뢰할 수 있는 취업 준비 코치, 명확하고 실용적
11: - Trust signals: 입력 근거 표시, 상태의 의미 설명, 근거 없는 점수 사용 금지
12: - Avoid: 합격 가능성처럼 보이는 임의 퍼센트, 긴 AI 설명문, 경험을 과장하는 표현
13: 
14: ## Product goals
15: - Goals:
16:   - 지원자가 직무에 어필할 역량과 공부할 역량을 한눈에 구분한다.
17:   - 직무 지식과 사용자 경험을 연결해 예상 질문과 답변 전략을 제공한다.
18:   - 경험이 없을 때는 학습, 유사 경험만 있을 때는 연결, 직접 경험이 있을 때는 어필하도록 안내한다.
19: - Non-goals:
20:   - 객관적 근거 없는 직무 적합도 점수 제공
21:   - 사용자를 대신한 완성형 면접 답변 작성
22: - Success signals:
23:   - 사용자가 각 역량을 `어필`, `답변 정리`, `학습` 중 하나로 분류해 이해할 수 있다.
24:   - 준비 항목에서 왜 공부하는지와 어떤 경험을 연결할지 바로 확인할 수 있다.
25: 
26: ## Personas and jobs
27: 
<truncated 3118 bytes>
st/readability: 색상만으로 상태를 구분하지 않고 텍스트 배지를 함께 표시
73: - Screen-reader semantics: 상태 분포에 `aria-label`, 질문 체크박스에 질문 문장 사용
74: - Reduced motion and sensory considerations: 필수 애니메이션 없음
75: 
76: ## Responsive behavior
77: - Supported breakpoints/devices: 데스크톱, 태블릿, 모바일
78: - Layout adaptations: 상태 열과 세부 카드가 모바일에서 단일 열로 변경
79: - Touch/hover differences: 핵심 정보는 hover 없이 항상 표시
80: 
81: ## Interaction states
82: - Loading: 기존 분석 결과 로딩 표시 유지
83: - Empty: 확인된 역량 또는 준비 항목이 없다는 안내
84: - Error: 기존 API 오류 처리 유지
85: - Success: 질문 체크 상태와 진행률 표시
86: - Disabled: 해당 없음
87: - Offline/slow network: 기존 동작 유지
88: 
89: ## Content voice
90: - Tone: 짧고 단정적이며 행동 지향적
91: - Terminology: `어필 가능`, `답변 정리`, `학습 필요`, `판단 보류`
92: - Microcopy rules: 중복 설명을 피하고 `업무 연결`, `내 연결점`, `준비 순서`, `핵심 개념`, `예상 질문`처럼 스캔 가능한 제목을 사용한다.
93: 
94: ## Implementation constraints
95: - Framework/styling system: Vue 3 SFC, 기존 CSS 변수
96: - Design-token constraints: 신규 색상 하드코딩 최소화
97: - Performance constraints: 추가 API 호출 없이 기존 분석 응답에서 렌더링
98: - Compatibility constraints: 기존 문자열형 역량 분석과 기존 timeline 응답 지원
99: - Test/screenshot expectations: Vite build, 디자인 검증, Playwright 분석 흐름 통과
100: 
101: ## Open questions
102: - [ ] 실제 사용자 평가를 통해 상태 분류 명칭과 설명의 이해도를 검증한다.
103: - [ ] 질문별 답변 초안과 AI 피드백 기능을 후속 범위에서 결정한다.
104: 
The above content shows the entire, complete file contents of the requested file.


Created At: 2026-06-24T08:12:50Z
Completed At: 2026-06-24T08:12:50Z
File Path: `file:///C:/Users/SSAFY/Desktop/t08_project/.omo/artifacts/analyze-13-data.json`
Total Lines: 1369
Total Bytes: 67245
Showing lines 800 to 1369
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
800:                 "type": "concept",
801:                 "question": "시뮬레이터의 정확도 한계는 어떻게 평가하나?",
802:                 "done": false,
803:                 "answer_guide": "정확도 지표와 실측과의 비교",
804:                 "follow_up_questions": [
805:                   "현실 모델링 오차 보정 방법?"
806:                 ]
807:               },
808:               {
809:                 "type": "experience",
810:                 "question": "ROS2/Gazebo 기반 프로젝트에서 맡은 역할은?",
811:                 "done": false,
812:                 "answer_guide": "구현 내용과 결과",
813:                 "follow_up_questions": [
814:                   "어떤 이슈를 어떻게 해결했나?"
815:                 ]
816:               },
817:               {
818:                 "type": "application",
819:                 "question": "시뮬레이터를 현장 적용과 연결할 때 주의점은?",
820:                 "done": false,
821:                 "answer_guide": "이식성, 재현성, 데이터 일관성",
822:                 "follow_up_questions": [
823:                   "실제 사례를 들 수 있는가?"
824:                 ]
825:               }
826:             ],
827:             "question": "",
828:             "answer_guide": "",
829:             "evidence": "",
830:             "study_goal": "",
831:             "follow_up_questions": []
832:           }
833:         ]
834:       },
835:       {
836:         "category": "알
<truncated 27421 bytes>
s": "- 자료구조, 알고리즘, 운영체제, 네트워크, 데이터베이스 등 CS 기초 이해\n- 아두이노, 라즈베리파이 등 임베디드 기기에 대한 활용 능력\n- 새로운 기술을 빠르게 학습하고 적용하려는 태도\n- 팀원과 원활하게 소통하며 협업할 수 있는 커뮤니케이션 능력\n- 프로젝트를 끝까지 완성해 본 경험과 책임감",
1338:     "preferred_qualifications": "- 로봇 제어 SW 개발 및 실적용 경험자\n- EtherCAT, TCP/IP, 산업용 통신 및 실시간 제어 시스템 개발 경험 보유자\n- Rust 프로그램 가능자\n- Git 형상관리 및 협업 개발 경험 보유자\n- Linux / Ubuntu OS 사용 경험자\n- 2D/3D 영상처리 개발 및 실적용 경험자\n- 자격증 : 정보처리기사 / 로보틱스 및 임베디드 관련 자격증 보유자"
1339:   },
1340:   "user": {
1341:     "id": 1,
1342:     "email": "qwer1234@naver.com"
1343:   },
1344:   "summary": {
1345:     "company_name": "유일로보틱스",
1346:     "job_title": "로봇 제어 SW 개발자",
1347:     "interview_types": [
1348:       "technical"
1349:     ],
1350:     "timeline_categories": [
1351:       "모션 제어 설계",
1352:       "EtherCAT",
1353:       "임베디드 IO 연동",
1354:       "TCP/IP 표준 통신",
1355:       "실시간 제어/시뮬레이션 검증",
1356:       "상태 모니터링 및 이상 감지",
1357:       "이상 감지",
1358:       "안전 제어",
1359:       "로봇 제어기",
1360:       "시뮬레이터",
1361:       "알고리즘/모션 플래닝 시뮬레이션",
1362:       "로봇 시스템 통합",
1363:       "현장 튜닝/현장 적용",
1364:       "SDK/API 설계/개발"
1365:     ],
1366:     "timeline_category_count": 14,
1367:     "competency_count": 5
1368:   }
1369: }
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.


AGENT: Gemini 3.5 Flash High

### EVALUATION

* **Input Coverage**
  * **자소서/프로필 분석 연계**: [analyze-13-data.json](file:///C:/Users/SSAFY/Desktop/t08_project/.omo/artifacts/analyze-13-data.json) 분석 결과, 지원자의 4개 자소서 답변 내용(사과 수확 로봇 기구학 제어, 배드민턴 동동아리 협업 등)과 프로필 스택이 유일로보틱스 직무 요구사항인 14개 로드맵 카테고리에 누락 없이 고르게 배치되었습니다.
  * **인터뷰 유형 매핑**: 선택된 'technical'(기술면접) 유형에 따라 개념 질문, 실무 경험 질문, 심화 적용 질문의 3단계 질문 세트가 5개 역량 요소(필수 3, 우대 2)별로 적절히 분류되어 입출력의 정합성이 매우 높습니다.
  * **경험 매치 분석**: 직접 경험(`direct`), 유사 경험(`related`), 경험 부족(`none`) 상태 구분이 비교적 명확하며, 각 상태에 부합하는 대비 방향('어필 가능', '답변 정리', '학습 필요')으로 상태값이 바르게 추출되었습니다.

* **UI/UX**
  * **스크롤 장벽 유발**: 현재 [AnalyzeResultView.vue](file:///C:/Users/SSAFY/Desktop/t08_project/frontend/src/views/AnalyzeResultView.vue)는 14개 로드맵 카테고리 전체를 세부 정보(개념, 질문, 답변 가이드)까지 모두 펼쳐진 단일 타임라인으로 화면에 그립니다. 이로 인해 데스크톱과 모바일 양쪽에서 극심한 피로를 주는 스크롤 병목(Scroll Wall)을 초래합니다.
  * **낮은 가치 수준의 지표 시각화**: [capture-summary.json](file:///C:/Users/SSAFY/Desktop/t08_project/.omo/artifacts/analyze-result-page/capture-summary.json)에서 관찰되듯이, 근거 커버리지의 모든 항목이 100% 진행률의 가로 막대 14개로 중복 렌더링되고 있어 시각적 정보 밀도가 현저히 떨어지며 사용성 측면의 의미 있는 구분을 방해합니다.
  * **정보 계층 분리 모호**: 어필해야 할 내 강점 영역과 이론적 지식이 부족하여 
<truncated 111829 bytes>
ercent}%`;
      document.getElementById('global-progress-desc').textContent = `총 ${totalQuestions}개 질문 중 ${completedCount}개 완료`;

      // Update Circular Progress Bar
      const circle = document.querySelector('.progress-ring-circle');
      if (circle) {
        const radius = 28;
        const circumference = 2 * Math.PI * radius; // 175.9
        const offset = circumference - (percent / 100) * circumference;
        circle.style.strokeDasharray = circumference;
        circle.style.strokeDashoffset = offset;
      }
    }
  </script>
</body>
</html>
```

---

### IMPLEMENTATION NOTES

1. **분할 창(Split-Pane) 레이아웃 및 모바일 드릴다운 도입**: 기존 [AnalyzeResultView.vue](file:///C:/Users/SSAFY/Desktop/t08_project/frontend/src/views/AnalyzeResultView.vue)의 14개 카테고리 수직 적층 구조를 좌측 리스트(필터링 바 포함) 및 우측 상세 패널의 2열 구조로 전면 개편했습니다. 모바일 기기(980px 이하)에서는 전체 리스트 뷰에서 상세 카드 뷰로의 드릴다운(Drill-down) 전환(Back 버튼 탑재)을 적용하여 '스크롤 장벽'을 원천 해소했습니다.
2. **근거 출처 마트릭스(Source Verification Matrix) 위젯**: 의미 없는 14개의 100% 가로 채우기 막대들을 걷어내고, 14개 요구 도메인별로 `채용공고(Job)`, `내 경험(Profile)`, `직무 DB(Knowledge Graph)`가 어떻게 교차 추적 검증되었는지를 컬러 점 지표로 한눈에 매핑하는 마트릭스 대장 형태로 재디자인하여 커버리지의 신뢰성 가치를 극대화했습니다.
3. **상태 관리 동기화 및 LocalStorage 유지**: 각 문항별 준비 완료(체크박스 활성화) 상태를 브라우저 로컬 저장소에 바인딩하여 백엔드 오버헤드 없이 즉각적인 변경사항이 전역 상단 헤더의 진성 진행률 원형 게이지(conic-gradient/SVG)와 리스트 카드별 실시간 막대 진행률에 부드러운 트랜지션으로 동기 분배되도록 설계했습니다.

모든 요구사항에 따른 분석 및 인터랙티브 HTML 목업 작성이 성공적으로 완료되었습니다.

### 진행된 작업 요약

1. **상세 분석 및 평가 수행**: 
   * [analyze-13-data.json](file:///C:/Users/SSAFY/Desktop/t08_project/.omo/artifacts/analyze-13-data.json)의 14개 로드맵 데이터 및 5개 핵심 역량 구조 검토
   * [AnalyzeResultView.vue](file:///C:/Users/SSAFY/Desktop/t08_project/frontend/src/views/AnalyzeResultView.vue) 및 관련 하위 컴포넌트들의 스크롤 병목(Scroll Wall) 문제 및 낮은 정보 밀도의 근거 커버리지 바(14x 100%) 오작동 분석
   * [DESIGN.md](file:///C:/Users/SSAFY/Desktop/t08_project/DESIGN.md)의 브랜드 가이드라인 및 색상/컴포넌트 토큰 준수 여부 대조

2. **이상적 목업 작성**:
   * 스크롤 지옥을 해결하는 **좌우 분할 레이아웃(Split-Pane)** 적용 및 모바일 드릴다운 동작 구현 (CSS/JS 포함)
   * 100% 막대그래프를 대체하는 **교차 추적 근거 대장(Source Verification Matrix)** 구현
   * 로컬 저장소 연동 및 문항 체크 시 실시간 전역 원형 진행률 반영 로직 개발
   * [result_page_mockup.html](file:///C:/Users/SSAFY/.gemini/antigravity-cli/brain/87c4454c-1c6a-40ba-a318-fe80a06994b1/result_page_mockup.html) 파일로 작성 완료 및 상세 평가 내용 답변 제공