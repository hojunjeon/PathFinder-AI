import { expect, test } from '@playwright/test'

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('access', 'e2e-token')
  })
})

function mockProfileApi(page, profile = {}) {
  let savedPayload = null

  return {
    getSavedPayload: () => savedPayload,
    ready: page.route('**/api/profile/', async route => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          json: {
            name: '',
            major: '',
            education: '',
            careers: [],
            projects: [],
            awards: [],
            certificates: [],
            ...profile,
          },
        })
        return
      }

      savedPayload = route.request().postDataJSON()
      await route.fulfill({ status: 200, json: savedPayload })
    }),
  }
}

test('프로필을 불러오고 저장한다', async ({ page }) => {
  await mockProfileApi(page, {
    name: '홍길동',
    major: '컴퓨터공학',
    education: '한국대학교 학사 졸업',
  }).ready

  await page.goto('/profile')
  await expect(page.getByLabel('이름')).toHaveValue('홍길동')

  await page.getByLabel('이름').fill('김철수')
  await page.getByRole('button', { name: '프로필 저장' }).click()

  await expect(page.getByText('저장되었습니다.')).toBeVisible()
})

test('프로필 저장 실패 메시지를 표시한다', async ({ page }) => {
  await page.route('**/api/profile/', async route => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        json: {
          name: '',
          major: '',
          education: '',
          careers: [],
          projects: [],
          awards: [],
          certificates: [],
        },
      })
      return
    }

    await route.fulfill({
      status: 400,
      json: { message: '잘못된 입력 양식입니다.' },
    })
  })

  await page.goto('/profile')
  await page.getByRole('button', { name: '프로필 저장' }).click()

  await expect(page.getByText('잘못된 입력 양식입니다.')).toBeVisible()
})

test('빈 반복 항목을 간단히 추가하고 삭제한다', async ({ page }) => {
  await mockProfileApi(page).ready
  await page.goto('/profile')

  await page.getByRole('button', { name: '+ 경력 추가' }).click()
  await expect(page.getByLabel('회사명')).toBeVisible()
  await page.getByLabel('회사명').fill('테스트 회사')
  await expect(page.getByText('테스트 회사')).toBeVisible()

  await page.getByRole('button', { name: '경력 1 삭제' }).click()
  await expect(page.getByLabel('회사명')).toHaveCount(0)
})

test('경력과 프로젝트는 분석에 필요한 필드만 입력하고 저장한다', async ({ page }) => {
  const api = mockProfileApi(page, {
    careers: [{
      company: '기존 회사',
      title: '백엔드 개발자',
      employment_type: '정규직',
      start_date: '2024-01-01',
      end_date: '2025-01-01',
      current: false,
      period: '2024-01-01 ~ 2025-01-01',
      description: '기존 주요 업무',
    }],
    projects: [{
      name: '기존 프로젝트',
      role: 'API 개발',
      stack: 'Django',
      start_date: '2025-01-01',
      end_date: '2025-03-01',
      period: '2025-01-01 ~ 2025-03-01',
      description: '기존 설명',
      result: '응답 속도 개선',
    }],
  })
  await api.ready

  await page.goto('/profile')

  await expect(page.getByLabel('회사명')).toBeVisible()
  await expect(page.getByLabel('직무')).toBeVisible()
  await expect(page.getByLabel('주요 업무 및 성과')).toBeVisible()
  await expect(page.getByLabel('고용 형태')).toHaveCount(0)
  await expect(page.getByLabel('시작일')).toHaveCount(0)
  await expect(page.getByLabel('종료일')).toHaveCount(0)

  await expect(page.getByLabel('프로젝트명')).toBeVisible()
  await expect(page.getByLabel('역할')).toBeVisible()
  await expect(page.getByLabel('기술 스택')).toBeVisible()
  await expect(page.getByLabel('프로젝트 설명')).toBeVisible()
  await expect(page.getByLabel('결과 및 성과')).toBeVisible()

  await page.getByRole('button', { name: '프로필 저장' }).click()

  expect(api.getSavedPayload().careers).toEqual([{
    company: '기존 회사',
    title: '백엔드 개발자',
    description: '기존 주요 업무',
  }])
  expect(api.getSavedPayload().projects).toEqual([{
    name: '기존 프로젝트',
    role: 'API 개발',
    stack: 'Django',
    description: '기존 설명',
    result: '응답 속도 개선',
  }])
})

test('자격증과 수상내역은 간단한 필드만 입력하고 저장한다', async ({ page }) => {
  const api = mockProfileApi(page, {
    certificates: [{
      name: '정보처리기사',
      issuer: '한국산업인력공단',
      acquired_date: '2025-06-01',
      credential_id: '1234',
    }],
    awards: [{
      title: '프로젝트 우수상',
      issuer: 'SSAFY',
      award_date: '2025-12-15',
      description: 'API 설계와 배포를 담당했습니다.',
    }],
  })
  await api.ready

  await page.goto('/profile')

  await expect(page.getByLabel('자격증명')).toHaveValue('정보처리기사')
  await expect(page.getByLabel('주관 기관')).toHaveCount(0)
  await expect(page.getByLabel('취득일')).toHaveCount(0)
  await expect(page.getByLabel('등록번호')).toHaveCount(0)

  await expect(page.getByLabel('수상명')).toHaveValue('프로젝트 우수상')
  await expect(page.getByLabel('수상 설명')).toHaveValue('API 설계와 배포를 담당했습니다.')
  await expect(page.getByLabel('수상일')).toHaveCount(0)

  await page.getByRole('button', { name: '프로필 저장' }).click()

  expect(api.getSavedPayload().certificates).toEqual([{ name: '정보처리기사' }])
  expect(api.getSavedPayload().awards).toEqual([{
    title: '프로젝트 우수상',
    description: 'API 설계와 배포를 담당했습니다.',
  }])
})
