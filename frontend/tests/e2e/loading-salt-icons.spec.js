import { expect, test } from '@playwright/test'

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('access', 'e2e-token')
  })
})

test('shows generation loading state and loads SALT png icons', async ({ page }) => {
  await mockAnalyzeFlow(page)
  let releaseAnalyze
  await page.route('**/api/analyze/', async route => {
    await new Promise(resolve => {
      releaseAnalyze = resolve
    })
    await route.fulfill({ status: 201, json: { id: 99 } })
  })

  await fillManualPosting(page)
  await page.locator('#next-step-btn').click()
  await page.locator('.cover-question-input').fill('직무 역량')
  await page.locator('.cover-answer-input').fill('백엔드 API와 DB 최적화 경험이 있습니다.')
  await page.locator('#next-cover-letter-btn').click()

  await expect(page.locator('.loading-spinner')).toBeVisible()
  await expect(page.getByText('로드맵을 생성하고 있습니다')).toBeVisible()

  releaseAnalyze()
  await page.waitForURL('**/analyze/99')
  const icons = page.locator('.stat-icon img')
  await expect(icons).toHaveCount(4)
  await expect(icons.nth(0)).toHaveAttribute('src', /S\.png/)
  await expect(icons.nth(1)).toHaveAttribute('src', /A\.png/)
  await expect(icons.nth(2)).toHaveAttribute('src', /L\.png/)
  await expect(icons.nth(3)).toHaveAttribute('src', /T\.png/)
  await expect.poll(() => icons.evaluateAll(images => (
    images.every(image => image.complete && image.naturalWidth > 0)
  ))).toBe(true)
})

async function mockAnalyzeFlow(page) {
  await page.route('**/api/companies/?name=*', route => route.fulfill({
    status: 200,
    json: [{ id: 1, company_name: '쿠팡', industry: 'Commerce', size: 'large', roadmap_supported: true }],
  }))
  await page.route('**/api/job-postings/manual/**', route => route.fulfill({
    status: 201,
    json: {
      supported: true,
      company: { id: 1, company_name: '쿠팡', industry: 'Commerce', size: 'large' },
      job_posting: { id: 7, resolved: true },
      matched_job: { id: 11, job_title: '백엔드 개발자' },
      jobs: [{ id: 11, job_title: '백엔드 개발자', interview_stages: [] }],
      jobs_meta: { count: 1, page: 1, page_size: 30 },
    },
  }))
  await page.route('**/api/analyze/99/', route => route.fulfill({
    json: {
      id: 99,
      company_name: '쿠팡',
      job_title: '백엔드 개발자',
      competency_gap: {
        competency_map: [
          competency('API 성능 개선', 'strength', 88, 92),
          competency('기술 선택 근거', 'articulate', 58, 84),
          competency('시스템 설계', 'study', 24, 70),
        ],
      },
      timeline_data: [],
      status: 'done',
    },
  }))
}

async function fillManualPosting(page) {
  await page.goto('/analyze/new')
  await page.locator('#company-search-input').fill('쿠팡')
  await page.getByRole('option', { name: /쿠팡/ }).click()
  await page.locator('#job-title-input').fill('백엔드 개발자')
  await page.locator('#responsibilities-input').fill('주문/배송 API 개발과 대규모 트래픽 처리')
  await page.locator('#requirements-input').fill('Python, Database, REST API 경험')
  await page.getByLabel(/기술면접/).check()
}

function competency(keyword, status, radarScore, jobScore) {
  return {
    keyword,
    status,
    importance: 'required',
    signal: '테스트 근거',
    action: '테스트 액션',
    radar_score: radarScore,
    job_score: jobScore,
    score_rationale: { my_reason: '내 역량 근거', job_reason: '기업 요구 근거' },
  }
}
