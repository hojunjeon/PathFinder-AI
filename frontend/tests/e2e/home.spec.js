import { expect, test } from '@playwright/test'

test('first visit opens the Pathi reference home with connected CTAs', async ({ page }) => {
  await page.goto('/')

  await expect(page).toHaveURL(/\/$/)
  await expect(page.getByRole('heading', { name: /Pathi와 함께라면/ })).toBeVisible()
  await expect(page.getByAltText(/Pathi가 채용공고/)).toBeVisible()
  await expect(page.getByRole('heading', { name: '이용 방법' })).toBeVisible()
  await expect(page.getByRole('heading', { name: '분석 결과 미리보기' })).toBeVisible()

  const nav = page.getByRole('navigation', { name: '주요 메뉴' })
  await expect(nav.getByRole('link', { name: '서비스 소개', exact: true })).toHaveAttribute('href', '/#features')
  await expect(nav.getByRole('link', { name: '기능', exact: true })).toHaveAttribute('href', '/#features')
  await expect(nav.getByRole('link', { name: '이용 방법', exact: true })).toHaveAttribute('href', '/#how')
  await expect(nav.getByRole('link', { name: '커뮤니티', exact: true })).toHaveAttribute('href', '/community')
  await expect(nav.getByRole('link', { name: '대시보드', exact: true })).toHaveAttribute('href', '/dashboard')
  await expect(nav.getByRole('link', { name: '로그인', exact: true })).toHaveAttribute('href', '/login')
  await expect(nav.getByRole('link', { name: '회원가입', exact: true })).toHaveAttribute('href', '/login?mode=signup')

  await expect(page.getByRole('link', { name: /분석 시작하기/ }).first()).toHaveAttribute('href', '/analyze/new')
  await expect(page.getByRole('link', { name: '서비스 소개 보기' })).toHaveAttribute('href', '/#features')
  await expect(page.getByRole('link', { name: /질문·답변 전체 보기/ })).toHaveAttribute('href', '/analyze/new')
})

test('logged-in users still land on the main page and use buttons for features', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('access', 'e2e-token')
  })
  await page.route('**/api/profile/', async route => {
    await route.fulfill({
      status: 200,
      json: {
        name: '홍길동',
        email: 'user@example.com',
      },
    })
  })

  await page.goto('/')

  await expect(page).toHaveURL(/\/$/)
  await expect(page.getByRole('navigation', { name: '주요 메뉴' }).getByRole('link', { name: '홈', exact: true })).toBeVisible()
  const account = page.getByRole('link', { name: '현재 로그인 계정 프로필' })
  await expect(account).toContainText('로그인 계정')
  await expect(account).toContainText('홍길동')
  await expect(account).toContainText('user@example.com')
  await expect(page.getByRole('link', { name: /분석 시작하기/ }).first()).toHaveAttribute('href', '/analyze/new')
  await expect(page.getByRole('link', { name: '무료로 분석 시작하기' })).toHaveAttribute('href', '/analyze/new')
})

test('login success redirects to the main page instead of roadmap creation', async ({ page }) => {
  await page.route('**/api/auth/login/', async route => {
    await route.fulfill({
      status: 200,
      json: { access: 'e2e-access', refresh: 'e2e-refresh' },
    })
  })
  await page.route('**/api/profile/', async route => {
    await route.fulfill({
      status: 200,
      json: {
        name: '김패스',
        email: 'user@example.com',
      },
    })
  })

  await page.goto('/login')
  await page.locator('#email').fill('user@example.com')
  await page.locator('#password').fill('password123')
  await page.locator('#submit-btn').click()

  await expect(page).toHaveURL(/\/$/)
  const account = page.getByRole('link', { name: '현재 로그인 계정 프로필' })
  await expect(account).toContainText('김패스')
  await expect(account).toContainText('user@example.com')
  await expect(page.getByRole('link', { name: /분석 시작하기/ }).first()).toHaveAttribute('href', '/analyze/new')
})

test('signup collects only account data and required agreements', async ({ page }) => {
  const pageErrors = []
  page.on('pageerror', error => pageErrors.push(error.message))
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
  expect(pageErrors).toEqual([])
})
