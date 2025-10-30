import { useSurveyStore } from '~/stores/survey'
import { useGlobalStore } from '~/stores/global'

export default defineNuxtRouteMiddleware(async (to, from) => {
    // Only validate survey routes
    if (!to.path.includes('/survey/')) {
        return
    }

    const surveyStore = useSurveyStore()
    const globalStore = useGlobalStore()
    const surveyId = to.params.id
    const questionIndex = parseInt(to.params.question, 10)

    try {
        // Select the survey in store
        surveyStore.selectSurvey(surveyId)

        // Fetch questions for this survey
        const questions = await surveyStore.getQuestionsOfSurvey()

        // Validate question index is within bounds
        if (!questions || questions.length === 0) {
            // No questions found for this survey
            globalStore.warning('Survey not found or has no questions')
            return navigateTo('/')
        }

        // Check if question index is valid (1-based indexing, so valid range is 1 to length)
        if (questionIndex < 1 || questionIndex > questions.length) {
            // Invalid question number
            globalStore.warning('Question not found in this survey')
            return navigateTo('/')
        }
    } catch (error) {
        console.error('Error validating survey:', error)
        globalStore.warning('Error loading survey. Please try again.')
        return navigateTo('/')
    }
})
