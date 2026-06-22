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
          cover_letters: [],
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
          cover_letters: [],
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
