import { expect, test } from '@playwright/test'

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('access', 'e2e-token')
  })
})

test('dashboard loads data, renders charts, filters, toggles dark mode, and exposes png download', async ({ page }) => {
  await page.goto('/dashboard')

  await expect(page.getByText('한국 채용시장 경쟁률 분석')).toBeVisible()
  await expect(page.getByText('전체 공고 수')).toBeVisible()
  await expect(page.locator('canvas')).toHaveCount(4)
  await expect(page.getByRole('button', { name: /PNG/ })).toHaveCount(4)

  const firstTotal = await page.locator('.stat-value').first().textContent()
  await page.locator('.chip').first().click()
  await expect(page.locator('.stat-value').first()).not.toHaveText(firstTotal)

  const downloadPromise = page.waitForEvent('download')
  await page.locator('#download-chart-a').click()
  const download = await downloadPromise
  expect(download.suggestedFilename()).toBe('industry-salary-chart.png')

  await page.getByRole('button', { name: '🌙' }).click()
  await expect(page.locator('.app-shell')).toHaveClass(/dark/)
})
