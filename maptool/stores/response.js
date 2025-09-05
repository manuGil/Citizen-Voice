import { defineStore } from 'pinia';
import { useUserStore } from './user';
import { useGlobalStore } from './global';
import setRequestConfig from './utils/setRequestConfig';

// const answer = useAnswerStore();

export const useResponseStore = defineStore('response', {

    state: () =>
    // required data for the response store
    // responseId // if null it means that the respondent 
    // respondent
    {
        return {
            responseData: {},
            surveySession: null, // Store survey context before response creation
            answers:
                [
                    // expects an array of objects with the following structure
                    // {
                    // question_url: string
                    // text: string
                    // mapview: {url: uri or null, location: uri or null} 
                    // }
                ],

        }
    },
    getters: {
        responseId() {
            return this.responseData.response_id
        },
        responseUrl() {
            return this.responseData.url
        },
        // when using ARROW functions, state should be passed as an argument to be able to 
        // access the state of the store using 'this'
        // getAnswersToCurrentSurvey: (state) => this.answersToCurrentSurvey

    },
    actions: {
        updateAnswer(answer) {
            // Store answers locally without creating response yet
            const existingAnswer = this.answers.find(a => a.question_url === answer.question_url);
            if (existingAnswer) {
                existingAnswer.text = answer.text;
                if (!existingAnswer.mapview || (existingAnswer.mapview && Object.keys(existingAnswer.mapview).length === 0))
                    // update the mapview object only if it is empty or undefined
                    existingAnswer.mapview = answer.mapview || {};
            }
            else {
                // Ensure answer has proper structure
                const newAnswer = {
                    question_url: answer.question_url,
                    text: answer.text,
                    mapview: answer.mapview || {}
                };
                this.answers.push(newAnswer);
            }

        },
        updateAnswerMapView(answer_mapview) {
            // Store mapview answers locally without creating response yet

            // answer_mapview  must be an object with the following structure
            // { question_url: uri,
            //  mapview:{
            //  url: uri,
            //  location: uri
            //  }
            // }
            const existingAnswer = this.answers.find(a => a.question_url === answer_mapview.question_url);
            if (existingAnswer) {
                // existingAnswer.text = answer.text;
                existingAnswer.mapview = answer_mapview.mapview;
            }
            else {
                const answer = {
                    question_url: answer_mapview.question_url,
                    text: '', 
                    mapview: answer_mapview.mapview || {}
                }

                // console.log('answer in update answer map view //> ', answer);
                this.answers.push(answer);
            }

        },

        initializeSurveySession(sessionData) {
            // Store survey context without creating response yet
            this.surveySession = sessionData;
        },

        async ensureResponseExists() {
            // Create response if it doesn't exist yet and we have survey session data
            if (Object.keys(this.responseData).length === 0 && this.surveySession) {
                try {
                    await this.createResponse(this.surveySession);
                } catch (error) {
                    console.error('Failed to create survey session:', error);
                    throw error;
                }
            }
        },

        async createResponse({ survey_url, respondent_url = null }) {
            /**
         * Creates a respondent in the backend and initializes the localstorage with:
         * respondent, iterview-uuid, and message
         * 
         * @param {number} survey_url URI to existing survey
         * @param {number} responden_url URI to the existingrespondent, null values means that the respondent is not logged in, and the backend will create register the respondent as anonymous (if allowed by the survey)
         * @returns {object} the response object 
         * 
         * @question what happens if a respondent does multiple surveys, do we need to link all the surveys?
         */

            // console.log('surveyId //> ', surveyId);
            const user = useUserStore()
            const csrftoken = user.getCookie('csrftoken');
            const token = user.getAuthToken


            // update schema in client
            // modify this to use the new api endpoint
            const config = setRequestConfig({
                method: 'POST',
                body: {
                    survey: survey_url,
                    respondent: respondent_url  // this is required by the api
                }
            });

            if (Object.keys(this.responseData).length === 0) {

                const { data: response, pending, error } = await useAsyncData(() => $cmsApi('/responses/', config));

                const responseData = await response.value;

                // console.log('config //> ', config);
                if (error.value) {
                    throw new Error('error in createResponse //> ', error);
                }
                this.responseData = responseData;
                // console.log('responseData //> ', responseData);
            }
        },

        getRespondentId() {
            if (localStorage?.getItem('respondent-id') !== null) {
                return localStorage.getItem('respondent-id')
            }
            return null
        },
        setResponse(response) {
            this.responseId = response
        },
        setCurrentQuestion(questionNumber) {
            this.currentQuestion = questionNumber
        },
        async getSurvey({ id }) {

            const { data: survey } = await useAsyncData(() => $cmsApi('/surveys/' + id));

            if (survey) {
                // console.log('survey.value.id in get Survey//> ', survey.value.id);
                this.surveyId = survey.id;
            }

            return survey
        },

        clearAnswers() {
            // Clear all the answers and reset response data
            this.answers = [];
            this.responseData = {};
            this.surveySession = null;
        },
        async submitAnswer(response_url, question_url, answer_value, mapview_url = null) {
            const user = useUserStore();
            const global = useGlobalStore();
            const csrftoken = user.getCookie('csrftoken');
            const token = user.getAuthToken;

            // Create FormData instead of JSON
            const formData = new FormData();
            formData.append('response', response_url);
            formData.append('question', question_url);
            formData.append('body', answer_value);

            // ✅ Only append mapview if it has a valid value
            if (mapview_url && mapview_url.trim() !== '' && mapview_url !== 'null') {
                console.log('Adding mapview to form:', mapview_url);
                formData.append('mapview', mapview_url);
            } else {
                console.log('No mapview provided - field will be null');
                // Don't append anything - this will result in null in the serializer
            }

            const config = {
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                method: 'POST',
                // pas the data for the new Response object as the request body

                // TODO: have the repondent set to the logged in user 

                body: formData  // Use FormData instead of JSON
            };
            if (token) {
                config.headers['Authorization'] = `Token ${token}`
            };

            // console.log('config //>', config);
            const { data: response, error: err } = await useAsyncData('submitAnswer', () => $cmsApi('/answers/', config));

            if (response) {
                console.log('response submitted //> ', response);
            }

            if (err?.value) {
                throw new Error('error in SubmitAnswer //> ', err);
            }

        },

        async batchSubmitAnswers() {
            // Create response first, then submit all answers as a batch
            if (!this.surveySession) {
                throw new Error('Survey session not initialized');
            }

            // Create response if it doesn't exist
            if (Object.keys(this.responseData).length === 0) {
                await this.createResponse(this.surveySession);
            }

            // Submit all answers
            const submitPromises = this.answers.map(answer => {
                const mapview_url = answer.mapview && answer.mapview.url ? answer.mapview.url : null;
                return this.submitAnswer(
                    this.responseUrl,
                    answer.question_url,
                    answer.text,
                    mapview_url
                );
            });

            await Promise.all(submitPromises);
        }

    }
})