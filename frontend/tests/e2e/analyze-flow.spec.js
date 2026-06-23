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
  await expect(page.getByText('역량 분석')).toBeVisible()
  await expect(page.getByText('시스템 설계').first()).toBeVisible()
  await expect(page.getByText('1주차: 시스템 설계 복습')).toBeVisible()
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
  await expect(page.getByText('매칭된 기업: 쿠팡')).toBeVisible()
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
          strengths: ['프로젝트 경험'],
          gaps: ['시스템 설계'],
          required_competencies: ['Python'],
        },
        text_roadmap: '1주차: 시스템 설계 복습',
        timeline_data: [{ week: 1, title: '1주차', tasks: ['시스템 설계'] }],
        status: 'done',
        created_at: '2026-06-05T00:00:00Z',
      },
    })
  })
}
