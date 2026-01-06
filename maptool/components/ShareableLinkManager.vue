<template>
    <v-card class="shareable-link-card" variant="outlined">
        <v-card-title class="d-flex align-center">
            <v-icon icon="mdi-share-variant" class="mr-2"></v-icon>
            Shareable Link
        </v-card-title>
        
        <v-card-text>
            <!-- Link is enabled -->
            <div v-if="shareableLink.enabled">
                <v-alert type="success" variant="tonal" class="mb-4">
                    <template v-slot:title>Link Active</template>
                    Anyone with this link can access your survey.
                </v-alert>
                
                <!-- Link URL with copy button -->
                <div class="d-flex align-center mb-4">
                    <v-text-field
                        :model-value="shareableLink.url"
                        readonly
                        density="compact"
                        hide-details
                        class="flex-grow-1"
                    >
                        <template v-slot:append-inner>
                            <v-btn
                                icon="mdi-content-copy"
                                size="small"
                                variant="text"
                                @click="copyLink"
                                :loading="isCopying"
                            ></v-btn>
                        </template>
                    </v-text-field>
                </div>
                
                <!-- Link settings display -->
                <div class="text-body-2 text-grey-darken-1 mb-4">
                    <div class="d-flex align-center mb-1">
                        <v-icon :icon="shareableLink.requiresAuth ? 'mdi-lock' : 'mdi-lock-open'" size="small" class="mr-2"></v-icon>
                        <span>{{ shareableLink.requiresAuth ? 'Requires login' : 'Open to anyone' }}</span>
                    </div>
                    <div v-if="shareableLink.expiresAt" class="d-flex align-center">
                        <v-icon icon="mdi-clock-outline" size="small" class="mr-2"></v-icon>
                        <span>Expires: {{ formatDate(shareableLink.expiresAt) }}</span>
                    </div>
                </div>
                
                <!-- Actions -->
                <div class="d-flex gap-2">
                    <v-btn
                        variant="outlined"
                        color="warning"
                        @click="regenerateLink"
                        :loading="isRegenerating"
                        size="small"
                    >
                        <v-icon icon="mdi-refresh" class="mr-1"></v-icon>
                        Regenerate
                    </v-btn>
                    <v-btn
                        variant="outlined"
                        color="error"
                        @click="disableLink"
                        :loading="isDisabling"
                        size="small"
                    >
                        <v-icon icon="mdi-link-off" class="mr-1"></v-icon>
                        Disable
                    </v-btn>
                </div>
            </div>
            
            <!-- Link is not enabled -->
            <div v-else>
                <p class="text-body-2 text-grey-darken-1 mb-4">
                    Create a shareable link to let others access your survey without needing to find it in the survey list.
                </p>
                
                <!-- Options -->
                <v-switch
                    v-model="requiresAuth"
                    label="Require login to access"
                    color="primary"
                    hide-details
                    class="mb-2"
                ></v-switch>
                
                <v-select
                    v-model="expiresInDays"
                    :items="expirationOptions"
                    item-title="label"
                    item-value="value"
                    label="Link expiration"
                    density="compact"
                    variant="outlined"
                    class="mb-4"
                ></v-select>
                
                <v-btn
                    color="primary"
                    variant="outlined"
                    @click="generateLink"
                    :loading="isGenerating"
                >
                    <v-icon icon="mdi-link-plus" class="mr-1"></v-icon>
                    Generate Link
                </v-btn>
            </div>
        </v-card-text>
    </v-card>
</template>

<script setup>
import { useSurveyStore } from '~/stores/survey'
import { useGlobalStore } from '~/stores/global'

const props = defineProps({
    surveyId: {
        type: [Number, String],
        required: true
    }
})

const surveyStore = useSurveyStore()
const globalStore = useGlobalStore()

const shareableLink = computed(() => surveyStore.shareableLink)

const requiresAuth = ref(false)
const expiresInDays = ref(null)
const isGenerating = ref(false)
const isDisabling = ref(false)
const isRegenerating = ref(false)
const isCopying = ref(false)

const expirationOptions = [
    { label: 'Never expires', value: null },
    { label: '1 day', value: 1 },
    { label: '7 days', value: 7 },
    { label: '30 days', value: 30 },
    { label: '90 days', value: 90 },
]

// Load initial shareable link status
onMounted(async () => {
    await surveyStore.loadShareableLinkStatus(props.surveyId)
})

const generateLink = async () => {
    isGenerating.value = true
    try {
        await surveyStore.generateShareableLink(
            props.surveyId,
            requiresAuth.value,
            expiresInDays.value
        )
    } finally {
        isGenerating.value = false
    }
}

const disableLink = async () => {
    isDisabling.value = true
    try {
        await surveyStore.disableShareableLink(props.surveyId)
    } finally {
        isDisabling.value = false
    }
}

const regenerateLink = async () => {
    isRegenerating.value = true
    try {
        // Disable and regenerate with same settings
        await surveyStore.disableShareableLink(props.surveyId)
        await surveyStore.generateShareableLink(
            props.surveyId,
            shareableLink.value.requiresAuth,
            expiresInDays.value
        )
    } finally {
        isRegenerating.value = false
    }
}

const copyLink = async () => {
    if (!shareableLink.value.url) return
    
    isCopying.value = true
    try {
        await navigator.clipboard.writeText(shareableLink.value.url)
        globalStore.succes('Link copied to clipboard!')
    } catch (e) {
        globalStore.warning('Failed to copy link')
    } finally {
        isCopying.value = false
    }
}

const formatDate = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}
</script>

<style lang="scss" scoped>
.shareable-link-card {
    margin-top: 16px;
}

.gap-2 {
    gap: 8px;
}
</style>

