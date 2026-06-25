import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'

const root = process.cwd()

const requiredFiles = [
  'src/views/LoginView.vue',
  'src/views/ProfileView.vue',
  'src/views/AnalyzeCreateView.vue',
  'src/views/AnalyzeResultView.vue',
  'src/views/HistoryView.vue',
  'src/views/DashboardView.vue',
  'src/components/profile/ProfileEntryForm.vue',
  'src/components/analyze/StepJobUrl.vue',
  'src/components/analyze/StepCoverLetter.vue',
  'src/components/analyze/StepInterviewType.vue',
  'src/components/result/CompetencyGap.vue',
  'src/components/result/InterviewDrill.vue',
  'src/components/result/PreparationKeywordBoard.vue',
  'src/components/result/RoadmapTimeline.vue',
  'src/composables/useJobsData.js',
  'public/data/jobs_careers.jsonl',
]

for (const file of requiredFiles) {
  assert(existsSync(join(root, file)), `Missing required frontend file: ${file}`)
}

const router = read('src/router/index.js')
for (const route of ['/login', '/profile', '/analyze/new', '/analyze/:id', '/history', '/dashboard']) {
  assert(router.includes(`path: '${route}'`), `Missing route ${route}`)
}

const profile = read('src/views/ProfileView.vue')
assert(profile.includes("api.get('/api/profile/')"), 'ProfileView must use /api/profile/ GET')
assert(profile.includes("api.put('/api/profile/'"), 'ProfileView must use /api/profile/ PUT')
assert(!profile.includes('CoverLetterForm'), 'ProfileView must not edit cover letters')
assert(!profile.includes('cover_letters'), 'ProfileView must not persist cover letters')
assert(profile.includes("key: 'careers'"), 'ProfileView must configure career inputs')
assert(profile.includes("key: 'projects'"), 'ProfileView must configure project inputs')
assert(profile.includes("key: 'certificates'"), 'ProfileView must configure certificate inputs')
assert(profile.includes("key: 'awards'"), 'ProfileView must configure award inputs')
for (const removedField of ['employment_type', 'start_date', 'end_date', 'current', 'credential_id', 'acquired_date', 'award_date', 'issuer']) {
  assert(!profile.includes(removedField), `ProfileView must not persist removed field ${removedField}`)
}

const stepJobUrl = read('src/components/analyze/StepJobUrl.vue')
assert(stepJobUrl.includes('/api/job-postings/manual/'), 'StepJobUrl must save manual postings through backend')
assert(!stepJobUrl.includes("'kakao':"), 'StepJobUrl must not hard-code company URL aliases')

const analyzeCreate = read('src/views/AnalyzeCreateView.vue')
assert(!analyzeCreate.includes("api.put('/api/profile/'"), 'AnalyzeCreateView must not save cover letters through profile API')
assert(!analyzeCreate.includes('job_id:'), 'AnalyzeCreateView must use company_id plus job_posting, not legacy job_id')
assert(analyzeCreate.includes('company_id:'), 'AnalyzeCreateView must submit selected company_id')
assert(analyzeCreate.includes('job_posting:'), 'AnalyzeCreateView must submit structured job_posting')

const result = read('src/views/AnalyzeResultView.vue')
assert(result.includes('CompetencyGap'), 'AnalyzeResultView must render CompetencyGap')
assert(!result.includes('RoadmapTimeline'), 'AnalyzeResultView must not render legacy RoadmapTimeline in v2 result layout')
assert(!result.includes('PreparationKeywordBoard'), 'AnalyzeResultView must not render legacy PreparationKeywordBoard in v2 result layout')
assert(!result.includes('InterviewDrill'), 'AnalyzeResultView must not render legacy InterviewDrill in v2 result layout')
assert(result.includes('result-sidebar'), 'AnalyzeResultView must provide sidebar navigation for the v2 result layout')
assert(result.includes('scrollToSection'), 'AnalyzeResultView sidebar must navigate within the result page')
assert(result.includes('id="summary"'), 'AnalyzeResultView sidebar must expose the summary anchor')
assert(result.includes("{ id: 'gap', label: '역량 분석' }"), 'AnalyzeResultView sidebar must link to the v2 competency analysis section')
assert(result.includes("{ id: 'sprint-title', label: '준비 항목' }"), 'AnalyzeResultView sidebar must link to the v2 preparation section')
assert(result.includes('제출 자기소개서 확인'), 'AnalyzeResultView must offer read-only cover letter review')
assert(result.includes('showModal()'), 'AnalyzeResultView must show the cover letter without route navigation')
assert(!result.includes('자기소개서 입력 화면'), 'AnalyzeResultView must not route users to a new analysis for review')
assert(result.includes('submitted_cover_letter_items'), 'AnalyzeResultView must render stored question and answer fields')
assert(result.includes('analysis.submitted_cover_letter'), 'AnalyzeResultView must retain a legacy raw-text fallback')

const competencyGap = read('src/components/result/CompetencyGap.vue')
assert(competencyGap.includes('역량 지도 &amp; <span>액션 플래너</span>'), 'CompetencyGap must own the v2 result header')
assert(competencyGap.includes('radar_score'), 'CompetencyGap must consume current competency scores')
assert(competencyGap.includes('job_score'), 'CompetencyGap must consume company requirement scores')
assert(competencyGap.includes('score_rationale'), 'CompetencyGap must consume score rationales')
assert(competencyGap.includes('질문 &amp; 답변 전략'), 'CompetencyGap must render the v2 sprint Q&A panel')

const jobsData = read('public/data/jobs_careers.jsonl').trim().split('\n')
assert(jobsData.length > 0, 'jobs_careers.jsonl must not be empty')
JSON.parse(jobsData[0])

function read(file) {
  return readFileSync(join(root, file), 'utf8')
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message)
  }
}

console.log('frontend design verification passed')
