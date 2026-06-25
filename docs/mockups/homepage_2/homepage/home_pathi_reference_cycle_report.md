# PathFinder AI 메인 페이지 디자인 사이클

## 적용 기준

`PT/DESIGN.md`와 프로젝트의 Pathi 캐릭터/서비스 구조를 기준으로 다음 규칙을 적용했다.

- warm off-white 배경, 검정 타이포그래피, 오렌지 포인트
- 긴 설명 대신 16:9 포스터형 장면과 도식 중심 구성
- Pathi를 장식이 아니라 입력 → 분석 → 준비를 안내하는 가이드로 사용
- 핵심 메시지는 한 화면에 한 문장 수준으로 제한
- 외부 이미지/CDN 없이 inline SVG로 재현 가능한 시각 자산 구성

## 역할 분리 컨텍스트

| 역할 | 평가 맥락 |
|---|---|
| Brand Director | PT 팔레트, 타이포그래피, 기존 네온 다크 톤 제거 여부 |
| Visual Story Agent | Pathi 반복 활용, 포스터 비율, 도식/차트/장면 수 |
| UX Copy Agent | 전체 문장량, 문단·제목 길이, CTA 명확성 |
| Frontend QA Agent | 반응형, 접근성, 키보드 포커스, reduced motion, self-contained 구현 |

## 반복 결과

| 버전 | 점수 | 결과 |
|---|---:|---|
| `home_pathi_reference_round1.html` | 55.0 | PT 팔레트 불일치 및 시각 모듈 부족으로 재설계 |
| `home_pathi_reference.html` | **99.2** | 90점 기준 통과 |

점수는 `evaluate_home_mockup.py`의 재현 가능한 정적 평가 루브릭 기준이다.

### 최종 점수 상세

- Brand alignment: 20 / 20
- Visual storytelling: 19.2 / 20
- Text economy: 20 / 20
- Accessibility: 20 / 20
- Implementation: 20 / 20

## 최종 산출물

- `home_pathi_reference.html` - 최종 메인 페이지 시안
- `home_pathi_reference_preview.png` - 데스크톱 전체 미리보기
- `home_pathi_reference_mobile_preview.png` - 모바일 전체 미리보기
- `home_pathi_reference_round1.html` - 1차 버전
- `home_pathi_reference_evaluation.json` - 반복별 평가 결과
- `evaluate_home_mockup.py` - 평가 스크립트
