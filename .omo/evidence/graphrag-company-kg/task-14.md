# T14. Korean architecture documentation

## 구현

- `docs/10_GraphRAG_기업_KG_구현.md`를 추가했다.
- 문서에 DB와 KG 차이, SQL source-of-truth, source/claim/fact 흐름, private evidence 경계, 임베딩 도입 조건을 정리했다.
- 최초 1회 작업과 서비스 지속 업데이트 작업을 분리했다.
- 기업/직무 없음, 공고 내용 변경 시나리오를 서비스 동작 기준으로 작성했다.
- 기존 `docs/09_로드맵_생성_기업검색_및_기준직무_fallback.md`의 fallback `Job` 생성 설명을 현재 구현에 맞게 정정했다.
- 기존 `docs/03_직무검색_API_및_분석_payload_개선.md`, `docs/05_채용공고_자기소개서_DB저장.md`, `docs/06_직무_DB_연동_및_표시명_정리.md` 상단에 현재 기준은 `docs/10_GraphRAG_기업_KG_구현.md`라는 superseded 안내를 추가했다.

## 검증

- Backend regression: `.omo/evidence/graphrag-company-kg/wave4-backend-regression-pytest.txt`
  - 70 passed
- Frontend static/build/E2E:
  - `.omo/evidence/graphrag-company-kg/wave4-frontend-green-test.txt`
  - `.omo/evidence/graphrag-company-kg/wave4-frontend-build.txt`
  - `.omo/evidence/graphrag-company-kg/wave4-frontend-e2e.txt`

## 판정

완료. 문서는 profiles/cover_letters/analyses를 GraphRAG DB로 주장하지 않고, companies SQL과 KG projection의 역할을 분리한다.
