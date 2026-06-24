import { computed, ref, watch } from 'vue'

export function useRoadmapProgress(analysis) {
  const completedTasks = ref({})
  const roadmapItems = computed(() => normalizeRoadmap(analysis.value?.timeline_data || []))
  const storageKey = computed(() => {
    const id = analysis.value?.id
    return id ? `roadmap-progress:${id}` : ''
  })
  const totalTaskCount = computed(() => {
    return roadmapItems.value.reduce((count, category) => {
      return count + category.subtopics.reduce((subCount, subtopic) => subCount + subtopic.questions.length, 0)
    }, 0)
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
    return nextItem.approach || nextItem.answer_guide || nextItem.question || '개인 맞춤 질문의 답변 방향을 정리하세요.'
  })

  function initializeCompletedTasks(timeline) {
    const items = normalizeRoadmap(timeline || [])
    const stored = loadCompletedTasks(storageKey.value, items)
    completedTasks.value = stored || initialCompletedTasks(items)
  }

  function toggleTask({ categoryIdx, subtopicIdx, questionIdx = 0 }) {
    const key = `${categoryIdx}-${subtopicIdx}-${questionIdx}`
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
    category.subtopics.forEach((subtopic, subtopicIdx) => {
      subtopic.questions.forEach((_, questionIdx) => {
        validKeys.add(`${categoryIdx}-${subtopicIdx}-${questionIdx}`)
      })
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
  }).sort((a, b) => a.priority - b.priority)
}

function normalizeCategoryItem(item, itemIdx) {
  return {
    category: item.category || item.title || `${itemIdx + 1}번째 영역`,
    responsibility: item.responsibility || item.summary || '',
    priority: Number.isInteger(Number(item.priority)) ? Number(item.priority) : itemIdx + 1,
    priority_reason: item.priority_reason || item.priorityReason || item.summary || '',
    experience_match: normalizeExperienceMatch(item.experience_match || item.experienceMatch),
    experience_keywords: normalizeStringList(item.experience_keywords || item.experienceKeywords),
    competency_keywords: normalizeStringList(item.competency_keywords || item.competencyKeywords),
    sources: normalizeStringList(item.sources),
    subtopics: item.subtopics.map((subtopic, subtopicIdx) => normalizeSubtopic(subtopic, subtopicIdx)),
  }
}

function normalizeSubtopic(subtopic, subtopicIdx) {
  const title = subtopic.title || subtopic.concept || `항목 ${subtopicIdx + 1}`
  const matchedExperience = Object.prototype.hasOwnProperty.call(subtopic, 'matched_experience')
    ? subtopic.matched_experience
    : subtopic.matchedExperience || subtopic.evidence || ''
  const fallbackQuestion = {
    type: normalizeQuestionType(subtopic.type),
    question: subtopic.question || title,
    answer_guide: subtopic.answer_guide || subtopic.answerGuide || '',
    follow_up_questions: normalizeStringList(subtopic.follow_up_questions),
    done: Boolean(subtopic.done),
    hasDone: Object.prototype.hasOwnProperty.call(subtopic, 'done'),
  }

  const questions = Array.isArray(subtopic.questions) && subtopic.questions.length
    ? subtopic.questions.map((questionItem) => normalizeQuestionItem(questionItem, fallbackQuestion))
    : [fallbackQuestion]

  return {
    title,
    why: subtopic.why || '',
    evidence: subtopic.evidence || '',
    study_goal: subtopic.study_goal || subtopic.studyGoal || '',
    preparation_type: normalizePreparationType(subtopic.preparation_type || subtopic.preparationType),
    job_reason: subtopic.job_reason || subtopic.jobReason || subtopic.why || '',
    matched_experience: matchedExperience || '',
    experience_source: subtopic.experience_source || subtopic.experienceSource || '',
    source_ids: normalizeStringList(subtopic.source_ids || subtopic.sourceIds),
    experience_connection: normalizeExperienceConnection(
      subtopic.experience_connection || subtopic.experienceConnection,
      matchedExperience,
    ),
    study_focus: normalizeStudyFocus(subtopic.study_focus || subtopic.studyFocus),
    preparation_steps: normalizeStringList(
      subtopic.preparation_steps || subtopic.preparationSteps || subtopic.approach
    ),
    approach: subtopic.approach || subtopic.study_goal || subtopic.studyGoal || '',
    questions: questions.filter(item => item.question),
  }
}

function normalizeExperienceMatch(value) {
  return ['direct', 'related', 'none'].includes(value) ? value : 'none'
}

function normalizeExperienceConnection(value, matchedExperience) {
  const connection = value && typeof value === 'object' && !Array.isArray(value) ? value : {}
  return {
    evidence: connection.evidence || matchedExperience || '',
    transferable_point: connection.transferable_point || connection.transferablePoint || '',
    gap: connection.gap || '',
  }
}

function normalizeStudyFocus(value) {
  if (!Array.isArray(value)) return []
  return value.map((item) => {
    if (typeof item === 'string') return { keyword: item.trim(), checkpoint: '' }
    return {
      keyword: String(item?.keyword || item?.title || item?.concept || '').trim(),
      checkpoint: String(item?.checkpoint || item?.goal || item?.description || '').trim(),
    }
  }).filter(item => item.keyword)
}

function normalizePreparationType(value) {
  return ['appeal', 'organize', 'study'].includes(value) ? value : inferPreparationType(value)
}

function inferPreparationType(value) {
  const normalized = String(value || '').toLowerCase()
  if (normalized.includes('강점') || normalized.includes('어필')) return 'appeal'
  if (normalized.includes('보완') || normalized.includes('정리')) return 'organize'
  return 'study'
}

function normalizeQuestionItem(questionItem, fallbackQuestion) {
  if (typeof questionItem === 'string') {
    return {
      type: fallbackQuestion.type,
      question: questionItem,
      answer_guide: fallbackQuestion.answer_guide,
      follow_up_questions: fallbackQuestion.follow_up_questions,
      done: false,
      hasDone: false,
    }
  }

  return {
    type: normalizeQuestionType(questionItem?.type),
    question: questionItem?.question || fallbackQuestion.question,
    answer_guide: questionItem?.answer_guide || questionItem?.answerGuide || fallbackQuestion.answer_guide,
    follow_up_questions: normalizeStringList(questionItem?.follow_up_questions || questionItem?.followUps),
    done: Boolean(questionItem?.done),
    hasDone: Boolean(questionItem && Object.prototype.hasOwnProperty.call(questionItem, 'done')),
  }
}

function normalizeQuestionType(value) {
  return ['concept', 'experience', 'application'].includes(value) ? value : 'concept'
}

function normalizeStringList(value) {
  return Array.isArray(value)
    ? value.map(item => String(item || '').trim()).filter(Boolean)
    : []
}

function normalizeLegacyItem(item, itemIdx) {
  return {
    category: item.title || (item.week ? `${item.week}주차` : `${itemIdx + 1}번째 영역`),
    responsibility: item.summary || '',
    priority: itemIdx + 1,
    priority_reason: '',
    experience_match: 'none',
    experience_keywords: [],
    competency_keywords: [],
    sources: [],
    subtopics: (item.tasks || []).map((task, taskIdx) => ({
      title: task,
      why: '',
      evidence: '',
      study_goal: '',
      source_ids: [],
      preparation_type: 'study',
      job_reason: '',
      matched_experience: '',
      experience_source: '',
      experience_connection: { evidence: '', transferable_point: '', gap: '' },
      study_focus: [],
      preparation_steps: [],
      approach: '',
      questions: [{
        type: 'concept',
        question: String(task),
        answer_guide: '',
        follow_up_questions: [],
        done: false,
        hasDone: false,
      }],
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
      subtopic.questions.forEach((question, questionIdx) => {
        taskList.push({ categoryIdx, subtopicIdx, questionIdx, legacy: subtopic.legacy })
        hasExplicitDone ||= question.hasDone
        if (question.done) completed[`${categoryIdx}-${subtopicIdx}-${questionIdx}`] = true
      })
    })
  })

  if (!hasExplicitDone && taskList.some(task => task.legacy)) {
    const completeCount = Math.round(taskList.length * 0.4)
    taskList.slice(0, completeCount).forEach(task => {
      completed[`${task.categoryIdx}-${task.subtopicIdx}-${task.questionIdx}`] = true
    })
  }

  return completed
}

function findNextIncomplete(roadmapItems, completedTasks) {
  for (let categoryIdx = 0; categoryIdx < roadmapItems.length; categoryIdx++) {
    const category = roadmapItems[categoryIdx]
    for (let subtopicIdx = 0; subtopicIdx < category.subtopics.length; subtopicIdx++) {
      const subtopic = category.subtopics[subtopicIdx]
      for (let questionIdx = 0; questionIdx < subtopic.questions.length; questionIdx++) {
        if (!completedTasks[`${categoryIdx}-${subtopicIdx}-${questionIdx}`]) {
          return {
            category: category.category,
            title: subtopic.title,
            approach: subtopic.approach,
            ...subtopic.questions[questionIdx],
          }
        }
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
