import { spawn } from 'node:child_process'
import { writeFile } from 'node:fs/promises'
import playwright from '../../frontend/node_modules/playwright/index.js'

const { chromium } = playwright
const port = Number(process.env.QA_PORT ?? 5297)
const baseUrl = `http://127.0.0.1:${port}`
const frontendCwd = new URL('../../frontend/', import.meta.url)
const forbiddenCopy = '\uC120\uD0DD\uD55C \uD68C\uC0AC\uC5D0 \uC5F0\uACB0\uD560 \uC218 \uC788\uB294 \uAE30\uC900 \uC9C1\uBB34\uAC00 \uC5C6\uC2B5\uB2C8\uB2E4.'
const viewports = [
  { name: 'desktop', width: 1280, height: 900 },
  { name: 'mobile', width: 390, height: 900 },
]

function startVite() {
  return spawn(
    process.platform === 'win32' ? 'cmd.exe' : 'npx',
    process.platform === 'win32'
      ? ['/c', 'npx', 'vite', '--host', '127.0.0.1', '--port', String(port), '--strictPort']
      : ['vite', '--host', '127.0.0.1', '--port', String(port), '--strictPort'],
    { cwd: frontendCwd, stdio: ['ignore', 'pipe', 'pipe'] },
  )
}

async function waitForServer(server) {
  const logs = []
  server.stdout.on('data', chunk => logs.push(chunk.toString()))
  server.stderr.on('data', chunk => logs.push(chunk.toString()))

  const startedAt = Date.now()
  while (Date.now() - startedAt < 30000) {
    try {
      const response = await fetch(baseUrl)
      if (response.ok) {
        return logs
      }
    } catch {
      await new Promise(resolve => setTimeout(resolve, 300))
    }
  }
  throw new Error(`Vite did not start on ${baseUrl}. Logs:\n${logs.join('')}`)
}

async function stopVite(server) {
  if (!server.pid) {
    return 'no pid'
  }
  if (process.platform === 'win32') {
    await new Promise(resolve => {
      const killer = spawn('taskkill', ['/PID', String(server.pid), '/T', '/F'])
      killer.on('close', resolve)
      killer.on('error', resolve)
    })
    return `taskkill /PID ${server.pid} /T /F`
  }
  server.kill('SIGTERM')
  return `SIGTERM ${server.pid}`
}

const server = startVite()
const results = []
let cleanup = 'not attempted'

try {
  const serverLogs = await waitForServer(server)
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
            matched_job: { id: 77, job_title: '우주선 조종사' },
            jobs: [{ id: 77, job_title: '우주선 조종사', interview_stages: [] }],
            jobs_meta: { count: 1, page: 1, page_size: 30 },
          },
        })
      })

      await page.goto(`${baseUrl}/analyze/new`, { waitUntil: 'networkidle' })
      await page.locator('#company-search-input').fill('쿠팡')
      await page.getByRole('option', { name: /쿠팡/ }).click()
      await page.locator('#job-title-input').fill('우주선 조종사')
      await page.locator('#responsibilities-input').fill('서비스 운영 자동화')
      await page.locator('#requirements-input').fill('문제 해결 경험')
      await page.getByLabel(/기술면접/).check()
      await page.locator('#next-step-btn').click()
      await page.locator('.cover-question-input').waitFor({ state: 'visible' })

      const screenshot = `.omo/evidence/roadmap-company-only-visual-${viewport.name}.png`
      await page.screenshot({ path: screenshot, fullPage: true })
      results.push({
        viewport,
        screenshot,
        forbiddenCopyCount: await page.getByText(forbiddenCopy).count(),
        coverLetterVisible: await page.locator('.cover-question-input').isVisible(),
      })
      await page.close()
    }
  } finally {
    await browser.close()
  }

  const report = {
    ok: results.every(result => result.forbiddenCopyCount === 0 && result.coverLetterVisible),
    baseUrl,
    serverLogs,
    results,
  }
  await writeFile('.omo/evidence/roadmap-company-only-visual-qa.json', `${JSON.stringify(report, null, 2)}\n`)
  console.log(JSON.stringify(report, null, 2))
} finally {
  cleanup = await stopVite(server)
  await writeFile('.omo/evidence/roadmap-company-only-visual-cleanup.txt', `${cleanup}\n`)
}
