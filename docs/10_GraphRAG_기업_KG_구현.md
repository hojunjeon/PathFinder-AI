# GraphRAG 기업 KG 구현 설계

## 결론

PathFinder AI에서 GraphRAG는 `companies`를 대체하는 CRUD 저장소가 아니라, 기업 주변의 확장 지식을 검증 가능한 형태로 붙이는 파생 지식 계층이다.

`companies`는 SQL 원본이다. 기업명, 산업, 규모, 인재상, 문화 키워드처럼 서비스가 직접 관리해야 하는 기본 값은 SQL에서 수정한다. KG는 기업의 주력 사업, 제품, 최신 이슈, 기술 스택, 직무 후보, 역량 관계처럼 스키마가 계속 넓어질 수 있는 정보를 `source -> claim -> fact` 흐름으로 관리한다.

사용자 프로필, 채용공고, 자기소개서, 분석 결과는 public KG에 넣지 않는다. 이 데이터는 분석 시점의 private evidence로만 LLM에 전달한다.

## 최종 데이터 구조

### SQL 원본

| 구분 | 테이블 | 역할 |
|---|---|---|
| 기업 원본 | `companies` | 기업 CRUD의 기준. 기업명, 산업, 규모, 인재상, 문화 키워드, 지원 여부를 관리한다. |
| 사용자 프로필 | `profiles` | 사용자의 이력, 프로젝트, 수상, 자격증을 저장한다. 자기소개서는 저장하지 않는다. |
| 사용자 공고 | `job_postings` | 사용자가 입력한 회사/직무/담당업무/자격요건/우대사항의 스냅샷이다. |
| 자기소개서 | `cover_letters` | 특정 지원 분석에서 제출한 자기소개서 원문이다. 사용자, 기업, 공고, 분석과 연결된다. |
| 분석 결과 | `analyses` | LLM 결과를 저장한다. `company`, `job_posting`, `cover_letter`를 참조하고 기존 결과 shape을 유지한다. |

### 기업 KG 계층

| 구분 | 테이블 | 역할 |
|---|---|---|
| 출처 문서 | `company_source_documents` | fixture, 관리자 입력, 홈페이지, 뉴스, 보고서 등 public/admin 출처를 저장한다. |
| 출처 청크 | `company_source_chunks` | 긴 출처 문서를 나눈 조각이다. MVP에서는 embedding 필수가 아니며 `not_required` 상태를 기본으로 둔다. |
| 후보 주장 | `company_knowledge_claims` | 출처에서 추출한 기업 지식 후보이다. 기본은 `pending`이다. |
| 승인 사실 | `company_knowledge_facts` | 승인된 claim만 public KG context로 투영한다. private candidate는 fact가 될 수 없다. |
| 직무/역량 분류 | `role_families`, `skills`, `interview_types`, `study_areas`, `role_family_skills` | 기존 `jobs`의 비공개/저가치 필드를 대체하는 공용 taxonomy다. |

## 입력이 DB 또는 KG가 되는 흐름

### 1. 기업 기본 정보

관리자가 `companies`를 수정하면 SQL 원본만 바뀐다.

```text
관리자: 삼성전자 industry 수정
-> companies row 업데이트
-> 기업 검색/분석의 기본 회사 정보로 사용
```

이 정보는 KG가 아니라 CRUD 대상이다.

### 2. 기업 확장 정보

관리자가 뉴스나 기업 소개 문서를 등록하면 public KG 후보가 된다.

```text
관리자: "삼성전자가 HBM 사업을 확대했다"는 public source 등록
-> company_source_documents 생성
-> company_source_chunks 생성
-> company_knowledge_claims pending 생성
-> 관리자 승인
-> company_knowledge_facts 생성
-> company_graph_context에 포함
```

이 구조가 GraphRAG를 도입하는 핵심이다. 새 정보가 들어와도 `companies` 컬럼을 계속 늘리지 않고 claim/fact로 확장할 수 있다.

### 3. 사용자가 입력한 채용공고

사용자가 로드맵 생성에서 공고를 입력하면 private DB가 된다.

```text
사용자: 쿠팡 / 백엔드 개발자 / 담당업무 / 자격요건 입력
-> job_postings row 생성
-> 분석 요청의 private_evidence_context에 포함
-> public KG fact로 자동 승격하지 않음
```

기업/직무명이 DB/KG에 없어도 사용자가 입력한 공고 자체를 우선 근거로 분석한다. 비슷한 직무명을 근거로 기술스택이나 업무를 추론하지 않는다.

### 4. 사용자가 제출한 자기소개서

자기소개서는 프로필이 아니라 지원 분석 단위로 저장한다.

```text
사용자: 이번 지원용 자기소개서 입력
-> cover_letters row 생성
-> analyses.cover_letter_id 연결
-> private_evidence_context에 포함
-> public KG에는 절대 기록하지 않음
```

## 서비스 동작 시나리오

### 시나리오 1. 기업은 있으나 DB/KG에 없는 직무명

```text
사용자 입력:
- 기업: 쿠팡
- 직무명: 결제 리스크 플랫폼 엔지니어
- 담당업무/자격요건/우대사항: 공고 원문 기반 입력
```

서비스 동작:

1. `companies`에서 쿠팡을 찾는다.
2. `job_postings`에 사용자가 입력한 공고를 저장한다.
3. 기존 `jobs` fallback row를 만들지 않는다.
4. 분석 API는 기존 `job_posting_id`를 받아 같은 `JobPosting` row를 재사용한다.
5. LLM에는 `company_graph_context`와 `private_evidence_context.job_posting`을 분리해서 보낸다.
6. KG에 새 직무가 필요해 보이면 `user_private_candidate` claim까지만 만들 수 있다.
7. public fact 승격은 관리자 redaction 또는 별도 public/admin source가 있어야 한다.

### 시나리오 2. 기업/직무명은 같지만 공고 내용이 바뀐 경우

```text
이전 공고:
- 백엔드 개발자
- Django, REST API

새 공고:
- 백엔드 개발자
- Kafka, 대규모 이벤트 처리, Kubernetes
```

서비스 동작:

1. 새 입력은 새 `job_postings` row로 저장한다.
2. 분석은 최신 사용자 입력 공고를 우선 근거로 삼는다.
3. KG에 있는 일반 기업/역량 정보는 보조 컨텍스트로만 사용한다.
4. 변경 내용은 자동으로 public KG fact가 되지 않는다.
5. 반복적으로 관측되거나 public source가 확인되면 claim으로 만들고 승인 후 fact로 올린다.

## 임베딩 정책

MVP에서는 임베딩을 필수로 하지 않는다.

현재 구조는 SQL 기반 deterministic retrieval이다.

```text
company_id
-> approved company_knowledge_facts 조회
-> source id / fact id / trust_level 포함
-> LLM prompt의 company_graph_context로 전달
```

임베딩은 다음 조건 중 하나가 확인될 때 도입한다.

| 조건 | 도입 방향 |
|---|---|
| 기업별 source document가 길어져 keyword/fact 조회만으로 부족함 | `company_source_chunks.embedding_status=pending` 후 비동기 embedding |
| 사용자가 "이 이슈와 내 경험의 관련성"처럼 의미 검색을 요구함 | public chunks만 vector search 대상으로 사용 |
| 운영 환경에서 비용/성능 병목이 측정됨 | GMS/OpenAI embedding API와 로컬 모델을 비교해 결정 |

로컬 embedding 모델을 서비스 서버 요청 경로에 바로 올리는 것은 권장하지 않는다. HW 자원, 배포 크기, 응답 지연이 커진다. 도입한다면 비동기 worker에서 public source chunk만 처리한다. GMS/OpenAI API를 쓰는 경우에도 private profile/cover letter를 public corpus embedding에 섞지 않는다.

## 최초 1회 작업과 지속 업데이트

### 최초 1회

1. SQL migration으로 KG 관련 테이블과 `cover_letters`, `analyses` 연결 필드를 만든다.
2. 기존 `jobs`를 로드맵 기준 데이터에서 제거한다.
3. 기업 fixture를 `companies`와 초기 `company_source_documents`/claim 후보로 정리한다.
4. 핵심 role/skill/interview/study taxonomy seed를 넣는다.
5. LLM payload를 `company_graph_context`와 `private_evidence_context`로 분리한다.
6. 프론트 분석 생성 흐름을 `company_id + job_posting_id + submitted_cover_letter` 계약으로 맞춘다. 저장된 공고가 없는 direct 분석 생성 요청에서만 `job_posting` 객체를 함께 보낸다.

### 지속 업데이트

1. 관리자나 크롤러가 public/admin source를 추가한다.
2. source에서 pending claim을 만든다.
3. 관리자가 claim을 승인/거절한다.
4. 승인된 claim만 fact로 투영한다.
5. 사용자가 입력한 공고는 private evidence로 저장하고 분석에 사용한다.
6. private candidate는 review backlog로만 보고, public fact 승격에는 별도 출처를 요구한다.
7. 사용자 삭제 시 private candidate claim도 함께 삭제한다.

## 주의할 점

- `companies`를 KG로 완전히 대체하지 않는다. CRUD, 검색, 권한, migration, fixture 운영은 SQL이 더 안정적이다.
- `profiles`, `cover_letters`, `analyses`는 GraphRAG corpus가 아니다.
- LLM 분석 결과를 다음 분석의 사실 근거로 재사용하지 않는다.
- 유사 직무명 기반 추론은 위험하다. 모르는 직무는 사용자 입력 공고를 우선하고, KG는 기업 일반 맥락만 제공한다.
- 사용자 private evidence가 `company_source_chunks`나 `company_knowledge_facts`에 들어가면 설계 위반이다.

## 검증 기준

구현 검증은 다음을 통과해야 한다.

```text
cd backend
.\venv\Scripts\python.exe -m pytest
```

```text
cd llm_server
.\venv\Scripts\python.exe -m pytest
```

```text
cd frontend
npm test
npm run build
npx playwright test tests/e2e/analyze-flow.spec.js tests/e2e/profile.spec.js
```

추가로 고유 private marker를 넣은 자기소개서/공고가 `company_knowledge_facts.object` 또는 `company_source_chunks.chunk_text`에 존재하지 않아야 한다.
