import { spawn } from 'node:child_process'
import { writeFile } from 'node:fs/promises'
import playwright from '../../../frontend/node_modules/playwright/index.js'

const { chromium } = playwright
const port = Number(process.env.QA_PORT ?? 5317)
const baseUrl = `http://127.0.0.1:${port}`
const frontendCwd = new URL('../../../frontend/', import.meta.url)
const viewports = [
  { name: 'desktop', width: 1280, height: 940 },
  { name: 'mobile', width: 390, height: 920 },
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
      if (response.ok) return logs
    } catch {
      await new Promise(resolve => setTimeout(resolve, 300))
    }
  }
  throw new Error(`Vite did not start on ${baseUrl}. Logs:\n${logs.join('')}`)
}

async function launchBrowser() {
  try {
    return {
      browser: await chromium.launch({ channel: 'chrome' }),
      channel: 'chrome',
    }
  } catch {
    return {
      browser: await chromium.launch(),
      channel: 'bundled-chromium',
    }
  }
}

async function stopVite(server) {
  if (!server.pid) return 'no pid'
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

async function mockResult(page) {
  await page.route('**/api/analyze/99/', async route => {
    await route.fulfill({
      json: {
        id: 99,
        company_name: '쿠팡',
        job_title: '백엔드 개발자',
        selected_interview_types: ['technical'],
        competency_gap: {
          summary: 'API 개선 경험은 강점이고 시스템 설계 지식은 우선 보완이 필요합니다.',
          competency_map: [
            {
              keyword: 'API 성능 개선',
              status: 'strength',
              importance: 'required',
              signal: '성능 개선 프로젝트 경험 있음',
              action: '병목 분석 과정을 어필',
            },
            {
              keyword: '시스템 설계',
              status: 'study',
              importance: 'preferred',
              signal: '대규모 설계 경험 근거 없음',
              action: '분산 구조 우선 학습',
            },
          ],
        },
        timeline_data: [
          {
            category: '로보틱스',
            responsibility: '산업용 로봇 제어 알고리즘 개발',
            priority: 1,
            priority_reason: '직접 경험을 회사 업무 언어로 전환하면 면접 어필력이 큽니다.',
            experience_match: 'direct',
            experience_keywords: ['로봇 팔 제어 정확도 개선 경험'],
            competency_keywords: ['역기구학', '제어 검증'],
            sources: ['채용공고', '프로필'],
            subtopics: [
              {
                title: '역기구학',
                preparation_type: 'appeal',
                job_reason: '로봇 제어 업무의 목표 자세 계산과 검증에 쓰입니다.',
                matched_experience: '로봇 팔 제어 정확도 개선 경험',
                experience_connection: {
                  evidence: '로봇 팔 제어 정확도 개선 경험',
                  transferable_point: '산업용 로봇의 목표 자세 계산과 검증으로 연결할 수 있습니다.',
                  gap: '특이점 처리 기준을 보완해야 합니다.',
                },
                study_focus: [{ keyword: 'FK와 IK 차이', checkpoint: '입력과 출력 비교' }],
                preparation_steps: ['프로젝트 흐름 정리', '해법 선택 이유 정리', '오차 검증 수치 연결'],
                questions: [
                  {
                    type: 'experience',
                    question: '프로젝트에서 역기구학을 어떻게 사용했나요?',
                    done: false,
                    answer_guide: 'STAR 순서로 문제, 구현, 검증 수치를 연결하세요.',
                    follow_up_questions: ['실시간성이 깨질 때 fallback은 무엇인가요?'],
                  },
                ],
              },
            ],
          },
        ],
        status: 'done',
        created_at: '2026-06-24T00:00:00Z',
      },
    })
  })
}

const server = startVite()
const results = []
let cleanup = 'not attempted'

try {
  const serverLogs = await waitForServer(server)
  const { browser, channel } = await launchBrowser()
  try {
    for (const viewport of viewports) {
      const page = await browser.newPage({ viewport })
      await page.addInitScript(() => {
        localStorage.setItem('access', 'visual-qa-token')
      })
      await mockResult(page)
      await page.goto(`${baseUrl}/analyze/99`, { waitUntil: 'networkidle' })
      const topScreenshot = `.omo/ulw-loop/evidence/analyze-result-rehearsal-${viewport.name}-top.png`
      await page.screenshot({ path: topScreenshot, fullPage: false })
      await page.locator('#prep-keywords').scrollIntoViewIfNeeded()
      const keywordHeadingVisible = await page.getByRole('heading', { name: '준비 키워드' }).isVisible()
      const majorKeywordVisible = await page.locator('#prep-keywords').getByText('대주제 키워드', { exact: true }).isVisible()
      const minorKeywordVisible = await page.locator('#prep-keywords').getByText('소주제 키워드', { exact: true }).isVisible()
      await page.locator('#interview-drill').scrollIntoViewIfNeeded()
      const drillScreenshot = `.omo/ulw-loop/evidence/analyze-result-rehearsal-${viewport.name}-drill.png`
      await page.screenshot({ path: drillScreenshot, fullPage: false })
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth)
      results.push({
        viewport,
        screenshots: { top: topScreenshot, drill: drillScreenshot },
        browserChannel: channel,
        keywordHeadingVisible,
        majorKeywordVisible,
        minorKeywordVisible,
        headingVisible: await page.getByRole('heading', { name: '질문 리허설' }).isVisible(),
        companyContextVisible: await page.getByText('회사/업무 맥락', { exact: true }).first().isVisible(),
        personalEvidenceVisible: await page.getByText('내 경험 근거', { exact: true }).first().isVisible(),
        followUpVisible: await page.locator('#interview-drill').getByText('실시간성이 깨질 때 fallback은 무엇인가요?').isVisible(),
        horizontalOverflow: overflow,
      })
      await page.close()
    }
  } finally {
    await browser.close()
  }

  const report = {
    ok: results.every(result => (
      result.keywordHeadingVisible
      && result.majorKeywordVisible
      && result.minorKeywordVisible
      && result.headingVisible
      && result.companyContextVisible
      && result.personalEvidenceVisible
      && result.followUpVisible
      && !result.horizontalOverflow
    )),
    baseUrl,
    serverLogs,
    results,
  }
  await writeFile('.omo/ulw-loop/evidence/analyze-result-rehearsal-visual-qa.json', `${JSON.stringify(report, null, 2)}\n`)
  console.log(JSON.stringify(report, null, 2))
  if (!report.ok) process.exitCode = 1
} finally {
  cleanup = await stopVite(server)
  await writeFile('.omo/ulw-loop/evidence/analyze-result-rehearsal-cleanup.txt', `${cleanup}\n`)
}
