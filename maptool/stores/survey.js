import { defineStore } from 'pinia'
import { useUserStore } from './user'
import { useGlobalStore } from './global'
import setRequestConfig from './utils/setRequestConfig';

export const useSurveyStore = defineStore('survey', {
    state: () => {
        return {
            selectedSurveyId: null,
            currentSurveyDesign: [],
            questions: [],
            // Shareable link state
            shareableLink: {
                enabled: false,
                token: null,
                requiresAuth: false,
                expiresAt: null,
                url: null,
            }
        }
    },
    getters: {
        questionCount() {
            return this.questions.length
        },
        getMapViewUrl() {
            return (index) => {
                if (!this.questions || this.questions.length === 0 || index < 0 || index >= this.questions.length) {
                    return null;
                }
                return this.questions[index]?.mapview || null;
            }
        },
        getShareableUrl() {
            return this.shareableLink.url
        }
    },
    actions: {
        $reset() {
            this.selectedSurveyId = null
            this.currentSurveyDesign = []
            this.questions = []
            this.shareableLink = {
                enabled: false,
                token: null,
                requiresAuth: false,
                expiresAt: null,
                url: null,
            }
        },

        async getSurvey(survey_url) {
            const user = useUserStore()
            const token = user.getAuthToken

            const config = {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'GET',
            }

            if (token) {
                config.headers['Authorization'] = `Bearer ${token}`
            }

            const data = await useAsyncData(() => $cmsApi(survey_url, config));

            return data
        },

        selectSurvey(id) {
            this.selectedSurveyId = id
        },

        async getSurveys() {
            const user = useUserStore()
            const token = user.getAuthToken

            const config = {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'GET',
            }

            if (token) {
                config.headers['Authorization'] = `Bearer ${token}`
            }
            const { data, error } = await useAsyncData('surveys', () => $cmsApi('/surveys', config));

            return { data, error }
        },

        /**
         * Create a new survey based on the passed parameters
         */
        async createSurvey(
            name,
            description,
            publish_date,
            expire_date
        ) {
            const user = useUserStore()
            const global = useGlobalStore()
            const csrftoken = user.getCookie('csrftoken');
            const token = user.getAuthToken

            const config = {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                method: 'POST',
                body: {
                    name,
                    description,
                    publish_date,
                    expire_date
                },
            }

            if (token) {
                config.headers['Authorization'] = `Bearer ${token}`
            }

            const { data: register, pending, error } = await useAsyncData('createSurvey', () => $cmsApi('/surveys/create-survey', config))

            if (error.value) {
                let warnMessage = null
                for (const [key, value] of Object.entries(error._value.data)) {
                    warnMessage = warnMessage ? `${warnMessage} \n\n ${key}: ${value}` : `${key}: ${value}`
                }
                global.warning(warnMessage)
                return null
            }

            if (register?.value) {
                global.succes('Survey created successfully')
                this.id = register.value.id
                return register.value
            }

            return this.id
        },

        /**
         * Update an existing survey
         */
        async updateSurvey(id, body) {
            const global = useGlobalStore()
            const config = setRequestConfig({ method: 'PATCH', body: { ...body } })

            const { data: register, pending, error } = await useAsyncData('updateSurvey', () => $cmsApi(`/surveys/${id}/`, config))

            if (error.value) {
                let warnMessage = null
                for (const [key, value] of Object.entries(error._value.data)) {
                    warnMessage = warnMessage ? `${warnMessage} \n\n ${key}: ${value}` : `${key}: ${value}`
                }
                global.warning(warnMessage)
                return null
            }
            if (register?.value) {
                global.succes('Updated')
                return register.value
            }
        },

        /**
         * Get surveys of the current user
         */
        async getSurveysOfCurrentUser() {
            const user = useUserStore()
            await user.loadUser()
            const global = useGlobalStore()
            const csrftoken = user.getCookie('csrftoken');
            const token = user.getAuthToken

            const config = {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                method: 'GET'
            }

            if (token) {
                config.headers['Authorization'] = `Bearer ${token}`
            }

            const response = await useAsyncData('getSurveys', () => $cmsApi('/surveys/my-surveys', config))

            const error = response.error
            if (error.value) {
                let warnMessage = null
                for (const [key, value] of Object.entries(error._value.data)) {
                    warnMessage = warnMessage ? `${warnMessage} \n\n ${key}: ${value}` : `${key}: ${value}`
                }
                global.warning(warnMessage)
            }

            return response
        },

        /**
         * Delete an existing survey based on the passed ID
         */
        async deleteSurvey(id) {
            const user = useUserStore()
            const global = useGlobalStore()
            const csrftoken = user.getCookie('csrftoken');
            const token = user.getAuthToken

            const config = {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                method: 'DELETE'
            }

            if (token) {
                config.headers['Authorization'] = `Bearer ${token}`
            }

            const { data: register, pending, error } = await useAsyncData('deleteSurvey', () => $cmsApi('/surveys/' + id, config))

            if (error.value) {
                let warnMessage = null
                for (const [key, value] of Object.entries(error._value.data)) {
                    warnMessage = warnMessage ? `${warnMessage} \n\n ${key}: ${value}` : `${key}: ${value}`
                }
                global.warning(warnMessage)
            }
            else {
                global.succes('Survey deleted')
                this.id = 1
                await navigateTo('/design')
            }
        },

        async getQuestionsOfSurvey() {
            const user = useUserStore();
            const global = useGlobalStore();
            const config = setRequestConfig({ method: 'GET' });

            const id = this.selectedSurveyId

            // Use unique cache key per survey to prevent loading cached questions from wrong survey
            const { data: response, pending, error } = await useAsyncData(`survey-${id}-questions`, () => $cmsApi('/surveys/' + id + '/questions', config));

            const responseData = await response.value;

            this.questions = responseData;

            if (error.value) {
                console.log('error in get questions //> ', error.value);
            };

            return responseData;
        },

        // ============================================
        // Shareable Link Actions
        // ============================================

        /**
         * Generate a shareable link for a survey
         * @param {number} surveyId - The survey ID
         * @param {boolean} requiresAuth - Whether link requires authentication
         * @param {number|null} expiresInDays - Expiration in days (null for no expiration)
         */
        async generateShareableLink(surveyId, requiresAuth = false, expiresInDays = null) {
            const user = useUserStore()
            const global = useGlobalStore()
            const token = user.getAuthToken

            if (!token) {
                global.warning('You must be logged in to generate shareable links')
                return null
            }

            const config = {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                method: 'POST',
                body: {
                    requires_auth: requiresAuth,
                    expires_in_days: expiresInDays
                }
            }

            try {
                const { data, error } = await useAsyncData(
                    `generate-shareable-link-${surveyId}`,
                    () => $cmsApi(`/surveys/${surveyId}/generate-shareable-link/`, config),
                    { server: false }
                )

                if (error.value) {
                    console.error('Generate shareable link error:', error.value)
                    global.warning('Failed to generate shareable link')
                    return null
                }

                if (data.value) {
                    this.shareableLink = {
                        enabled: data.value.shareable_link_enabled,
                        token: data.value.shareable_token,
                        requiresAuth: data.value.shareable_link_requires_auth,
                        expiresAt: data.value.shareable_link_expires_at,
                        url: data.value.shareable_url,
                    }
                    global.succes('Shareable link generated!')
                    return data.value
                }
            } catch (e) {
                console.error('Generate shareable link exception:', e)
                global.warning('Failed to generate shareable link')
                return null
            }
        },

        /**
         * Disable the shareable link for a survey
         * @param {number} surveyId - The survey ID
         */
        async disableShareableLink(surveyId) {
            const user = useUserStore()
            const global = useGlobalStore()
            const token = user.getAuthToken

            if (!token) {
                global.warning('You must be logged in to manage shareable links')
                return false
            }

            const config = {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                method: 'POST'
            }

            try {
                const { data, error } = await useAsyncData(
                    `disable-shareable-link-${surveyId}`,
                    () => $cmsApi(`/surveys/${surveyId}/disable-shareable-link/`, config),
                    { server: false }
                )

                if (error.value) {
                    console.error('Disable shareable link error:', error.value)
                    global.warning('Failed to disable shareable link')
                    return false
                }

                this.shareableLink = {
                    enabled: false,
                    token: null,
                    requiresAuth: false,
                    expiresAt: null,
                    url: null,
                }
                global.succes('Shareable link disabled')
                return true
            } catch (e) {
                console.error('Disable shareable link exception:', e)
                global.warning('Failed to disable shareable link')
                return false
            }
        },

        /**
         * Access a survey via shareable link token
         * @param {string} shareableToken - The shareable token
         */
        async accessSurveyViaShareableLink(shareableToken) {
            const user = useUserStore()
            const token = user.getAuthToken

            const config = {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'GET'
            }

            // Include auth token if user is logged in
            if (token) {
                config.headers['Authorization'] = `Bearer ${token}`
            }

            try {
                const { data, error } = await useAsyncData(
                    `access-shareable-${shareableToken}`,
                    () => $cmsApi(`/surveys/share/${shareableToken}/`, config),
                    { server: false }
                )

                if (error.value) {
                    console.error('Access via shareable link error:', error.value)
                    return { success: false, error: error.value }
                }

                if (data.value) {
                    this.selectedSurveyId = data.value.id
                    return { success: true, survey: data.value }
                }
            } catch (e) {
                console.error('Access via shareable link exception:', e)
                return { success: false, error: e }
            }

            return { success: false, error: 'Unknown error' }
        },

        /**
         * Get questions via shareable link token
         * @param {string} shareableToken - The shareable token
         */
        async getQuestionsViaShareableLink(shareableToken) {
            const user = useUserStore()
            const token = user.getAuthToken

            const config = {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'GET'
            }

            // Include auth token if user is logged in
            if (token) {
                config.headers['Authorization'] = `Bearer ${token}`
            }

            try {
                const { data, error } = await useAsyncData(
                    `questions-shareable-${shareableToken}`,
                    () => $cmsApi(`/surveys/share/${shareableToken}/questions/`, config),
                    { server: false }
                )

                if (error.value) {
                    console.error('Get questions via shareable link error:', error.value)
                    return { success: false, error: error.value }
                }

                if (data.value) {
                    this.questions = data.value
                    return { success: true, questions: data.value }
                }
            } catch (e) {
                console.error('Get questions via shareable link exception:', e)
                return { success: false, error: e }
            }

            return { success: false, error: 'Unknown error' }
        },

        /**
         * Load shareable link status for a survey
         * @param {number} surveyId - The survey ID
         */
        async loadShareableLinkStatus(surveyId) {
            const user = useUserStore()
            const token = user.getAuthToken

            if (!token) {
                return null
            }

            const config = {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                method: 'GET'
            }

            try {
                const { data, error } = await useAsyncData(
                    `survey-${surveyId}`,
                    () => $cmsApi(`/surveys/${surveyId}/`, config),
                    { server: false }
                )

                if (data.value) {
                    this.shareableLink = {
                        enabled: data.value.shareable_link_enabled || false,
                        token: data.value.shareable_token || null,
                        requiresAuth: data.value.shareable_link_requires_auth || false,
                        expiresAt: data.value.shareable_link_expires_at || null,
                        url: data.value.shareable_token 
                            ? `${window.location.origin}/citizen-map/survey/share/${data.value.shareable_token}`
                            : null,
                    }
                    return this.shareableLink
                }
            } catch (e) {
                console.error('Load shareable link status exception:', e)
            }

            return null
        }
    }
})
