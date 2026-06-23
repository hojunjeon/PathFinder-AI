import playwright from '../../frontend/node_modules/playwright/index.js'

const { chromium } = playwright

const baseUrl = process.env.QA_BASE_URL ?? 'http://127.0.0.1:5174'
const viewports = [
  { name: 'desktop', width: 1280, height: 900 },
  { name: 'mobile', width: 390, height: 900 },
]

const results = []

const browser = await chromium.launch()
try {
  for (const viewport of viewports) {
    const page = await browser.newPage({ viewport })
    await page.addInitScript(() => {
      localStorage.setItem('access', 'visual-qa-token')
    })
    await page.route('**/api/companies/?name=*', async route => {
      await route.fulfill({
        status: 200,
        json: [{
          id: 1,
          company_name: '쿠팡',
          industry: 'Commerce',
          size: 'large',
          talent_description: '고객 중심',
          culture_keywords: ['실험', '속도'],
          roadmap_supported: true,
        }],
      })
    })
    await page.goto(`${baseUrl}/analyze/new`, { waitUntil: 'networkidle' })
    await page.locator('#company-search-input').fill('쿠팡')
    await page.getByRole('option', { name: /쿠팡/ }).waitFor()
    const matchButtonCount = await page.locator('#match-job-btn').count()
    const screenshot = `.omo/evidence/roadmap-button-visual-${viewport.name}.png`
    await page.screenshot({ path: screenshot, fullPage: true })
    results.push({
      viewport,
      matchButtonCount,
      screenshot,
      hasCompanyDropdown: await page.getByRole('option', { name: /쿠팡/ }).isVisible(),
    })
    await page.close()
  }
} finally {
  await browser.close()
}

console.log(JSON.stringify({ ok: results.every(result => result.matchButtonCount === 0 && result.hasCompanyDropdown), results }, null, 2))
