<template>
    <NuxtLayout name="default">
        <div class="">
            <!-- Question card: number & text -->
            <v-card class="my-card">
            <template v-slot:title>
                    <div class="title-wrapper" style="white-space: normal;">
                        {{ question.text }}
                        <span v-if="question.required" class="required-indicator">*</span>
                        <span v-else class="optional-indicator">(optional)</span>
                    </div>
            </template>
            <template v-slot:subtitle>
                    <div class="title-wrapper" style="white-space: normal;">
                        {{ question.explanation}}
                    </div>
            </template>
                <!-- Answer card-->
                <div v-if="question.has_text_input" class="my-card col">
                    <RespondentViewQuestionTypesAnswerTypeLongText 
                    v-if="question.question_type === 'text'"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                    />
                    <RespondentViewQuestionTypesAnswerTypeShortText 
                    v-if="question.question_type === 'short-text'"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                    />
                    <RespondentViewQuestionTypesAnswerTypeSelect
                    v-if="question.question_type === 'radio'"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                    />
                    <RespondentViewQuestionTypesAnswerTypeMultiselect
                     v-if="question.question_type === 'select-multiple'"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                     />
                    <RespondentViewQuestionTypesAnswerTypeDate 
                    v-if="question.question_type === 'date'"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                    />
                    <RespondentViewQuestionTypesAnswerTypeInteger 
                    v-if="(question.question_type === 'integer' || 
                        question.question_type === 'float')" 
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                    />
                    <RespondentViewQuestionTypesAnswerTypeUploadImage
                    v-if="question.question_type === 'image-upload'"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                    />
                    <RespondentViewQuestionTypesAnswerTypeLikertScale
                    v-if="question.question_type === 'likert-scale'"
                    :question="question"
                    :answer="current_answer"
                    :question_index="current_question_index"
                    @update-answer="handleUpdateAnswer"
                    />
                </div>

                <div class="q-pa-md row items-start q-gutter-md">
                    <!-- Map card -->
                    <div v-if="(question.mapview != null )" style="min-width: 600px;"
                        class="my-card col">
                        <MapView
                        :mapViewUrl ="question.mapview" 
                        />
                    </div>
                    <!-- Navigation -->
                    <v-card-actions>
                        <v-btn v-show="current_question_index > 1" @click="prevQuestion" color="primary" variant="outlined">
                            <i class="fa-solid fa-arrow-left"></i>
                            <span class="q-pa-sm">Previous Question</span>
                        </v-btn>
                        <v-btn v-show="survey_store.questionCount != current_question_index" @click="nextQuestion" color="primary" variant="outlined">
                            <i class="fa-solid fa-arrow-right"></i>
                            <span class="q-pa-sm">Next Question</span>
                        </v-btn>
                                <v-btn v-show="survey_store.questionCount == current_question_index" @click="submitAnswers" color="primary" variant="flat" :disabled="isSubmitting">
                                    <v-progress-circular v-if="isSubmitting" indeterminate size="16" class="mr-2"></v-progress-circular>
                                    <i v-else class="fa-solid fa-check"></i>
                                    <span class="q-pa-sm">{{ isSubmitting ? 'Submitting...' : 'Submit' }}</span>
                                </v-btn>
                    </v-card-actions>
                </div>
            </v-card>
        </div>

        <!-- Loading Dialog -->
        <v-dialog v-model="isSubmitting" persistent width="400">
            <v-card>
                <v-card-text class="text-center pa-6">
                    <v-progress-circular indeterminate size="64" color="primary" class="mb-4"></v-progress-circular>
                    <div class="text-h6 mb-2">Submitting Your Answers</div>
                    <div class="text-body-2 text-medium-emphasis">Please wait while we save your responses...</div>
                </v-card-text>
            </v-card>
        </v-dialog>

    </NuxtLayout>
</template>


<script setup>
import { ref, watch } from "vue"
import { navigateTo } from "nuxt/app";
import { useSurveyStore } from "~/stores/survey";
import { useResponseStore } from '~/stores/response';
import { useMapViewStore } from "~/stores/mapview";
import { useGlobalStore } from "~/stores/global";
import { resetSurveySession } from "~/stores/utils/storeReset";
// import leaflet from "leaflet"
import "leaflet/dist/leaflet.css";

const responseStore = useResponseStore();
const mapViewStore = useMapViewStore();

mapViewStore.$reset();

const route = useRoute();
const survey_store = useSurveyStore();

// Ensure correct survey is selected for direct navigation to question pages
survey_store.selectSurvey(route.params.id);

// Load questions if not already loaded for this survey
if (!survey_store.questions.length || survey_store.selectedSurveyId !== route.params.id) {
    await survey_store.getQuestionsOfSurvey();
}

// Initialize survey session for batch submission  
const runtimeConfig = useRuntimeConfig();
const apiBaseUrl = runtimeConfig.apiParty?.endpoints?.cmsApi?.url || 'http://localhost:8000/voice/v3';
responseStore.initializeSurveySession({
    survey_url: `${apiBaseUrl}/surveys/${survey_store.selectedSurveyId}/`,
    respondent_url: null  // null for anonymous respondents
});

const questions = survey_store.questions;

// Handle case where questions couldn't be loaded
if (!questions || questions.length === 0) {
    throw createError({
        statusCode: 404,
        statusMessage: 'Survey questions not found. Please go back to the survey start page.'
    });
}

// Here, we use the list of questions in the survey store to display questions according to the order
// specified when the survey was created. We use the numbers in the URL to navigate between questions
// while maintaining the order of the questions in the survey store. 
var current_question_index = parseInt(route.params.question, 10); // use url questions id as an index to load each question 

// Validate question index
if (current_question_index < 1 || current_question_index > questions.length) {
    throw createError({
        statusCode: 404,
        statusMessage: 'Question not found in this survey.'
    });
}

let current_question_url = questions[current_question_index - 1].url;  // gets the id for the questions
let current_mapview_id = questions[current_question_index - 1].mapview;  // gets the value for the map view
let question = questions[current_question_index - 1];

// Initialize current_answer with existing answer from store if available
const initializeCurrentAnswer = async () => {
    const existingAnswer = responseStore.answers.find(answer => answer.question_url === current_question_url);
    
    if (existingAnswer) {
        console.log('Found existing answer for current question:', existingAnswer);
        
        // If answer has a saved mapview, restore it to the mapview store
        if (existingAnswer.mapview && existingAnswer.mapview.url && existingAnswer.mapview.location) {
            await restoreMapviewFromAnswer(existingAnswer.mapview);
        }
        
        return {
            question_url: current_question_url,
            text: existingAnswer.text || '',
            mapview: existingAnswer.mapview || {},
            question_index: existingAnswer.question_index || current_question_index
        };
    } else {
        console.log('No existing answer found, initializing empty answer');
        return { 
            question_url: current_question_url, 
            text: '', 
            mapview: {} 
        };
    }
};

const restoreMapviewFromAnswer = async (savedMapview) => {
    try {
        console.log('Restoring mapview from saved answer:', savedMapview);
        
        // Fetch the location data to get the geometries
        if (savedMapview.location) {
            const locationResponse = await $cmsApi(savedMapview.location, { method: 'GET' });
            
            if (locationResponse && locationResponse.geojson && locationResponse.geojson.features) {
                console.log('Restoring geometries:', locationResponse.geojson);
                
                // Update mapview store with the fetched data
                mapViewStore.updateGeometries(locationResponse.geojson);
                mapViewStore.updateLocation(savedMapview.location);
                mapViewStore.url = savedMapview.url;
                
                console.log('Mapview store restored successfully');
            }
        }
        
        // Also fetch mapview details if needed
        if (savedMapview.url) {
            await mapViewStore.fetchMapView(savedMapview.url);
        }
        
    } catch (error) {
        console.error('Error restoring mapview:', error);
    }
};

const current_answer = ref(await initializeCurrentAnswer());
const handleUpdateAnswer = (updatedAnswer, questionIndex) =>{
    // Handle the updated answer here
    // Get the current question index from the route (reactive to route changes)
    const currentQuestionIndex = parseInt(route.params.question, 10);
    const currentQuestionUrl = questions[currentQuestionIndex - 1].url;
    
    console.log('Current question index:', currentQuestionIndex);
    console.log('Current question URL:', currentQuestionUrl);
    console.log('Updated answer:', updatedAnswer);
    
    current_answer.text = updatedAnswer;
    current_answer.question_index = questionIndex;
    current_answer.question_url = currentQuestionUrl;
    const current_mapview = mapViewStore.getMapViewAnswer;
    current_answer.mapview = current_mapview;
    
    // Create a new answer object to avoid reference issues
    const answerToStore = {
        question_url: currentQuestionUrl,
        text: updatedAnswer,
        mapview: current_mapview,
        question_index: questionIndex
    };
    
    console.log('Answer to store:', answerToStore);
    
    // This will automatically create response if it doesn't exist yet
    responseStore.updateAnswer(answerToStore);
};
const circles = ref([]) // this is what user will add
let circleClickedAndRemoved = false
let resetClicked = false

// to navigate from one question to the previous/next
const prevQuestion = async () => {
    // if this is not the first question:
    let question_to_navigate = (parseInt(route.params.question, 10) - 1)
    if (question_to_navigate != 0) {
        return navigateTo('/survey/' + route.params.id + '/' + question_to_navigate)
    } else {
        return navigateTo('/survey/' + route.params.id)
    }
}

const nextQuestion = async () => {
    // if this is not the last question:
    return navigateTo('/survey/' + route.params.id + '/' + (parseInt(route.params.question, 10) + 1))
}


const isSubmitting = ref(false);

const submitAnswers = async () => {
    const global = useGlobalStore();

    isSubmitting.value = true;

    try {
        // First, validate required questions
        const validationResult = validateRequiredQuestions();
        if (!validationResult.isValid) {
            global.error(validationResult.errorMessage);
            return; // Don't submit if required validation fails
        }

        // Ensure all questions have answers (create empty answers for non-required skipped questions)
        await ensureAllQuestionsAnswered();

        // Use the new batch submission method
        await responseStore.batchSubmitAnswers();

        // Clear the store after submission
        resetSurveySession();

        global.succes("Your answers have been submitted");
        return navigateTo('/submitted/');

    } catch (error) {
        console.error("Error submitting answers:", error);
        global.error("There was an error submitting your answers. Please try again.");
    } finally {
        isSubmitting.value = false;
    }
};

const validateRequiredQuestions = () => {
    console.log('Validating required questions...');
    
    const missingRequiredQuestions = [];
    
    for (const question of questions) {
        // Check if question is required
        if (question.required === true) {
            const existingAnswer = responseStore.answers.find(answer => answer.question_url === question.url);
            
            // Check if answer exists and has non-empty text
            if (!existingAnswer || !existingAnswer.text || existingAnswer.text.trim() === '') {
                missingRequiredQuestions.push(question);
                console.log(`Required question missing answer: "${question.text}"`);
            }
        }
    }
    
    if (missingRequiredQuestions.length > 0) {
        const questionTitles = missingRequiredQuestions.map(q => `"${q.text}"`).join(', ');
        return {
            isValid: false,
            errorMessage: `Please answer the following required question${missingRequiredQuestions.length > 1 ? 's' : ''}: ${questionTitles}`
        };
    }
    
    console.log('All required questions have been answered');
    return { isValid: true };
};

const ensureAllQuestionsAnswered = async () => {
    // Create empty answers for any skipped NON-REQUIRED questions
    console.log('Ensuring all questions have answers...');
    console.log('Total questions in survey:', questions.length);
    console.log('Current answers in store:', responseStore.answers.length);

    for (const question of questions) {
        const existingAnswer = responseStore.answers.find(answer => answer.question_url === question.url);
        
        // Only create empty answers for non-required questions
        if (!existingAnswer && !question.required) {
            console.log(`Creating empty answer for skipped non-required question: ${question.url}`);
            
            // Create empty answer for skipped question
            const emptyAnswer = {
                question_url: question.url,
                text: '', // Empty string as required by backend
                mapview: {},
                question_index: questions.indexOf(question) + 1
            };
            
            // Add to response store
            responseStore.updateAnswer(emptyAnswer);
        }
    }
    
    console.log('Final answer count:', responseStore.answers.length);
};

// inspired by Roy J's solution on Stack Overflow:
// https://stackoverflow.com/questions/54499070/leaflet-and-vuejs-how-to-add-a-new-marker-onclick-in-the-map
const removeCircle = async (index) => {
    // console.log("removeCircle function called")
    circles._value.splice(index, 1)
    circleClickedAndRemoved = true
}

const addCircle = async (event) => {
    if (circleClickedAndRemoved) {
        circleClickedAndRemoved = false
    } else if (resetClicked) {
        resetClicked = false
    } else {
        // console.log("addCircle function called")
        circles._value.push(
            [event.latlng.lat, event.latlng.lng]
        )
    }
}
const resetMap = async () => {
    // console.log("resetMap function called")
    circles._value.splice(0, circles._value.length)
    // TODO: reset map center and zoom level based on mapview
    resetClicked = true
}

// TODO: fix the problem of writing answer bodies with the first input. The issue seems to persits between surveys as well.
// Check if code is using he data stored in the response stored to submit answers.


</script>

<style lang="scss">
#map {
    height: 180px;
}

/* Question requirement indicators */
.required-indicator {
    color: #d32f2f; /* Red color for required */
    font-weight: bold;
    font-size: 1.2em;
    margin-left: 4px;
}

.optional-indicator {
    color: #757575; /* Gray color for optional */
    font-size: 0.9em;
    font-style: italic;
    margin-left: 8px;
    opacity: 0.8;
}
</style>