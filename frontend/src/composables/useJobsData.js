import { ref, reactive, computed, onMounted } from 'vue'

export function useJobsData() {
  const allRecords = ref([])
  const loading = ref(true)

  const filters = reactive({
    industries: [],
    expRange: [0, 12],
    company: '',
  })

  onMounted(async () => {
    const text = await fetch('/data/jobs_careers.jsonl').then(r => r.text())
    allRecords.value = text.trim().split('\n').map(line => JSON.parse(line))
    loading.value = false
  })

  const filteredRecords = computed(() =>
    allRecords.value.filter(r => {
      const industryOk = filters.industries.length === 0 || filters.industries.includes(r.industry)
      const expOk = r.required_experience_years >= filters.expRange[0]
        && r.required_experience_years <= filters.expRange[1]
      const companyOk = !filters.company || r.company_name.includes(filters.company)
      return industryOk && expOk && companyOk
    })
  )

  const allIndustries = computed(() => [...new Set(allRecords.value.map(r => r.industry))].sort())

  const summaryStats = computed(() => {
    const records = filteredRecords.value
    if (!records.length) return { total: 0, avgApplicants: 0, topJob: '-' }
    const avgApplicants = Math.round(records.reduce((s, r) => s + r.applicant_count, 0) / records.length)
    const jobMap = {}
    records.forEach(r => {
      jobMap[r.job_title] = (jobMap[r.job_title] || 0) + r.applicant_count
    })
    const topJob = Object.entries(jobMap).sort((a, b) => b[1] - a[1])[0]?.[0] || '-'
    return { total: records.length, avgApplicants, topJob }
  })

  // 차트 A: 산업별 평균 연봉 vs 평균 지원자 수
  const industryChartData = computed(() => {
    const byIndustry = {}
    filteredRecords.value.forEach(r => {
      if (!byIndustry[r.industry]) byIndustry[r.industry] = { salarySum: 0, applicantSum: 0, count: 0 }
      byIndustry[r.industry].salarySum += r.annual_salary_krw
      byIndustry[r.industry].applicantSum += r.applicant_count
      byIndustry[r.industry].count++
    })
    const industries = Object.keys(byIndustry).sort()
    return {
      labels: industries,
      salaries: industries.map(i => Math.round(byIndustry[i].salarySum / byIndustry[i].count / 10000)),
      applicants: industries.map(i => (byIndustry[i].applicantSum / byIndustry[i].count).toFixed(1)),
    }
  })

  // 차트 B: 직무 레벨별 평균 지원자 수
  const levelChartData = computed(() => {
    const levels = ['신입', '주니어', '리드', '시니어', '수석', '전문']
    const levelGroups = {}
    filteredRecords.value.forEach(r => {
      const level = levels.find(lv => r.job_title.startsWith(lv)) || '기타'
      if (!levelGroups[level]) levelGroups[level] = []
      levelGroups[level].push(r.applicant_count)
    })
    const validLevels = levels.filter(lv => levelGroups[lv]?.length)
    return {
      labels: validLevels,
      data: validLevels.map(lv =>
        Math.round(levelGroups[lv].reduce((a, b) => a + b, 0) / levelGroups[lv].length)
      ),
    }
  })

  // 차트 C: 경력 연수별 평균 지원자 수
  const expChartData = computed(() => {
    const byExp = {}
    filteredRecords.value.forEach(r => {
      const exp = r.required_experience_years
      if (!byExp[exp]) byExp[exp] = []
      byExp[exp].push(r.applicant_count)
    })
    const expLabels = Object.keys(byExp).sort((a, b) => a - b)
    return {
      labels: expLabels.map(e => `${e}년`),
      data: expLabels.map(e => (byExp[e].reduce((a, b) => a + b, 0) / byExp[e].length).toFixed(1)),
    }
  })

  // 차트 D: 연봉 구간별 분포
  const salaryDistData = computed(() => {
    const bins = [0, 4000, 6000, 8000, 10000, 12000, 15000, 20000]
    const labels = ['~4천만', '4~6천만', '6~8천만', '8천만~1억', '1~1.2억', '1.2~1.5억', '1.5억+']
    const counts = new Array(bins.length - 1).fill(0)
    filteredRecords.value.forEach(r => {
      const man = r.annual_salary_krw / 10000
      for (let i = 0; i < bins.length - 1; i++) {
        if (man >= bins[i] && man < bins[i + 1]) { counts[i]++; break }
      }
    })
    return { labels, data: counts }
  })

  return {
    loading, filters, allIndustries, summaryStats,
    industryChartData, levelChartData, expChartData, salaryDistData,
  }
}
