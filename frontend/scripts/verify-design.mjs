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
  'src/components/profile/CareerForm.vue',
  'src/components/profile/ProjectForm.vue',
  'src/components/profile/CoverLetterForm.vue',
  'src/components/analyze/StepJobUrl.vue',
  'src/components/analyze/StepCoverLetter.vue',
  'src/components/analyze/StepInterviewType.vue',
  'src/components/result/CompetencyGap.vue',
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

const stepJobUrl = read('src/components/analyze/StepJobUrl.vue')
assert(stepJobUrl.includes('/api/job-postings/manual/'), 'StepJobUrl must save manual postings through backend')
assert(!stepJobUrl.includes("'kakao':"), 'StepJobUrl must not hard-code company URL aliases')

const analyzeCreate = read('src/views/AnalyzeCreateView.vue')
assert(analyzeCreate.includes("api.put('/api/profile/'"), 'AnalyzeCreateView must save cover letters through profile API')
assert(analyzeCreate.includes('cover_letters'), 'AnalyzeCreateView must pass structured cover letters')

const result = read('src/views/AnalyzeResultView.vue')
assert(result.includes('CompetencyGap'), 'AnalyzeResultView must render CompetencyGap')
assert(result.includes('RoadmapTimeline'), 'AnalyzeResultView must render RoadmapTimeline')

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
