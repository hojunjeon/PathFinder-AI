import { expect, test } from '@playwright/test'

test('signup stays on the login page and asks only for account fields', async ({ page }) => {
  await page.goto('/login')
  await page.locator('#tab-signup').click()

  await expect(page).toHaveURL(/\/login$/)
  await expect(page.locator('#name')).toBeVisible()
  await expect(page.locator('#email')).toBeVisible()
  await expect(page.locator('#password')).toBeVisible()
  await expect(page.locator('#password-confirm')).toBeVisible()
  await expect(page.getByLabel('전공')).toHaveCount(0)
  await expect(page.getByLabel('학력')).toHaveCount(0)
})

test('signup sends account data and redirects after success', async ({ page }) => {
  let signupRequest
  await page.route('**/api/auth/signup/', async route => {
    signupRequest = route.request().postDataJSON()
    await route.fulfill({
      status: 201,
      json: { access: 'signup-access', refresh: 'signup-refresh' },
    })
  })

  await page.goto('/login')
  await page.locator('#tab-signup').click()
  await page.locator('#name').fill('홍길동')
  await page.locator('#email').fill('new@example.com')
  await page.locator('#password').fill('password123!')
  await page.locator('#password-confirm').fill('password123!')
  await page.locator('#submit-btn').click()

  await expect(page).toHaveURL(/\/$/)
  expect(signupRequest).toEqual({
    name: '홍길동',
    email: 'new@example.com',
    password: 'password123!',
    password_confirm: 'password123!',
  })
})

test('signup blocks mismatched passwords before calling the API', async ({ page }) => {
  let requestCount = 0
  await page.route('**/api/auth/signup/', async route => {
    requestCount += 1
    await route.abort()
  })

  await page.goto('/login')
  await page.locator('#tab-signup').click()
  await page.locator('#name').fill('홍길동')
  await page.locator('#email').fill('new@example.com')
  await page.locator('#password').fill('password123!')
  await page.locator('#password-confirm').fill('different123!')
  await page.locator('#submit-btn').click()

  await expect(page.getByText('비밀번호가 일치하지 않습니다.')).toBeVisible()
  expect(requestCount).toBe(0)
})
