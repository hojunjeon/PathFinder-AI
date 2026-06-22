import { expect, test } from '@playwright/test'

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('access', 'e2e-token')
  })
})

test('analyze flow resolves company through backend, submits, and renders result sections', async ({ page }) => {
  await page.route('**/api/companies/resolve/**', async route => {
    await route.fulfill({
      json: {
        id: 1,
        company_name: '쿠팡',
        industry: 'Commerce',
        size: 'large',
        talent_description: '고객 중심',
        culture_keywords: ['실험', '속도'],
      },
    })
  })
  await page.route('**/api/companies/1/jobs/', async route => {
    await route.fulfill({
      json: [{
        id: 11,
        job_title: '백엔드 개발자',
        interview_stages: [
          { order: 1, type: 'technical', desc: '기술 면접' },
          { order: 2, type: 'personality', desc: '인성 면접' },
        ],
      }],
    })
  })
  await page.route('**/api/analyze/', async route => {
    if (route.request().method() === 'POST') {
      await route.fulfill({ status: 201, json: { id: 99 } })
    } else {
      await route.fallback()
    }
  })
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

  await page.goto('/analyze/new')
  await page.locator('#job-url-input').fill('https://careers.coupang.com/jobs/1')
  await expect(page.getByText('쿠팡')).toBeVisible()

  await page.locator('#job-select').selectOption('11')
  await page.locator('#next-step-btn').click()
  await page.getByRole('textbox').fill('제출했던 자기소개서')
  await page.getByRole('button', { name: '다음' }).click()

  await page.getByLabel(/기술면접/).check()
  await page.locator('#submit-analyze-btn').click()

  await expect(page).toHaveURL(/\/analyze\/99$/)
  await expect(page.getByText('역량 분석')).toBeVisible()
  await expect(page.getByText('시스템 설계').first()).toBeVisible()
  await expect(page.getByText('1주차: 시스템 설계 복습')).toBeVisible()
  await expect(page.getByText('타임라인')).toBeVisible()
})

test('analyze flow with manual job text input submits successfully', async ({ page }) => {
  await page.route('**/api/companies/resolve/**', async route => {
    await route.fulfill({
      json: {
        id: 1,
        company_name: '쿠팡',
        industry: 'Commerce',
        size: 'large',
        talent_description: '고객 중심',
        culture_keywords: ['실험', '속도'],
      },
    })
  })
  await page.route('**/api/companies/1/jobs/', async route => {
    await route.fulfill({
      json: [{
        id: 11,
        job_title: '백엔드 개발자',
        interview_stages: [
          { order: 1, type: 'technical', desc: '기술 면접' },
          { order: 2, type: 'personality', desc: '인성 면접' },
        ],
      }],
    })
  })
  await page.route('**/api/analyze/', async route => {
    if (route.request().method() === 'POST') {
      const body = route.request().postDataJSON()
      expect(body.job_posting_text).toBe('이것은 직접 입력한 채용공고 본문 내용입니다.')
      await route.fulfill({ status: 201, json: { id: 99 } })
    } else {
      await route.fallback()
    }
  })
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

  await page.goto('/analyze/new')
  await page.locator('#job-url-input').fill('https://careers.coupang.com/jobs/1')
  await expect(page.getByText('쿠팡')).toBeVisible()

  await page.locator('#job-select').selectOption('11')

  // 직접 공고 내용 입력하기 체크박스 체크
  await page.getByLabel('직접 공고 내용 입력하기').check()

  // job-text-input에 텍스트 입력
  await page.locator('#job-text-input').fill('이것은 직접 입력한 채용공고 본문 내용입니다.')

  await page.locator('#next-step-btn').click()
  await page.getByRole('textbox').fill('제출했던 자기소개서')
  await page.getByRole('button', { name: '다음' }).click()

  await page.getByLabel(/기술면접/).check()
  await page.locator('#submit-analyze-btn').click()

  await expect(page).toHaveURL(/\/analyze\/99$/)
  await expect(page.getByText('역량 분석')).toBeVisible()
})

