import { expect, test } from '@playwright/test'

test('first visit opens the main page with login CTA', async ({ page }) => {
  await page.goto('/')

  await expect(page).toHaveURL(/\/$/)
  await expect(page.getByRole('heading', { name: '지원 공고를 면접 준비 로드맵으로 바꿔드립니다.' })).toBeVisible()
  await expect(page.getByRole('link', { name: '로그인하고 시작하기' })).toBeVisible()
  await expect(page.getByText('처음이라면 이 순서대로 진행하세요.')).toBeVisible()
})

test('logged-in users still land on the main page and use buttons for features', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('access', 'e2e-token')
  })

  await page.goto('/')

  await expect(page).toHaveURL(/\/$/)
  await expect(page.getByRole('link', { name: '로드맵 생성하기' }).first()).toBeVisible()
  await expect(page.getByRole('link', { name: '내 프로필 정리하기' })).toBeVisible()
  await expect(page.getByRole('link', { name: '이전 로드맵 보기' })).toBeVisible()
})

test('login success redirects to the main page instead of roadmap creation', async ({ page }) => {
  await page.route('**/api/auth/login/', async route => {
    await route.fulfill({
      status: 200,
      json: { access: 'e2e-access', refresh: 'e2e-refresh' },
    })
  })

  await page.goto('/login')
  await page.locator('#email').fill('user@example.com')
  await page.locator('#password').fill('password123')
  await page.locator('#submit-btn').click()

  await expect(page).toHaveURL(/\/$/)
  await expect(page.getByRole('link', { name: '로드맵 생성하기' }).first()).toBeVisible()
})

test('signup collects only account data and required agreements', async ({ page }) => {
  let signupPayload = null
  await page.route('**/api/auth/signup/', async route => {
    signupPayload = route.request().postDataJSON()
    await route.fulfill({
      status: 201,
      json: { access: 'e2e-access', refresh: 'e2e-refresh' },
    })
  })

  await page.goto('/login')
  await page.locator('#tab-signup').click()

  await expect(page.getByText('이력은 가입 후 프로필에서 작성할 수 있어요.')).toBeVisible()
  await page.locator('#name').fill('홍길동')
  await page.locator('#email').fill('USER@example.com')
  await page.locator('#password').fill('password123!')
  await page.locator('#password-confirm').fill('password123!')
  await page.getByLabel('필수 항목 모두 동의').check()
  await page.locator('#submit-btn').click()

  await expect(page).toHaveURL(/\/$/)
  expect(signupPayload).toEqual({
    email: 'USER@example.com',
    name: '홍길동',
    password: 'password123!',
    password_confirm: 'password123!',
    terms_agreed: true,
    privacy_agreed: true,
  })
  expect(signupPayload).not.toHaveProperty('major')
  expect(signupPayload).not.toHaveProperty('careers')
})
