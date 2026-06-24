import { expect, test } from '@playwright/test'

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('access', 'e2e-token')
  })
})

test('profile loading and successful save', async ({ page }) => {
  await page.route('**/api/profile/', async route => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        json: {
          name: '홍길동',
          major: '컴퓨터공학',
          education: '한국대학교 학사 졸업',
          careers: [],
          projects: [],
          awards: [],
          certificates: [],
        },
      })
    } else if (route.request().method() === 'PUT') {
      await route.fulfill({
        status: 200,
        json: { message: 'saved' },
      })
    }
  })

  await page.goto('/profile')
  await expect(page.locator('input[placeholder="이름"]')).toHaveValue('홍길동')
  await expect(page.getByRole('heading', { name: '자기소개서' })).toHaveCount(0)

  await page.locator('input[placeholder="이름"]').fill('김철수')
  await page.locator('#save-profile-btn').click()

  await expect(page.getByText('저장되었습니다.')).toBeVisible()
})

test('profile save failure displays error message', async ({ page }) => {
  await page.route('**/api/profile/', async route => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        json: {
          name: '홍길동',
          major: '컴퓨터공학',
          education: '한국대학교 학사 졸업',
          careers: [],
          projects: [],
          awards: [],
          certificates: [],
        },
      })
    } else if (route.request().method() === 'PUT') {
      await route.fulfill({
        status: 400,
        json: { message: '잘못된 입력 양식입니다.' },
      })
    }
  })

  await page.goto('/profile')
  await page.locator('#save-profile-btn').click()

  await expect(page.getByText('잘못된 입력 양식입니다.')).toBeVisible()
})

test('profile saves structured certificates and awards without cover letter section', async ({ page }) => {
  let savedPayload = null
  await page.route('**/api/profile/', async route => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        json: {
          name: '',
          major: '',
          education: '',
          careers: [],
          projects: [],
          cover_letters: [{ question: '기존 문항', answer: '기존 답변' }],
          awards: [],
          certificates: [],
        },
      })
    } else if (route.request().method() === 'PUT') {
      savedPayload = route.request().postDataJSON()
      await route.fulfill({
        status: 200,
        json: savedPayload,
      })
    }
  })

  await page.goto('/profile')
  await expect(page.getByRole('heading', { name: '자기소개서' })).toHaveCount(0)

  await page.getByRole('button', { name: '+ 자격증 추가' }).click()
  await page.locator('input[placeholder="예: 정보처리기사"]').fill('정보처리기사')
  await page.locator('input[placeholder="예: 한국산업인력공단"]').fill('한국산업인력공단')
  await page.locator('input[type="date"]').first().fill('2025-06-01')

  await page.getByRole('button', { name: '+ 수상내역 추가' }).click()
  await page.locator('input[placeholder="예: SSAFY 프로젝트 우수상"]').fill('SSAFY 프로젝트 우수상')
  await page.locator('input[placeholder="예: 삼성청년SW아카데미"]').fill('삼성청년SW아카데미')
  await page.locator('input[type="date"]').nth(1).fill('2025-12-15')
  await page.locator('textarea[placeholder="수상 배경, 역할, 평가 기준을 적어 주세요."]').fill('팀 프로젝트에서 API 설계와 배포를 담당했습니다.')

  await page.locator('#save-profile-btn').click()

  expect(savedPayload.certificates).toEqual([
    {
      name: '정보처리기사',
      issuer: '한국산업인력공단',
      acquired_date: '2025-06-01',
      credential_id: '',
    },
  ])
  expect(savedPayload.awards).toEqual([
    {
      title: 'SSAFY 프로젝트 우수상',
      issuer: '삼성청년SW아카데미',
      award_date: '2025-12-15',
      description: '팀 프로젝트에서 API 설계와 배포를 담당했습니다.',
    },
  ])
  expect(savedPayload.cover_letters).toBeUndefined()
})
