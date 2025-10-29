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
                    v-if="question.question_type === LONG_TEXT"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                    />
                    <RespondentViewQuestionTypesAnswerTypeShortText
                    v-if="question.question_type === SHORT_TEXT"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                    />
                    <RespondentViewQuestionTypesAnswerTypeSelect
                    v-if="question.question_type === SINGLE_CHOICE"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                    />
                    <RespondentViewQuestionTypesAnswerTypeMultiselect
                     v-if="question.question_type === MULTIPLE_CHOICE"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                     />
                    <RespondentViewQuestionTypesAnswerTypeDate
                    v-if="question.question_type === DATE"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                    />
                    <RespondentViewQuestionTypesAnswerTypeInteger
                    v-if="question.question_type === INTEGER"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                    />
                    <RespondentViewQuestionTypesAnswerTypeFloat
                    v-if="question.question_type === FLOAT"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                    />
                    <RespondentViewQuestionTypesAnswerTypeUploadImage
                    v-if="question.question_type === IMAGE_UPLOAD"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                    />
                    <RespondentViewQuestionTypesAnswerTypeLikertScale
                    v-if="question.question_type === LIKERT_SCALE"
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
                        ref="mapViewRef"
                        :mapViewUrl ="question.mapview"
                        :savedGeometries="savedMapData?.geometries" 
                        :savedMapOptions="savedMapData?.mapOptions"
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
import { useQuestionMapViewStore } from "~/stores/questionMapview";
import { useAnswerMapViewStore } from "~/stores/answerMapview";
import { useGlobalStore } from "~/stores/global";
import { resetSurveySession } from "~/stores/utils/storeReset";
import { extractRelativePath, cmsApiCall } from "~/utils/urlUtils";
import { LONG_TEXT, SHORT_TEXT, SINGLE_CHOICE, MULTIPLE_CHOICE, INTEGER, FLOAT, DATE, IMAGE_UPLOAD, LIKERT_SCALE } from "~/constants/questions";
// import leaflet from "leaflet"
import "leaflet/dist/leaflet.css";

const responseStore = useResponseStore();
const questionMapViewStore = useQuestionMapViewStore(); // For question base data
const answerMapViewStore = useAnswerMapViewStore(); // For user answer data

questionMapViewStore.$reset();
answerMapViewStore.$reset();

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
        
        // If answer has a saved mapview, restore it to the answerMapViewStore
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
            console.log('Using location URL:', savedMapview.location);
            
            const locationResponse = await cmsApiCall($cmsApi, savedMapview.location, { method: 'GET' });
            
            if (locationResponse && locationResponse.geojson && locationResponse.geojson.features) {
                console.log('Restoring geometries:', locationResponse.geojson);
                
                // Update answerMapViewStore with the fetched data
                answerMapViewStore.updateGeometries(locationResponse.geojson);
                answerMapViewStore.updateLocation(savedMapview.location);
                answerMapViewStore.url = savedMapview.url;
                
                console.log('Mapview store restored successfully');
            }
        }
        
        // Set mapview URL if provided
        if (savedMapview.url) {
            console.log('Setting mapview URL:', savedMapview.url);
            answerMapViewStore.url = savedMapview.url;
        }
        
    } catch (error) {
        console.error('Error restoring mapview:', error);
    }
};

const current_answer = ref(await initializeCurrentAnswer());
const mapViewRef = ref(null);

// Load saved geometries for the current question if available
const savedMapData = responseStore.getAnswerGeometries(current_question_url);
console.log('Loaded saved map data for current question:', savedMapData);
const handleUpdateAnswer = (updatedAnswer, questionIndex) =>{
    // Handle the updated answer here
    // Get the current question index from the route (reactive to route changes)
    const currentQuestionIndex = parseInt(route.params.question, 10);
    const currentQuestionUrl = questions[currentQuestionIndex - 1].url;
    
    console.log('Current question index:', currentQuestionIndex);
    console.log('Current question URL:', currentQuestionUrl);
    console.log('Updated answer:', updatedAnswer);
    
    current_answer.value.text = updatedAnswer;
    current_answer.value.question_index = questionIndex;
    current_answer.value.question_url = currentQuestionUrl;
    
    // For mapview questions, include current geometries and map state
    let current_mapview = {};
    if (question.mapview) {
        let geometries = null;
        let mapOptions = null;
        
        // Get current map state from the MapView component if available
        if (mapViewRef.value && mapViewRef.value.getMapState) {
            const mapState = mapViewRef.value.getMapState();
            geometries = mapState.geometries;
            mapOptions = mapState.mapOptions;
        } else if (answerMapViewStore.geometries) {
            // Fallback to store data
            geometries = answerMapViewStore.geometries;
            mapOptions = {
                zoom: answerMapViewStore.zoomLevel,
                center: answerMapViewStore.center,
                mapServiceUrl: answerMapViewStore.mapServiceUrl
            };
        }
        
        current_mapview = {
            geometries: geometries,
            userMapOptions: mapOptions
        };
    }
    current_answer.value.mapview = current_mapview;
    
    // Check if there's stored image data for this question
    const storedImageData = responseStore.getAnswerForQuestion(currentQuestionUrl);
    
    // Create a new answer object to avoid reference issues
    const answerToStore = {
        question_url: currentQuestionUrl,
        text: updatedAnswer,
        mapview: current_mapview,
        question_index: questionIndex,
        image_file: storedImageData?.image_file || null,
        image_url: storedImageData?.image_url || null
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
    // Save current question's geometries before navigating
    await saveCurrentQuestionGeometries();
    
    // if this is not the first question:
    let question_to_navigate = (parseInt(route.params.question, 10) - 1)
    if (question_to_navigate != 0) {
        return navigateTo('/survey/' + route.params.id + '/' + question_to_navigate)
    } else {
        return navigateTo('/survey/' + route.params.id)
    }
}

const nextQuestion = async () => {
    // Save current question's geometries before navigating
    await saveCurrentQuestionGeometries();
    
    // if this is not the last question:
    return navigateTo('/survey/' + route.params.id + '/' + (parseInt(route.params.question, 10) + 1))
}

const saveCurrentQuestionGeometries = async () => {
    // Save geometries and map state for the current question if it has a mapview
    if (question.mapview) {
        // Get current geometries from answerMapViewStore
        const geometries = answerMapViewStore.geometries;
        const mapOptions = {
            zoom: answerMapViewStore.zoomLevel,
            center: answerMapViewStore.center,
            mapServiceUrl: answerMapViewStore.mapServiceUrl
        };
        
        // Store geometries and map options in responseStore
        responseStore.updateAnswerGeometries(current_question_url, geometries, mapOptions);
        
        // Create mapview object for the answer
        const current_mapview = {
            geometries: geometries,
            userMapOptions: mapOptions
        };
        
        // Update the answer in responseStore
        const answerToStore = {
            question_url: current_question_url,
            text: current_answer.value.text || '',
            mapview: current_mapview,
            question_index: current_question_index
        };
        
        responseStore.updateAnswer(answerToStore);
    }
}


const isSubmitting = ref(false);

const submitAnswers = async () => {
    const global = useGlobalStore();

    isSubmitting.value = true;

    try {
        // Save current question's geometries before submission
        await saveCurrentQuestionGeometries();
        
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
            
            // Special case: Required question with hidden text field and map
            if (!question.has_text_input && question.mapview != null) {
                console.log(`Validating map-only required question: "${question.text}"`);
                
                // For map-only questions, check if geometries exist instead of text
                const hasGeometries = existingAnswer && 
                    existingAnswer.mapview && 
                    existingAnswer.mapview.geometries && 
                    existingAnswer.mapview.geometries.features && 
                    existingAnswer.mapview.geometries.features.length > 0;
                
                if (!hasGeometries) {
                    missingRequiredQuestions.push(question);
                    console.log(`Required map-only question missing geometries: "${question.text}"`);
                }
            } else {
                // Standard validation: check if answer exists and has non-empty text
                if (!existingAnswer || existingAnswer.text === null || existingAnswer.text === undefined || String(existingAnswer.text).trim() === '') {
                    missingRequiredQuestions.push(question);
                    console.log(`Required question missing answer: "${question.text}"`);
                }
            }
        }
    }
    
    if (missingRequiredQuestions.length > 0) {
        const questionTitles = missingRequiredQuestions.map(q => `"${q.text}"`).join(', ');
        const hasMapOnlyQuestions = missingRequiredQuestions.some(q => !q.has_text_input && q.mapview != null);
        
        let errorMessage = `Please answer the following required question${missingRequiredQuestions.length > 1 ? 's' : ''}: ${questionTitles}`;
        
        if (hasMapOnlyQuestions) {
            errorMessage += '. For map questions, you must add at least one geometry to the map.';
        }
        
        return {
            isValid: false,
            errorMessage: errorMessage
        };
    }
    
    console.log('All required questions have been answered');
    return { isValid: true };
};

const ensureAllQuestionsAnswered = async () => {
    // Create empty answers for any skipped NON-REQUIRED questions
    // and ensure map-only required questions have proper answer records
    console.log('Ensuring all questions have answers...');
    console.log('Total questions in survey:', questions.length);
    console.log('Current answers in store:', responseStore.answers.length);

    for (const question of questions) {
        const existingAnswer = responseStore.answers.find(answer => answer.question_url === question.url);
        
        if (!existingAnswer) {
            if (!question.required) {
                // Create empty answers for non-required questions
                console.log(`Creating empty answer for skipped non-required question: ${question.url}`);
                
                const emptyAnswer = {
                    question_url: question.url,
                    text: '', // Empty string as required by backend
                    mapview: {},
                    question_index: questions.indexOf(question) + 1
                };
                
                responseStore.updateAnswer(emptyAnswer);
            } else if (question.required && !question.has_text_input && question.mapview != null) {
                // Special case: Required map-only questions need answer records even with empty text
                console.log(`Creating answer record for required map-only question: ${question.url}`);
                
                // Check if there are geometries saved for this question
                const savedMapData = responseStore.getAnswerGeometries(question.url);
                
                const mapOnlyAnswer = {
                    question_url: question.url,
                    text: '', // Empty text is OK for map-only questions
                    mapview: savedMapData || {},
                    question_index: questions.indexOf(question) + 1
                };
                
                responseStore.updateAnswer(mapOnlyAnswer);
            }
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
    resetClicked = true
}


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