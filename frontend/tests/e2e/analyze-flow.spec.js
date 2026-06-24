import { expect, test } from '@playwright/test'

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('access', 'e2e-token')
  })
})

test('analyze flow saves manual posting, cover letter, submits, and renders result', async ({ page }) => {
  await mockManualPosting(page)
  await mockProfileSave(page)
  await page.route('**/api/analyze/', async route => {
    if (route.request().method() === 'POST') {
      const body = route.request().postDataJSON()
      expect(body.job_id).toBe(11)
      expect(body.job_posting_url).toBe('')
      expect(body.job_posting_text).toContain('담당업무:')
      expect(body.submitted_cover_letter).toContain('Q. 지원동기')
      await route.fulfill({ status: 201, json: { id: 99 } })
    } else {
      await route.fallback()
    }
  })
  await mockAnalysisResult(page)

  await fillManualPosting(page)
  await page.locator('#job-select').selectOption('11')
  await page.locator('#next-step-btn').click()

  await page.locator('.cover-question-input').fill('지원동기')
  await page.locator('.cover-answer-input').fill('제출했던 자기소개서 답변')
  await page.locator('#next-cover-letter-btn').click()

  await page.getByLabel(/기술면접/).check()
  await page.locator('#submit-analyze-btn').click()

  await expect(page).toHaveURL(/\/analyze\/99$/)
  await expect(page.getByRole('heading', { name: '역량 분석' })).toBeVisible()
  const competencySection = page.locator('#gap')
  await expect(competencySection.getByText('어필 가능', { exact: true })).toBeVisible()
  await expect(competencySection.getByText('답변 정리', { exact: true })).toBeVisible()
  await expect(competencySection.getByText('학습 필요', { exact: true })).toBeVisible()
  await expect(page.getByText('API 성능 개선').first()).toBeVisible()
  await expect(page.getByText('시스템 설계').first()).toBeVisible()
  await expect(page.getByRole('heading', { name: '직무 역량 매칭도' })).toHaveCount(0)
  await expect(page.getByRole('heading', { name: '준비 항목' })).toBeVisible()
  await expect(page.getByRole('heading', { name: '로보틱스' })).toBeVisible()
  await expect(page.getByText('왜 준비하나요?').first()).toBeVisible()
  await expect(page.getByText('로봇 팔 제어 정확도 개선 경험')).toBeVisible()
  await expect(page.getByText('FK와 IK 차이')).toBeVisible()
  await expect(page.getByText('직접 연결되는 경험이 확인되지 않았습니다.').first()).toBeVisible()
  await expect(page.getByLabel('역기구학')).toBeChecked()
  await expect(page.getByLabel('A가 아니라 B 방식을 채택한 이유는 무엇인가요?')).toBeChecked()
  await expect(page.getByText('40%').first()).toBeVisible()
  await page.getByLabel('EtherCAT').check()
  await expect(page.getByText('60%').first()).toBeVisible()
  await page.reload()
  await expect(page.getByLabel('EtherCAT')).toBeChecked()
  await expect(page.getByText('60%').first()).toBeVisible()
})

test('cover letter profile save request contains question and answer', async ({ page }) => {
  await mockManualPosting(page)
  let savedCoverLetters = null
  await page.route('**/api/profile/', async route => {
    if (route.request().method() === 'PUT') {
      savedCoverLetters = route.request().postDataJSON().cover_letters
      await route.fulfill({ status: 200, json: { cover_letters: savedCoverLetters } })
    } else {
      await route.fulfill({ json: { cover_letters: [] } })
    }
  })

  await fillManualPosting(page)
  await page.locator('#next-step-btn').click()
  await page.locator('.cover-question-input').fill('직무 역량을 설명해 주세요')
  await page.locator('.cover-answer-input').fill('백엔드 API와 DB 최적화 경험이 있습니다.')
  await page.locator('#next-cover-letter-btn').click()

  expect(savedCoverLetters).toEqual([
    {
      question: '직무 역량을 설명해 주세요',
      answer: '백엔드 API와 DB 최적화 경험이 있습니다.',
    },
  ])
})

async function fillManualPosting(page) {
  await page.goto('/analyze/new')
  await page.locator('#company-name-input').fill('쿠팡')
  await page.locator('#job-title-input').fill('백엔드 개발자')
  await page.locator('#responsibilities-input').fill('주문/배송 API 개발과 대규모 트래픽 처리')
  await page.locator('#requirements-input').fill('Python, Database, REST API 경험')
  await page.locator('#preferred-input').fill('분산 시스템 경험')
  await page.locator('#match-job-btn').click()
  await expect(page.locator('.company-profile-card').getByText('쿠팡')).toBeVisible()
}

async function mockManualPosting(page) {
  await page.route('**/api/job-postings/manual/**', async route => {
    await route.fulfill({
      status: 201,
      json: {
        supported: true,
        company: {
          id: 1,
          company_name: '쿠팡',
          industry: 'Commerce',
          size: 'large',
          talent_description: '고객 중심',
          culture_keywords: ['실험', '속도'],
        },
        job_posting: { id: 7, resolved: true },
        matched_job: { id: 11, job_title: '백엔드 개발자' },
        jobs: [{
          id: 11,
          job_title: '백엔드 개발자',
          interview_stages: [
            { order: 1, type: 'technical', desc: '기술 면접' },
            { order: 2, type: 'personality', desc: '인성 면접' },
          ],
        }],
        jobs_meta: { count: 1, page: 1, page_size: 30 },
      },
    })
  })
}

async function mockProfileSave(page) {
  await page.route('**/api/profile/', async route => {
    if (route.request().method() === 'PUT') {
      await route.fulfill({ status: 200, json: route.request().postDataJSON() })
    } else {
      await route.fulfill({ json: { cover_letters: [] } })
    }
  })
}

async function mockAnalysisResult(page) {
  await page.route('**/api/analyze/99/', async route => {
    await route.fulfill({
      json: {
        id: 99,
        company_name: '쿠팡',
        job_title: '백엔드 개발자',
        selected_interview_types: ['technical'],
        competency_gap: {
          summary: 'API 개선 경험은 강점이고 시스템 설계 지식은 우선 보완이 필요합니다.',
          competency_map: [{
            keyword: 'API 성능 개선',
            status: 'strength',
            importance: 'required',
            signal: '성능 개선 프로젝트 경험 있음',
            action: '병목 분석 과정을 어필',
          }, {
            keyword: '기술 선택 근거',
            status: 'articulate',
            importance: 'required',
            signal: '구현 경험은 있으나 선택 이유 부족',
            action: '트레이드오프 답변 정리',
          }, {
            keyword: '시스템 설계',
            status: 'study',
            importance: 'preferred',
            signal: '대규모 설계 경험 근거 없음',
            action: '분산 구조 우선 학습',
          }],
          strengths: [{
            keyword: '주문 API 성능 개선',
            experience: '주문 조회 API 개선 프로젝트',
            evidence: '응답 시간을 비교한 기록이 있습니다.',
            job_relevance: '대규모 트래픽 처리 업무와 직접 연결됩니다.',
            interview_focus: '병목 분석 과정과 본인 역할을 강조합니다.',
          }],
          gaps: [{
            keyword: '시스템 설계',
            gap_type: 'knowledge',
            reason: '대규모 시스템 설계 경험 근거가 부족합니다.',
            evidence: '채용공고는 분산 시스템 경험을 우대합니다.',
            action: '트레이드오프를 포함한 설계 답변을 준비합니다.',
            priority: 'high',
          }],
          required_competencies: [{
            keyword: 'Python',
            importance: 'required',
            evidence: '채용공고 필수 요건입니다.',
          }],
        },
        text_roadmap: '로보틱스 > 역기구학',
        timeline_data: [
          {
            category: '로보틱스',
            summary: '프로젝트와 채용공고의 제어 요구가 겹치는 영역입니다.',
            sources: ['채용공고', '프로젝트 1', '프로젝트 2'],
            subtopics: [
              {
                title: '역기구학',
                done: true,
                preparation_type: 'appeal',
                job_reason: '로봇 제어 업무의 핵심 지식입니다.',
                matched_experience: '로봇 팔 제어 정확도 개선 경험',
                experience_source: '프로필·자기소개서',
                study_focus: ['FK와 IK 차이', '특이점', '관절 제한'],
                approach: '프로젝트 문제, 적용 방식, 제약 처리, 검증 결과 순서로 어필하세요.',
                question: '1번 프로젝트에서 역기구학을 어떻게 사용했나요?',
                answer_guide: '목표 위치 계산과 관절각 산출 흐름을 설명하세요.',
                evidence: '자기소개서의 로봇 팔 제어 정확도 개선 경험',
                study_goal: 'FK/IK 차이와 특이점 대응을 설명할 수 있어야 합니다.',
                follow_up_questions: ['관절 제한은 어느 단계에서 반영했나요?'],
              },
              {
                title: '모션 플래닝',
                done: true,
                preparation_type: 'organize',
                job_reason: '경로 생성과 실시간 재계획 능력을 확인하는 개념입니다.',
                matched_experience: '경로 탐색 방식의 성능 비교 경험',
                experience_source: '자기소개서',
                study_focus: ['A*와 RRT 차이', '비용 함수', '재계획'],
                approach: '검토한 대안, 선택 기준, 결과를 직무 요구와 연결하세요.',
                question: 'A가 아니라 B 방식을 채택한 이유는 무엇인가요?',
                answer_guide: '계산 비용과 장애물 재탐색 빈도를 기준으로 답변하세요.',
                evidence: '성능 비교 기록',
                study_goal: 'A*, RRT, DWA의 장단점을 비교할 수 있어야 합니다.',
                follow_up_questions: ['실시간성이 깨질 때 fallback은 무엇인가요?'],
              },
            ],
          },
          {
            category: '통신',
            summary: '제어 주기와 안정성 관점에서 프로토콜 선택 기준을 정리합니다.',
            sources: ['기업 DB', '직무 DB', '채용공고'],
            subtopics: [
              {
                title: 'EtherCAT',
                done: false,
                preparation_type: 'study',
                job_reason: '다축 장비의 실시간 동기화와 제어 주기 설명에 필요합니다.',
                matched_experience: '',
                experience_source: '없음',
                study_focus: ['실시간 Ethernet', '분산 클럭', '다축 동기화'],
                approach: '일반 Ethernet 차이부터 장비 제어 적용 순서로 학습하세요.',
                question: 'EtherCAT을 사용하는 이유를 설명할 수 있나요?',
                answer_guide: '실시간성과 분산 클럭을 중심으로 답변하세요.',
                evidence: '산업용 자동화 키워드',
                study_goal: '일반 Ethernet과의 차이를 설명할 수 있어야 합니다.',
                follow_up_questions: [],
              },
              {
                title: 'CAN',
                done: false,
                preparation_type: 'organize',
                job_reason: '센서와 액추에이터 통신의 안정성과 병목 판단에 필요합니다.',
                matched_experience: '센서 데이터 수집 경험',
                experience_source: '프로필',
                study_focus: ['CAN frame', 'arbitration', 'bus load'],
                approach: '센서 연동 경험을 CAN 통신 특성과 연결해 정리하세요.',
                question: 'CAN 통신의 장점과 병목은 무엇인가요?',
                answer_guide: 'arbitration과 bus load를 구분해 설명하세요.',
                evidence: '센서 데이터 수집 경험',
                study_goal: 'CAN frame과 arbitration을 설명할 수 있어야 합니다.',
                follow_up_questions: [],
              },
            ],
          },
          {
            category: 'Rust',
            summary: '학습 이력을 제어 모듈 안정성 관점으로 연결합니다.',
            sources: ['개인 프로필', '자기소개서'],
            subtopics: [
              {
                title: '메모리 안전성과 실시간 제약',
                done: false,
                preparation_type: 'organize',
                job_reason: '제어 모듈의 안정성과 기존 시스템 연동 비용을 판단하기 위해 필요합니다.',
                matched_experience: 'Rust 학습 경험',
                experience_source: '프로필',
                study_focus: ['ownership', 'unsafe 경계', 'FFI'],
                approach: '안정성 이득과 연동 비용을 균형 있게 정리하세요.',
                question: '로봇 제어 모듈에 Rust를 적용한다면 장점과 비용은 무엇인가요?',
                answer_guide: 'ownership, FFI, 팀 러닝커브를 균형 있게 설명하세요.',
                evidence: 'Rust 학습 경험',
                study_goal: 'unsafe 경계 설정을 답변으로 정리할 수 있어야 합니다.',
                follow_up_questions: [],
              },
            ],
          },
        ],
        status: 'done',
        created_at: '2026-06-05T00:00:00Z',
      },
    })
  })
}
