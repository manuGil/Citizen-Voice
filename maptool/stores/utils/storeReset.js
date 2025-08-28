import { useResponseStore } from '~/stores/response';
import { useSurveyStore } from '~/stores/survey';
import { useMapViewStore } from '~/stores/mapview';
import { useAnswerMapViewStore } from '~/stores/answerMapview';
// Import other stores as needed

export const resetSurveySession = () => {
    const responseStore = useResponseStore();
    const surveyStore = useSurveyStore();
    const mapViewStore = useMapViewStore();
    const answerMapViewStore = useAnswerMapViewStore();

    // Reset all survey-related stores
    responseStore.$reset();
    surveyStore.$reset();
    mapViewStore.$reset();
    answerMapViewStore.$reset();


    // If you have an answer store
    // const answerStore = useAnswerStore();
    // answerStore.$reset();

    console.log('All survey stores have been reset');
};