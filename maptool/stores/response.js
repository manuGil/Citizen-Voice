import { defineStore } from 'pinia';
import { useUserStore } from './user';
import { useGlobalStore } from './global';
import setRequestConfig from './utils/setRequestConfig';
import { v4 as uuidv4 } from 'uuid';

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
                // Update image data if provided
                if (answer.image_file !== undefined) {
                    existingAnswer.image_file = answer.image_file;
                }
                if (answer.image_url !== undefined) {
                    existingAnswer.image_url = answer.image_url;
                }
            }
            else {
                // Ensure answer has proper structure
                const newAnswer = {
                    question_url: answer.question_url,
                    text: answer.text,
                    mapview: answer.mapview || {},
                    image_file: answer.image_file || null,
                    image_url: answer.image_url || null
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
        
        updateAnswerGeometries(question_url, geometries, mapOptions = null) {
            // Store geometries and map state for a specific question without creating mapview yet
            const existingAnswer = this.answers.find(a => a.question_url === question_url);
            if (existingAnswer) {
                // Store geometries in mapview object for later processing
                if (!existingAnswer.mapview) {
                    existingAnswer.mapview = {};
                }
                existingAnswer.mapview.geometries = geometries;
                
                // Store map options (zoom, center) if provided
                if (mapOptions) {
                    existingAnswer.mapview.userMapOptions = mapOptions;
                }
            } else {
                const answer = {
                    question_url: question_url,
                    text: '',
                    mapview: {
                        geometries: geometries,
                        userMapOptions: mapOptions
                    }
                };
                this.answers.push(answer);
            }
            console.log('Stored geometries and map options for question:', question_url, geometries, mapOptions);
        },
        
        getAnswerGeometries(question_url) {
            // Retrieve stored geometries for a specific question
            const existingAnswer = this.answers.find(a => a.question_url === question_url);
            if (existingAnswer && existingAnswer.mapview && existingAnswer.mapview.geometries) {
                return {
                    geometries: existingAnswer.mapview.geometries,
                    mapOptions: existingAnswer.mapview.userMapOptions
                };
            }
            return null;
        },

        getAnswerForQuestion(question_url) {
            // Retrieve stored answer for a specific question
            return this.answers.find(a => a.question_url === question_url);
        },

        updateAnswerImage(question_url, imageFile, imageUrl = null) {
            // Store image file locally for a specific question
            const existingAnswer = this.answers.find(a => a.question_url === question_url);
            if (existingAnswer) {
                existingAnswer.image_file = imageFile;
                existingAnswer.image_url = imageUrl;
                if (imageFile) {
                    existingAnswer.text = `Image selected: ${imageFile.name}`;
                }
            } else {
                const answer = {
                    question_url: question_url,
                    text: imageFile ? `Image selected: ${imageFile.name}` : '',
                    mapview: {},
                    image_file: imageFile,
                    image_url: imageUrl
                };
                this.answers.push(answer);
            }
            console.log('Stored image for question:', question_url, imageFile?.name);
        },

        removeAnswerImage(question_url) {
            // Remove stored image for a specific question
            const existingAnswer = this.answers.find(a => a.question_url === question_url);
            if (existingAnswer) {
                existingAnswer.image_file = null;
                existingAnswer.image_url = null;
                existingAnswer.text = '';
            }
            console.log('Removed image for question:', question_url);
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

            console.log('Submitting answer with config:', {
                url: '/answers/',
                method: 'POST',
                response_url,
                question_url,
                answer_value,
                mapview_url
            });

            const { data: response, error: err } = await useAsyncData(`submitAnswer-${Date.now()}-${Math.random()}`, () => $cmsApi('/answers/', config));

            if (response) {
                console.log('Answer submitted successfully:', response.value);
                return response.value;
            }

            if (err?.value) {
                console.error('Error in submitAnswer:', err.value);
                throw new Error(`Failed to submit answer: ${JSON.stringify(err.value)}`);
            }

        },

        async batchSubmitAnswers() {
            // Create response first, then process mapviews and submit all answers sequentially
            if (!this.surveySession) {
                throw new Error('Survey session not initialized');
            }

            // Create response if it doesn't exist
            if (Object.keys(this.responseData).length === 0) {
                await this.createResponse(this.surveySession);
            }

            console.log(`Processing ${this.answers.length} answers for submission...`);
            
            // First pass: Create mapviews for answers that have geometries
            await this.createMapviewsForAnswers();
            
            console.log(`Submitting ${this.answers.length} answers sequentially...`);
            
            // Submit answers sequentially to avoid race conditions
            for (let i = 0; i < this.answers.length; i++) {
                const answer = this.answers[i];
                const mapview_url = answer.mapview && answer.mapview.url ? answer.mapview.url : null;
                
                console.log(`Submitting answer ${i + 1}/${this.answers.length}:`, {
                    question_url: answer.question_url,
                    text: answer.text,
                    mapview_url: mapview_url,
                    has_image: !!answer.image_file
                });

                try {
                    // Check if this answer has an image file to upload
                    if (answer.image_file) {
                        await this.submitImageAnswer(answer, mapview_url);
                    } else {
                        await this.submitAnswer(
                            this.responseUrl,
                            answer.question_url,
                            answer.text,
                            mapview_url
                        );
                    }
                    console.log(`Answer ${i + 1} submitted successfully`);
                } catch (error) {
                    console.error(`Failed to submit answer ${i + 1}:`, error);
                    throw error; // Re-throw to stop submission on first failure
                }
            }
            
            console.log('All answers submitted successfully!');
        },

        async submitImageAnswer(answer, mapview_url) {
            // Submit an answer that includes an image file
            const user = useUserStore();
            const csrftoken = user.getCookie('csrftoken');
            const token = user.getAuthToken;

            // Create FormData for the upload
            const formData = new FormData();
            formData.append('question', answer.question_url);
            formData.append('image', answer.image_file);
            formData.append('response', this.responseUrl);

            // Handle mapview - only append if it exists and is valid
            if (mapview_url && mapview_url.trim() !== '' && mapview_url !== 'null') {
                console.log('Adding mapview to image upload:', mapview_url);
                formData.append('mapview', mapview_url);
            } else {
                console.log('No mapview provided for image upload');
            }

            const config = {
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                method: 'POST',
                body: formData
            };

            if (token) {
                config.headers['Authorization'] = `Token ${token}`;
            }

            console.log('Submitting image answer:', {
                question_url: answer.question_url,
                image_name: answer.image_file.name,
                mapview_url: mapview_url
            });

            const { data: response, error: err } = await useAsyncData(`submitImageAnswer-${Date.now()}-${Math.random()}`, () => $cmsApi('/answers/upload_image_answer/', config));

            if (response) {
                console.log('Image answer submitted successfully:', response.value);
                return response.value;
            }

            if (err?.value) {
                console.error('Error in submitImageAnswer:', err.value);
                throw new Error(`Failed to submit image answer: ${JSON.stringify(err.value)}`);
            }
        },

        async createMapviewsForAnswers() {
            // Create mapviews for answers that have collected geometries
            console.log('Processing mapview creation for answers with geometries...');
            
            for (let i = 0; i < this.answers.length; i++) {
                const answer = this.answers[i];
                
                // Check if this answer has geometry data stored in answerMapViewStore
                // We need to check if there's geometry data for this specific question
                if (this.needsMapviewCreation(answer)) {
                    console.log(`Creating mapview for answer ${i + 1}:`, answer.question_url);
                    
                    try {
                        const mapviewData = await this.createMapviewForAnswer(answer);
                        
                        // Update the answer with the created mapview information
                        answer.mapview = {
                            url: mapviewData.url,
                            location: mapviewData.location
                        };
                        
                        console.log(`Mapview created successfully for answer ${i + 1}`);
                    } catch (error) {
                        console.error(`Failed to create mapview for answer ${i + 1}:`, error);
                        throw error;
                    }
                }
            }
        },

        needsMapviewCreation(answer) {
            // Check if this answer has geometries that need to be saved as a mapview
            return answer.mapview && 
                   answer.mapview.geometries && 
                   answer.mapview.geometries.features && 
                   answer.mapview.geometries.features.length > 0 &&
                   !answer.mapview.url; // Only if mapview URL doesn't exist yet
        },

        async createMapviewForAnswer(answer) {
            // Create a mapview with the collected geometries for this answer
            const { useAnswerMapViewStore } = await import('./answerMapview');
            const answerMapViewStore = useAnswerMapViewStore();
            
            // Temporarily populate the answerMapViewStore with this answer's data
            answerMapViewStore.$reset();
            answerMapViewStore.updateName(uuidv4());
            answerMapViewStore.updateGeometries(answer.mapview.geometries);
            
            // Use actual user map options if available, otherwise fall back to defaults
            if (answer.mapview.userMapOptions) {
                console.log('Using user map options:', answer.mapview.userMapOptions);
                answerMapViewStore.updateZoomLevel(answer.mapview.userMapOptions.zoom);
                answerMapViewStore.updateCenter(answer.mapview.userMapOptions.center);
                answerMapViewStore.updateMapServiceUrl(answer.mapview.userMapOptions.mapServiceUrl || 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
            } else {
                // Set default map service URL and options
                answerMapViewStore.updateMapServiceUrl('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
                answerMapViewStore.updateZoomLevel(8);
                answerMapViewStore.updateCenter([52.045, 5.10]);
            }
            
            // Create the mapview
            const response = await answerMapViewStore.createMapview();
            
            if (response && response.data) {
                return {
                    url: answerMapViewStore.url,
                    location: answerMapViewStore.location
                };
            } else {
                throw new Error('Failed to create mapview');
            }
        }

    }
})