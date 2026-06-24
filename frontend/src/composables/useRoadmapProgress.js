import { computed, ref, watch } from 'vue'

export function useRoadmapProgress(analysis) {
  const completedTasks = ref({})
  const roadmapItems = computed(() => normalizeRoadmap(analysis.value?.timeline_data || []))
  const storageKey = computed(() => {
    const id = analysis.value?.id
    return id ? `roadmap-progress:${id}` : ''
  })
  const totalTaskCount = computed(() => {
    return roadmapItems.value.reduce((count, category) => count + category.subtopics.length, 0)
  })
  const completedTaskCount = computed(() => Object.values(completedTasks.value).filter(Boolean).length)
  const progressPercent = computed(() => {
    if (totalTaskCount.value === 0) return 0
    return Math.round((completedTaskCount.value / totalTaskCount.value) * 100)
  })
  const progressRingStyle = computed(() => ({
    background: `conic-gradient(var(--accent) ${progressPercent.value}%, var(--border-soft) 0)`,
  }))
  const progressText = computed(() => progressCopy(progressPercent.value))
  const nextIncompleteSubtopic = computed(() => findNextIncomplete(roadmapItems.value, completedTasks.value))
  const activeItemText = computed(() => {
    const nextItem = nextIncompleteSubtopic.value
    if (!nextItem) return '준비 항목 완료'
    return `${nextItem.category} · ${nextItem.title}`
  })
  const activeItemDesc = computed(() => {
    const nextItem = nextIncompleteSubtopic.value
    if (!nextItem) return '면접 전 최종 점검만 남았습니다.'
    return nextItem.study_goal || nextItem.question || '답변 기준을 정리하세요.'
  })

  function initializeCompletedTasks(timeline) {
    const items = normalizeRoadmap(timeline || [])
    const stored = loadCompletedTasks(storageKey.value, items)
    completedTasks.value = stored || initialCompletedTasks(items)
  }

  function toggleTask({ categoryIdx, subtopicIdx }) {
    const key = `${categoryIdx}-${subtopicIdx}`
    completedTasks.value[key] = !completedTasks.value[key]
  }

  watch(completedTasks, (tasks) => {
    saveCompletedTasks(storageKey.value, tasks, roadmapItems.value)
  }, { deep: true })

  return {
    activeItemDesc,
    activeItemText,
    completedTasks,
    initializeCompletedTasks,
    progressPercent,
    progressRingStyle,
    progressText,
    roadmapItems,
    toggleTask,
  }
}

function loadCompletedTasks(key, items) {
  if (!key) return null
  try {
    const rawValue = localStorage.getItem(key)
    if (!rawValue) return null
    const parsed = JSON.parse(rawValue)
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return null
    return filterCompletedTasks(parsed, items)
  } catch (error) {
    if (error instanceof SyntaxError) {
      localStorage.removeItem(key)
      return null
    }
    if (typeof DOMException !== 'undefined' && error instanceof DOMException) {
      return null
    }
    throw error
  }
}

function saveCompletedTasks(key, tasks, items) {
  if (!key) return
  localStorage.setItem(key, JSON.stringify(filterCompletedTasks(tasks, items)))
}

function filterCompletedTasks(tasks, items) {
  const validKeys = new Set()
  items.forEach((category, categoryIdx) => {
    category.subtopics.forEach((_, subtopicIdx) => {
      validKeys.add(`${categoryIdx}-${subtopicIdx}`)
    })
  })
  return Object.fromEntries(
    Object.entries(tasks).filter(([key, value]) => validKeys.has(key) && Boolean(value))
  )
}

function normalizeRoadmap(timeline = []) {
  return timeline.map((item, itemIdx) => {
    if (Array.isArray(item.subtopics)) return normalizeCategoryItem(item, itemIdx)
    return normalizeLegacyItem(item, itemIdx)
  })
}

function normalizeCategoryItem(item, itemIdx) {
  return {
    category: item.category || item.title || `${itemIdx + 1}번째 영역`,
    summary: item.summary || '',
    sources: Array.isArray(item.sources) ? item.sources : [],
    subtopics: item.subtopics.map((subtopic, subtopicIdx) => ({
      title: subtopic.title || subtopic.concept || `항목 ${subtopicIdx + 1}`,
      done: Boolean(subtopic.done),
      hasDone: Object.prototype.hasOwnProperty.call(subtopic, 'done'),
      why: subtopic.why || '',
      question: subtopic.question || '',
      answer_guide: subtopic.answer_guide || subtopic.answerGuide || '',
      evidence: subtopic.evidence || '',
      study_goal: subtopic.study_goal || subtopic.studyGoal || '',
      follow_up_questions: Array.isArray(subtopic.follow_up_questions) ? subtopic.follow_up_questions : [],
      source_ids: Array.isArray(subtopic.source_ids) ? subtopic.source_ids.filter(Boolean).map(String) : [],
    })),
  }
}

function normalizeLegacyItem(item, itemIdx) {
  return {
    category: item.title || (item.week ? `${item.week}주차` : `${itemIdx + 1}번째 영역`),
    summary: item.summary || '',
    sources: [],
    subtopics: (item.tasks || []).map((task, taskIdx) => ({
      title: task,
      done: false,
      hasDone: false,
      why: '',
      question: String(task),
      answer_guide: '',
      evidence: '',
      study_goal: '',
      follow_up_questions: [],
      legacy: true,
      taskIdx,
    })),
  }
}

function initialCompletedTasks(items) {
  const completed = {}
  const taskList = []
  let hasExplicitDone = false

  items.forEach((category, categoryIdx) => {
    category.subtopics.forEach((subtopic, subtopicIdx) => {
      taskList.push({ categoryIdx, subtopicIdx, legacy: subtopic.legacy })
      hasExplicitDone ||= subtopic.hasDone
      if (subtopic.done) completed[`${categoryIdx}-${subtopicIdx}`] = true
    })
  })

  if (!hasExplicitDone && taskList.some(task => task.legacy)) {
    const completeCount = Math.round(taskList.length * 0.4)
    taskList.slice(0, completeCount).forEach(task => {
      completed[`${task.categoryIdx}-${task.subtopicIdx}`] = true
    })
  }

  return completed
}

function findNextIncomplete(roadmapItems, completedTasks) {
  for (let categoryIdx = 0; categoryIdx < roadmapItems.length; categoryIdx++) {
    const category = roadmapItems[categoryIdx]
    for (let subtopicIdx = 0; subtopicIdx < category.subtopics.length; subtopicIdx++) {
      if (!completedTasks[`${categoryIdx}-${subtopicIdx}`]) {
        return { category: category.category, ...category.subtopics[subtopicIdx] }
      }
    }
  }
  return null
}

function progressCopy(percent) {
  if (percent >= 100) return '모든 항목을 확인했습니다.'
  if (percent >= 60) return '보완 항목을 압축해 정리하는 단계입니다.'
  if (percent >= 40) return '핵심 답변 근거를 먼저 정리했습니다.'
  if (percent >= 20) return '프로젝트 근거를 기술 개념에 연결하고 있습니다.'
  return '체크할 준비 항목을 확인하세요.'
}
