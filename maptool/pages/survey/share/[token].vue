<template>
    <NuxtLayout name="default">
        <div class="share-container">
            <!-- Loading state -->
            <div v-if="isLoading" class="text-center py-16">
                <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
                <p class="mt-4 text-grey-darken-1">Loading survey...</p>
            </div>

            <!-- Error state: Link invalid or expired -->
            <div v-else-if="error" class="text-center py-16">
                <v-icon icon="mdi-link-off" color="error" size="80"></v-icon>
                <h2 class="text-h5 mt-4">{{ errorTitle }}</h2>
                <p class="text-body-1 mt-2 text-grey-darken-1">{{ errorMessage }}</p>
                
                <!-- Login option if auth required -->
                <div v-if="requiresAuth && !isAuthenticated" class="mt-6">
                    <v-btn color="primary" variant="outlined" @click="redirectToLogin">
                        <v-icon icon="mdi-login" class="mr-2"></v-icon>
                        Login to Access
                    </v-btn>
                </div>
                
                <div class="mt-6">
                    <v-btn variant="text" to="/">
                        <v-icon icon="mdi-home" class="mr-2"></v-icon>
                        Go to Home
                    </v-btn>
                </div>
            </div>

            <!-- Survey loaded successfully -->
            <div v-else-if="survey" class="survey-content">
                <v-card class="survey-card" variant="outlined">
                    <v-card-title class="text-h5">{{ survey.name }}</v-card-title>
                    <v-card-subtitle v-if="survey.description">
                        {{ survey.description }}
                    </v-card-subtitle>
                    
                    <v-card-text>
                        <v-alert 
                            v-if="isExpiringSoon" 
                            type="warning" 
                            variant="tonal" 
                            class="mb-4"
                        >
                            This survey will expire soon. Please complete it before {{ formatDate(survey.expire_date) }}.
                        </v-alert>
                        
                        <p class="text-body-1">
                            This survey has <strong>{{ questionCount }}</strong> question(s).
                        </p>
                    </v-card-text>
                    
                    <v-card-actions>
                        <v-btn 
                            color="primary" 
                            variant="elevated" 
                            size="large"
                            @click="startSurvey"
                        >
                            <v-icon icon="mdi-play" class="mr-2"></v-icon>
                            Start Survey
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </div>
        </div>
    </NuxtLayout>
</template>

<script setup>
import { useSurveyStore } from '~/stores/survey'
import { useUserStore } from '~/stores/user'
import { useGlobalStore } from '~/stores/global'

const route = useRoute()
const router = useRouter()
const surveyStore = useSurveyStore()
const userStore = useUserStore()
const globalStore = useGlobalStore()

const isLoading = ref(true)
const error = ref(false)
const errorTitle = ref('')
const errorMessage = ref('')
const requiresAuth = ref(false)
const survey = ref(null)
const questions = ref([])

const isAuthenticated = computed(() => userStore.isAuthenticated)
const questionCount = computed(() => questions.value?.length || 0)

const isExpiringSoon = computed(() => {
    if (!survey.value?.expire_date) return false
    const expireDate = new Date(survey.value.expire_date)
    const now = new Date()
    const threeDays = 3 * 24 * 60 * 60 * 1000
    return (expireDate - now) < threeDays && (expireDate - now) > 0
})

const token = computed(() => route.params.token)

onMounted(async () => {
    // Try to load user session first
    if (process.client) {
        await userStore.loadUser()
    }
    
    await loadSurveyViaShareableLink()
})

const loadSurveyViaShareableLink = async () => {
    isLoading.value = true
    error.value = false
    
    try {
        // Access survey via shareable link
        const result = await surveyStore.accessSurveyViaShareableLink(token.value)
        
        if (!result.success) {
            handleError(result.error)
            return
        }
        
        survey.value = result.survey
        
        // Also fetch questions
        const questionsResult = await surveyStore.getQuestionsViaShareableLink(token.value)
        if (questionsResult.success) {
            questions.value = questionsResult.questions
        }
    } catch (e) {
        console.error('Error loading survey via shareable link:', e)
        handleError(e)
    } finally {
        isLoading.value = false
    }
}

const handleError = (err) => {
    error.value = true
    
    const statusCode = err?.statusCode || err?.data?.statusCode
    
    if (statusCode === 401) {
        // Authentication required
        requiresAuth.value = true
        errorTitle.value = 'Login Required'
        errorMessage.value = 'This survey requires you to be logged in. Please login to continue.'
    } else if (statusCode === 403) {
        errorTitle.value = 'Access Denied'
        errorMessage.value = 'You do not have permission to access this survey.'
    } else if (statusCode === 404 || statusCode === 410) {
        errorTitle.value = 'Link Invalid or Expired'
        errorMessage.value = 'This shareable link is no longer valid. It may have expired or been disabled by the survey creator.'
    } else {
        errorTitle.value = 'Something Went Wrong'
        errorMessage.value = 'Unable to load the survey. Please try again later or contact the survey creator.'
    }
}

const redirectToLogin = () => {
    // Store the current URL to redirect back after login
    if (process.client) {
        localStorage.setItem('redirectAfterLogin', route.fullPath)
    }
    router.push('/login')
}

const startSurvey = () => {
    if (survey.value && survey.value.id) {
        // Store the shareable token for use when submitting responses
        if (process.client) {
            localStorage.setItem('shareableToken', token.value)
        }
        // Navigate to the first question
        router.push(`/survey/${survey.value.id}/1`)
    }
}

const formatDate = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric'
    })
}
</script>

<style lang="scss" scoped>
.share-container {
    max-width: 600px;
    margin: 0 auto;
    padding: 32px 16px;
}

.survey-card {
    padding: 16px;
}

.py-16 {
    padding-top: 64px;
    padding-bottom: 64px;
}
</style>

