import { execFileSync, spawn } from 'node:child_process'
import { createRequire } from 'node:module'
import { mkdir, writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'

const evidenceDir = new URL('./evidence/', import.meta.url)
const require = createRequire(new URL('../../../frontend/package.json', import.meta.url))
const { chromium } = require('@playwright/test')
const baseUrl = 'http://127.0.0.1:5173'
const log = []

const server = spawn('npx', ['vite', '--host', '127.0.0.1', '--port', '5173', '--strictPort'], {
  cwd: new URL('../../../frontend/', import.meta.url),
  shell: true,
  stdio: ['ignore', 'pipe', 'pipe'],
})

server.stdout.on('data', data => log.push(`[vite] ${data}`))
server.stderr.on('data', data => log.push(`[vite:err] ${data}`))

try {
  await waitForServer(`${baseUrl}/analyze/99`)
  const browser = await chromium.launch({ channel: 'chrome' })
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } })
  const page = await context.newPage()
  await page.addInitScript(() => localStorage.setItem('access', 'qa-token'))
  await page.route('**/api/analyze/99/', route => route.fulfill({ json: structuredAnalysis() }))
  await page.route('**/api/analyze/100/', route => route.fulfill({ json: rawFallbackAnalysis() }))

  await page.goto(`${baseUrl}/analyze/99`)
  await page.getByRole('heading', { name: /역량 지도 .*액션 플래너/ }).waitFor()
  await page.getByRole('link', { name: /준비 항목/ }).click()
  await expectHash(page, '#sprint-title')
  await page.screenshot({ path: evidencePath('C002-result-desktop.png'), fullPage: true })
  await page.setViewportSize({ width: 768, height: 900 })
  await page.screenshot({ path: evidencePath('C002-result-tablet.png'), fullPage: true })
  await page.setViewportSize({ width: 375, height: 812 })
  await page.screenshot({ path: evidencePath('C002-result-mobile.png'), fullPage: true })
  await page.setViewportSize({ width: 1280, height: 900 })

  await page.getByRole('button', { name: '제출 자기소개서 확인' }).click()
  const dialog = page.getByRole('dialog', { name: '제출 자기소개서' })
  await dialog.waitFor()
  await dialog.getByRole('heading', { name: '지원동기' }).waitFor()
  const content = dialog.locator('.cover-letter-content')
  const scrollState = await content.evaluate(el => ({ clientHeight: el.clientHeight, scrollHeight: el.scrollHeight }))
  if (scrollState.scrollHeight <= scrollState.clientHeight) throw new Error('structured modal did not create internal scroll')
  await content.evaluate(el => el.scrollTo(0, el.scrollHeight))
  await dialog.locator('.cover-letter-item').last().waitFor()
  await page.screenshot({ path: evidencePath('C002-cover-letter-dialog.png'), fullPage: true })
  await dialog.getByRole('button', { name: '자기소개서 닫기' }).click()
  await page.getByRole('button', { name: '제출 자기소개서 확인' }).waitFor()

  await page.goto(`${baseUrl}/analyze/100`)
  await page.getByRole('button', { name: '제출 자기소개서 확인' }).click()
  const rawDialog = page.getByRole('dialog', { name: '제출 자기소개서' })
  await rawDialog.locator('.cover-letter-raw').waitFor()
  const rawText = await rawDialog.locator('.cover-letter-raw').innerText()
  if (!rawText.includes('legacy raw answer')) throw new Error('raw fallback text was not rendered')
  await page.screenshot({ path: evidencePath('C004-raw-fallback-dialog.png'), fullPage: true })

  await browser.close()
  log.push('PASS: sidebar hash navigation, structured modal scroll, close/focus path, and raw fallback rendered.')
} finally {
  stopServer()
  await mkdir(evidenceDir, { recursive: true })
  await writeFile(new URL('C002-browser-analyze-flow.txt', evidenceDir), log.join('\n'))
}

async function waitForServer(url) {
  for (let attempt = 0; attempt < 80; attempt += 1) {
    try {
      const res = await fetch(url)
      if (res.status < 500) return
    } catch {
      await new Promise(resolve => setTimeout(resolve, 250))
    }
  }
  throw new Error('vite server did not start')
}

function evidencePath(name) {
  return fileURLToPath(new URL(name, evidenceDir))
}

function stopServer() {
  if (!server.pid) return
  try {
    execFileSync('taskkill', ['/PID', String(server.pid), '/T', '/F'], { stdio: 'ignore' })
    log.push(`cleanup: stopped QA Vite process tree ${server.pid}`)
  } catch (error) {
    server.kill()
    log.push(`cleanup: server.kill fallback for ${server.pid}`)
  }
}

async function expectHash(page, hash) {
  for (let attempt = 0; attempt < 20; attempt += 1) {
    if (new URL(page.url()).hash === hash) return
    await page.waitForTimeout(100)
  }
  throw new Error(`expected hash ${hash}, got ${new URL(page.url()).hash}`)
}

function structuredAnalysis() {
  return {
    id: 99,
    company_name: '쿠팡',
    job_title: '백엔드 개발자',
    selected_interview_types: ['technical'],
    submitted_cover_letter: 'Q. 지원동기\nA. 제출했던 자기소개서 답변',
    submitted_cover_letter_items: [
      { question: '지원동기', answer: longText('제출했던 자기소개서 답변') },
      { question: '직무 역량', answer: longText('API와 DB 최적화 경험이 있습니다.') },
      { question: '성장 과정', answer: longText('자기소개서 마지막 답변입니다.') },
    ],
    competency_gap: {
      summary: 'API 개선 경험은 강점이고 시스템 설계 지식은 우선 보완이 필요합니다.',
      competency_map: [
        mapItem('API 성능 개선', 'strength', 88, 92),
        mapItem('기술 선택 근거', 'articulate', 58, 84),
        mapItem('시스템 설계', 'study', 24, 70),
      ],
    },
    timeline_data: timelineData(),
    status: 'done',
    created_at: '2026-06-05T00:00:00Z',
  }
}

function rawFallbackAnalysis() {
  return {
    ...structuredAnalysis(),
    id: 100,
    submitted_cover_letter_items: [],
    submitted_cover_letter: 'Q. legacy\nA. legacy raw answer',
  }
}

function mapItem(keyword, status, radar_score, job_score) {
  return {
    keyword,
    status,
    importance: 'required',
    signal: `${keyword} 근거`,
    action: `${keyword} 답변 정리`,
    radar_score,
    job_score,
    score_rationale: {
      my_reason: `${keyword} 현재 역량 근거입니다.`,
      job_reason: `${keyword} 기업 요구 근거입니다.`,
    },
  }
}

function timelineData() {
  return [{
    category: '로보틱스',
    priority: 1,
    subtopics: [{
      title: '역기구학',
      questions: [{
        type: 'concept',
        question: '순기구학과 역기구학의 차이는 무엇인가요?',
        answer_guide: '입력과 출력, 사용 목적을 비교하세요.',
        follow_up_questions: [],
      }],
    }],
  }]
}

function longText(seed) {
  return Array.from({ length: 12 }, (_, index) => `${seed} ${index + 1}`).join('\n')
}
