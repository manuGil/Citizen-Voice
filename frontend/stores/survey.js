import { defineStore } from 'pinia'
import { useUserStore } from './user'
import { useGlobalStore } from './global'

export const useSurveyStore = defineStore('survey', {
    state: () => {
        return {
            id: null
        }
    },
    getters: {

    },
    actions: {
        /**
        * Create survey
        * @param {*} name 
        * @param {*} description 
        * @param {*} publish_date 
        * @param {*} expire_date 
        * @param {id} id 
        */

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
            const token = user.userData.token

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
                config.headers['Authorization'] = `Token ${token}`
            }

            const { data: register, pending, error } = await useAsyncData('createSurvey', () => $cmsApi('/api/surveys/', config))

            if (error.value) {
                let warnMessage = null
                for (const [key, value] of Object.entries(error._value.data)) {
                    warnMessage = warnMessage ? `${warnMessage} \n\n ${key}: ${value}` : `${key}: ${value}`
                }
                // Notification
                global.negativeNotify(warnMessage)

            }
            if (register?.value) {
                // Notification
                global.succesNotify('createSurvey complete')
                this.id = 1
                await navigateTo('/design')
            }

        },

        /**
         * Delete an existing survey based on the passed ID
         */
        async deleteSurvey(
            id
        ) {
            const user = useUserStore()
            const global = useGlobalStore()
            const csrftoken = user.getCookie('csrftoken');
            const token = user.userData.token

            const config = {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                method: 'DELETE'
            }


            if (token) {
                config.headers['Authorization'] = `Token ${token}`
            }

            const { data: register, pending, error } = await useAsyncData('deleteSurvey', () => $cmsApi('/api/surveys/' + id, config))

            if (error.value) {
                let warnMessage = null
                for (const [key, value] of Object.entries(error._value.data)) {
                    warnMessage = warnMessage ? `${warnMessage} \n\n ${key}: ${value}` : `${key}: ${value}`
                }
                // Notification
                global.negativeNotify(warnMessage)

            }
            else {
                // Notification
                global.succesNotify('deleteSurvey complete')
                this.id = 1
                await navigateTo('/design')
            }

        },
    }
})