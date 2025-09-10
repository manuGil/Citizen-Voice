import { useResponseStore } from '~/stores/response';
import { useSurveyStore } from '~/stores/survey';
import { useQuestionMapViewStore } from '~/stores/questionMapview';
import { useAnswerMapViewStore } from '~/stores/answerMapview';
// Import other stores as needed

export const resetSurveySession = () => {
    const responseStore = useResponseStore();
    const surveyStore = useSurveyStore();
    const questionMapViewStore = useQuestionMapViewStore();
    const answerMapViewStore = useAnswerMapViewStore();

    console.log('Resetting survey session - clearing all previous answers and survey data');
    
    // Explicitly clear answers first to ensure clean state
    responseStore.clearAnswers();
    
    // Reset all survey-related stores to initial state
    responseStore.$reset();
    surveyStore.$reset();
    questionMapViewStore.$reset();
    answerMapViewStore.$reset();

    console.log('All survey stores have been reset - previous answers cleared');
};

// New utility function for initializing a new survey session
export const initializeSurveySession = async (surveyId) => {
    const responseStore = useResponseStore();
    const surveyStore = useSurveyStore();
    const questionMapViewStore = useQuestionMapViewStore();
    const answerMapViewStore = useAnswerMapViewStore();

    // Reset all stores first
    resetSurveySession();
    
    // Set the current survey
    surveyStore.selectSurvey(surveyId);
    
    console.log(`Survey session initialized for survey ID: ${surveyId}`);
};