# 11회차 프로젝트 명세서 — jobs_careers 데이터 적용

> **SSAFY 15기 AI 프로젝트 | 11회차 | 파이썬 데이터 시각화 (자유 데이터 파트)**  
> 기준 문서: `(25_0605) 관통템플릿_[파이썬]_[데이터시각화]_[15기]_[11회차]_r1.pdf`

---

## 1. 데이터 개요

### 📁 파일 정보

| 항목 | 내용 |
|------|------|
| 파일명 | `jobs_careers.jsonl` |
| 형식 | JSONL (JSON Lines — 한 줄 = 한 레코드) |
| 총 레코드 수 | **10,000건** |
| 결측값 | **없음** (완전한 데이터) |
| 데이터 성격 | 한국 기업 채용 공고 합성 데이터 (지원자 수 예측 모델 학습용) |

### 📊 컬럼 구조

| 컬럼명 | 데이터 타입 | 설명 | 예시값 |
|--------|------------|------|--------|
| `job_title` | string | 직무명 (레벨 + 직종) | "주니어 백엔드 엔지니어" |
| `industry` | string (범주형, 16종) | 산업 분야 | "IT", "제조", "게임", "금융" |
| `company_name` | string (범주형, 45개) | 회사명 | "카카오", "삼성전자", "LG전자" |
| `annual_salary_krw` | int | 연봉 (원 단위) | 47,565,378 ~ 183,668,255 |
| `required_experience_years` | int | 요구 경력 연수 | 0 ~ 12 |
| `applicant_count` | int | **지원자 수 (타겟 변수)** | 10 ~ 719 |

### 🔑 도메인 특성

- **직무명 구조:** `{레벨} {직종}` 형태 — 레벨 6단계(신입/주니어/리드/시니어/수석/전문) × 직종 48종 = 총 288가지
- **산업 분야 16종:** IT, 제조, 게임, 금융, 유통, 의료, 교육, 미디어, 건설, 항공, 콘텐츠, 물류, 바이오, 법률, 에너지, 컨설팅
- **연봉 범위:** 최소 4,756만원 ~ 최대 1억 8,366만원 (평균 약 9,939만원)
- **지원자 수 범위:** 최소 10명 ~ 최대 719명 (평균 117.7명)

---

## 2. 시각화 주제 정의

> **"한국 채용시장 경쟁률 분석 대시보드"**
>
> 경력, 연봉, 산업, 직무 등 다양한 요소가 채용 경쟁률(지원자 수)에 미치는 영향을 다각도로 시각화하여 구직자와 기업 모두에게 유의미한 인사이트를 제공한다.

---

## 3. 요구사항별 구현 명세

> 자유 데이터 파트: **F307 ~ F312** (필수), **F313 ~ F315** (선택)

---

### F307 — 자유 데이터 선택 및 구조 분석

**구현 내용:**
- `jobs_careers.jsonl` 파일을 JavaScript로 로드
- 전체 컬럼 구조, 데이터 타입, 값 범위, 고유값 목록 콘솔 출력 또는 화면 표시
- 주제 정의: "경력·연봉·산업이 채용 경쟁률에 미치는 영향 분석"

**데이터 로드 방식:**
```javascript
// JSONL 파싱 예시
const rawText = await fetch('./data/jobs_careers.jsonl').then(r => r.text());
const records = rawText.trim().split('\n').map(line => JSON.parse(line));
```

**README.md 작성 항목 (F307 요구사항):**
- 선택한 데이터셋 이름 및 출처
- 컬럼 설명 (위 표 참조)
- 시각화 주제 및 선택 이유
- 발견한 주요 인사이트 요약

---

### F308 — 자유 데이터 지표 비교 시각화

**목표:** 2개 이상 지표 비교·관계 표현 차트 구현

#### 차트 A: 산업별 평균 연봉 vs 평균 지원자 수 (이중 막대 차트)

| 항목 | 내용 |
|------|------|
| 차트 유형 | 이중 막대 차트 (Grouped Bar Chart) |
| X축 | 산업 분야 (16종) |
| Y축 1 | 평균 연봉 (만원) |
| Y축 2 | 평균 지원자 수 (명) |
| 라이브러리 | Chart.js — `type: 'bar'`, `datasets` 2개 구성 |
| 인사이트 포인트 | 콘텐츠: 낮은 연봉 ↔ 높은 경쟁률 / 항공: 높은 연봉 ↔ 낮은 경쟁률 |

**데이터 가공 로직:**
```javascript
// 산업별 평균 집계
const byIndustry = {};
records.forEach(r => {
  if (!byIndustry[r.industry]) byIndustry[r.industry] = { salarySum: 0, applicantSum: 0, count: 0 };
  byIndustry[r.industry].salarySum += r.annual_salary_krw;
  byIndustry[r.industry].applicantSum += r.applicant_count;
  byIndustry[r.industry].count++;
});
const industries = Object.keys(byIndustry);
const avgSalaries = industries.map(ind => Math.round(byIndustry[ind].salarySum / byIndustry[ind].count / 10000));
const avgApplicants = industries.map(ind => (byIndustry[ind].applicantSum / byIndustry[ind].count).toFixed(1));
```

#### 차트 B: 직무 레벨별 평균 지원자 수 비교 (수평 막대 차트)

| 항목 | 내용 |
|------|------|
| 차트 유형 | 수평 막대 차트 (Horizontal Bar) |
| 분류 기준 | job_title에서 레벨 추출 (신입/주니어/리드/시니어/수석/전문) |
| 측정값 | 평균 지원자 수 |
| 라이브러리 | Chart.js — `indexAxis: 'y'` |
| 인사이트 포인트 | 신입 408명 vs 전문 13명 — 30배 이상 차이 |

**레벨 추출 로직:**
```javascript
const levels = ['신입', '주니어', '리드', '시니어', '수석', '전문'];
const levelGroups = {};
records.forEach(r => {
  const level = levels.find(lv => r.job_title.startsWith(lv)) || '기타';
  if (!levelGroups[level]) levelGroups[level] = [];
  levelGroups[level].push(r.applicant_count);
});
const avgByLevel = levels.map(lv => ({
  label: lv,
  avg: levelGroups[lv] ? levelGroups[lv].reduce((a,b) => a+b, 0) / levelGroups[lv].length : 0
}));
```

---

### F309 — 자유 데이터 추이·분포 시각화

**목표:** 시간/범주/분포 중 1개 이상 관점 포함한 차트

#### 차트 C: 경력 연수별 평균 지원자 수 추이 (선 차트)

| 항목 | 내용 |
|------|------|
| 차트 유형 | 선 그래프 (Line Chart) |
| X축 | 경력 연수 (0 ~ 12년) |
| Y축 | 평균 지원자 수 |
| 라이브러리 | Chart.js — `type: 'line'`, smooth curve |
| 인사이트 포인트 | 0년: 408명 → 5년: 100명 → 12년: 13명 (급격한 감소) |

**데이터 가공 로직:**
```javascript
const byExp = {};
records.forEach(r => {
  const exp = r.required_experience_years;
  if (!byExp[exp]) byExp[exp] = [];
  byExp[exp].push(r.applicant_count);
});
const expLabels = Object.keys(byExp).sort((a,b) => a-b);
const expAvg = expLabels.map(exp => (byExp[exp].reduce((a,b)=>a+b,0) / byExp[exp].length).toFixed(1));
```

#### 차트 D: 연봉 구간별 분포 (히스토그램)

| 항목 | 내용 |
|------|------|
| 차트 유형 | 막대 차트 (히스토그램) |
| X축 | 연봉 구간 (2천만원 단위: ~4천, 4천~6천, 6천~8천, 8천~1억, 1억~1.2억, ...) |
| Y축 | 해당 구간 공고 수 |
| 라이브러리 | Chart.js — `type: 'bar'`, 인접 막대 사이 간격 0 |
| 인사이트 포인트 | 8천만~1억 구간 30.5%, 1억 이상 46% |

**데이터 가공 로직:**
```javascript
const salaryBins = [0, 4000, 6000, 8000, 10000, 12000, 15000, 20000]; // 만원 단위
const binLabels = ['~4천만', '4천~6천만', '6천~8천만', '8천만~1억', '1억~1.2억', '1.2억~1.5억', '1.5억+'];
const binCounts = new Array(salaryBins.length - 1).fill(0);
records.forEach(r => {
  const salaryMan = r.annual_salary_krw / 10000;
  for (let i = 0; i < salaryBins.length - 1; i++) {
    if (salaryMan >= salaryBins[i] && salaryMan < salaryBins[i+1]) {
      binCounts[i]++;
      break;
    }
  }
});
```

---

### F310 — 자유 시각화 결과 해석

**목표:** 차트 설계 의도, 데이터 가공 방식, 인사이트 문서화

**README.md에 포함할 인사이트 내용:**

#### 핵심 발견사항

1. **경력의 역설 (Experience Paradox)**
   - 신입(0년) 평균 지원자: **408명** vs 12년 경력: **13명** → 약 30배 차이
   - 경력이 쌓일수록 경쟁은 줄어들지만 포지션 자체가 희소해짐

2. **연봉-경쟁률 역설 (Salary Paradox)**
   - 콘텐츠 산업: 낮은 평균 연봉(8,919만원) ↔ 높은 경쟁률(147.4명/공고)
   - 항공 산업: 높은 평균 연봉(1억 102만원) ↔ 낮은 경쟁률(81.7명/공고)
   - **"연봉이 높다고 경쟁률이 높지 않다"** — 직무 선호도·진입장벽이 더 큰 영향

3. **가장 치열한 포지션 TOP 5**
   | 순위 | 직무명 | 평균 지원자 |
   |------|--------|-----------|
   | 1 | 주니어 퍼포먼스 마케터 | 403.7명 |
   | 2 | 주니어 유통 영업 | 321.4명 |
   | 3 | 주니어 게임 클라이언트 개발자 | 294.6명 |
   | 4 | 주니어 전략 컨설턴트 | 293.7명 |
   | 5 | 주니어 게임 서버 개발자 | 287.7명 |

4. **연봉 분포 특성**
   - 1억 이상 공고가 전체의 46%를 차지 → 고연봉 포지션 다수
   - 8천만~1억 구간이 30.5%로 최다 빈도

**차트별 설계 의도:**
- F308 이중막대: 연봉과 경쟁률이 동시에 보여야 "역설"을 직관적으로 확인 가능
- F309 선차트: 경력 연수라는 연속 변수의 '추이'를 표현하기 위해 선 그래프 선택
- F309 히스토그램: 연봉의 분포 형태(우치우/정규/편향 등) 파악에 최적

---

### F311 — 자유 데이터 복합 시각화 화면

**목표:** 복수 차트 조합 → "한국 채용시장 경쟁률 분석" 주제 중심 통합 화면

#### 대시보드 레이아웃 설계

```
┌─────────────────────────────────────────────────────────┐
│  🏆 한국 채용시장 경쟁률 분석 대시보드                      │
│  [산업 필터: ALL ▼]  [경력 범위: 0 ━━●━━ 12년]            │
├─────────────────┬───────────────────────────────────────┤
│                 │                                       │
│  [차트 A]       │  [차트 B]                             │
│  산업별         │  직무 레벨별                           │
│  연봉 vs 경쟁률  │  평균 지원자 수                        │
│  (이중막대)      │  (수평막대)                           │
│                 │                                       │
├─────────────────┴───────────────────────────────────────┤
│                 │                                       │
│  [차트 C]       │  [차트 D]                             │
│  경력 연수별     │  연봉 구간별                           │
│  지원자 추이     │  공고 분포                            │
│  (선 그래프)     │  (히스토그램)                         │
│                 │                                       │
├─────────────────┴───────────────────────────────────────┤
│  📊 요약 통계: 전체 공고 수 | 평균 경쟁률 | 최고 경쟁 직무   │
└─────────────────────────────────────────────────────────┘
```

**Vue.js 컴포넌트 구조:**
```
src/
├── components/
│   ├── jobs/
│   │   ├── JobsDashboard.vue       ← 대시보드 컨테이너 (F311)
│   │   ├── IndustrySalaryChart.vue ← 차트 A (F308)
│   │   ├── LevelApplicantChart.vue ← 차트 B (F308)
│   │   ├── ExperienceTrendChart.vue← 차트 C (F309)
│   │   ├── SalaryDistChart.vue     ← 차트 D (F309)
│   │   ├── JobsFilter.vue          ← 필터 UI (F312)
│   │   └── SummaryStats.vue        ← 요약 통계 카드
│   └── common/
│       └── ChartWrapper.vue        ← 차트 공통 래퍼
├── composables/
│   └── useJobsData.js              ← 데이터 로드·가공 로직 분리
└── data/
    └── jobs_careers.jsonl
```

---

### F312 — 인터랙티브 대시보드 구성

**목표:** 사용자 입력(클릭/드래그/필터/스크롤)에 따라 전체 차트 동적 갱신

#### 인터랙션 설계

| 인터랙션 | UI 요소 | 동작 |
|---------|---------|------|
| **산업 필터** | 드롭다운 또는 체크박스 멀티셀렉트 | 선택된 산업만 모든 차트에 반영 |
| **경력 범위 슬라이더** | Range Slider (0~12년) | 해당 경력 범위 공고만 필터링 |
| **차트 클릭** | 막대/점 클릭 | 해당 산업/레벨 상세 정보 팝업 표시 |
| **회사 검색** | 텍스트 입력 | 특정 회사명 기준 데이터 강조 표시 |
| **차트 툴팁** | 마우스 호버 | 상세 수치 표시 (Chart.js 기본 제공) |

**Vue.js 반응형 데이터 흐름:**
```javascript
// useJobsData.js 핵심 구조
const filters = reactive({
  industries: [],        // 선택된 산업 목록 (빈 배열 = 전체)
  expRange: [0, 12],    // 경력 범위 [min, max]
  company: ''           // 회사 검색어
});

const filteredRecords = computed(() => {
  return allRecords.value.filter(r => {
    const industryOk = filters.industries.length === 0 || filters.industries.includes(r.industry);
    const expOk = r.required_experience_years >= filters.expRange[0] 
               && r.required_experience_years <= filters.expRange[1];
    const companyOk = !filters.company || r.company_name.includes(filters.company);
    return industryOk && expOk && companyOk;
  });
});

// filteredRecords가 바뀌면 모든 차트 자동 업데이트 (Vue 반응형)
```

---

## 4. 심화 기능 적용 방안 (선택)

### F313 — AI 기반 시각화 분석

**적용 방안:**
- 현재 필터 상태의 데이터 요약을 프롬프트로 구성
- OpenAI API (또는 Gemini API) 호출 → 채용 트렌드 인사이트 생성
- 대시보드 하단에 "AI 분석 결과" 텍스트 박스로 표시

**프롬프트 템플릿 예시:**
```
현재 필터 조건: {산업}, 경력 {min}~{max}년
평균 지원자 수: {avg}명, 평균 연봉: {salary}만원
이 데이터를 기반으로 채용시장 트렌드와 구직자 전략을 간략히 분석해줘.
```

### F314 — 다크모드 테마 적용

**적용 방안:**
- Vue 3의 `provide/inject` 또는 Pinia store로 테마 상태 관리
- Chart.js `plugins.legend`, `scales` 색상을 테마에 따라 동적 변경
- CSS 변수(`--bg-color`, `--text-color`, `--grid-color`) 활용

**차트 색상 전환 예시:**
```javascript
const chartDefaults = computed(() => ({
  color: isDark.value ? '#e2e8f0' : '#1a202c',
  borderColor: isDark.value ? '#4a5568' : '#e2e8f0',
}));
```

### F315 — 차트 이미지 저장 기능

**적용 방안:**
- Chart.js `chart.toBase64Image()` 메서드 활용
- 각 차트 컴포넌트에 "📥 PNG 저장" 버튼 추가
- `<a>` 태그 `download` 속성으로 다운로드 트리거

```javascript
const downloadChart = (chartRef, filename) => {
  const url = chartRef.value.chart.toBase64Image('image/png', 1.0);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
};
```

---

## 5. 기술 스택 및 프로젝트 구조

### 기술 스택

| 분류 | 기술 | 용도 |
|------|------|------|
| 언어 | HTML, CSS, JavaScript | 기본 구조 및 스타일 |
| 프레임워크 | Vue.js 3 (Composition API) | SPA 구성 |
| 시각화 | Chart.js 4.x | 주 차트 라이브러리 |
| 시각화 보조 | Apache ECharts (선택) | 복잡한 차트 대체 가능 |
| 개발 도구 | Visual Studio Code | 에디터 |
| 브라우저 | Chrome | 권장 실행 환경 |

### 디렉토리 구조 (권장)

```
11_pjt/
├── index.html
├── src/
│   ├── App.vue
│   ├── main.js
│   ├── components/
│   │   ├── sports/           ← F301~F306 (스포츠 데이터 파트)
│   │   │   └── ...
│   │   └── jobs/             ← F307~F312 (jobs_careers 파트)
│   │       ├── JobsDashboard.vue
│   │       ├── IndustrySalaryChart.vue
│   │       ├── LevelApplicantChart.vue
│   │       ├── ExperienceTrendChart.vue
│   │       ├── SalaryDistChart.vue
│   │       ├── JobsFilter.vue
│   │       └── SummaryStats.vue
│   ├── composables/
│   │   ├── useSportsData.js
│   │   └── useJobsData.js    ← 데이터 로드·필터·집계 로직
│   └── data/
│       ├── sports.jsonl
│       └── jobs_careers.jsonl
└── README.md
```

---

## 6. 구현 순서 (권장)

```
1. jobs_careers.jsonl 로드 및 파싱 확인 (useJobsData.js)
   ↓
2. F307: 데이터 구조 콘솔 출력 + README.md 초안 작성
   ↓
3. F308: IndustrySalaryChart.vue (이중막대), LevelApplicantChart.vue (수평막대) 구현
   ↓
4. F309: ExperienceTrendChart.vue (선그래프), SalaryDistChart.vue (히스토그램) 구현
   ↓
5. F310: 각 차트의 설계 의도·인사이트 README.md에 기록
   ↓
6. F311: JobsDashboard.vue로 4개 차트 통합 배치 + SummaryStats.vue
   ↓
7. F312: JobsFilter.vue 구현 (산업 드롭다운, 경력 슬라이더) + 반응형 연결
   ↓
8. (선택) F313~F315 심화 기능 추가
   ↓
9. 전체 테스트 + 화면 캡처 + GitLab 업로드
```

---

## 7. 참고 자료

| 자료 | URL |
|------|-----|
| Chart.js 공식 문서 | https://www.chartjs.org/docs/latest/ |
| ECharts 공식 문서 | https://echarts.apache.org/en/index.html |
| Vue.js 3 공식 문서 | https://vuejs.org/guide/introduction.html |
| MDN Canvas API | https://developer.mozilla.org/ko/docs/Web/API/Canvas_API |
| Chart.js 이중 Y축 예제 | https://www.chartjs.org/docs/latest/samples/scales/multi-axis.html |
| Chart.js 인터랙션 가이드 | https://www.chartjs.org/docs/latest/configuration/interactions.html |

---

## 8. 제출 체크리스트

### 필수 기능 (F307~F312)

- [ ] **F307** — `jobs_careers.jsonl` 로드 완료 + README.md에 데이터 구조 기술
- [ ] **F308** — 산업별 이중막대 차트 + 레벨별 수평막대 차트 (2개 이상 지표 비교)
- [ ] **F309** — 경력별 선 그래프 + 연봉 히스토그램 (분포/추이 1개 이상)
- [ ] **F310** — README.md에 차트 설계 의도 + 인사이트 3개 이상 기재
- [ ] **F311** — `JobsDashboard.vue`에 4개 차트 통합 배치 완료
- [ ] **F312** — 산업 필터 + 경력 슬라이더 동작 확인 (필터 변경 시 차트 갱신)

### 심화 기능 (선택)

- [ ] **F313** — AI 분석 결과 표시 기능 구현
- [ ] **F314** — 다크모드 토글 + 차트 색상 전환 동작 확인
- [ ] **F315** — PNG 다운로드 버튼 동작 확인

### 제출물

- [ ] GitLab `11_pjt` 레포지토리에 전체 소스 코드 업로드
- [ ] 각 요구사항(F307~F312) 화면 캡처 이미지 첨부
- [ ] `README.md` 완성 (데이터 구조 + 인사이트 + 학습 내용 + 느낀 점)

---

*이 명세서는 `(25_0605) 관통템플릿_[파이썬]_[데이터시각화]_[15기]_[11회차]_r1.pdf`를 기준으로 `jobs_careers.jsonl` 데이터에 특화하여 작성되었습니다.*
