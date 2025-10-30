<template>
  <div class="error-page">
    <v-container class="fill-height">
      <v-row justify="center" align="center" class="h-100">
        <v-col cols="12" sm="8" md="6">
          <v-card class="text-center pa-8">
            <v-card-title class="text-h4 mb-4">
              <v-icon x-large color="error" class="mb-2">mdi-alert-circle</v-icon>
              <div>Oops! Something went wrong</div>
            </v-card-title>

            <v-card-text class="text-body1 mb-6">
              <p class="mb-4">
                {{ error.message || 'We encountered an unexpected error. Please try again.' }}
              </p>
              <p class="text-caption text-grey">
                Error code: {{ error.statusCode || 'Unknown' }}
              </p>
            </v-card-text>

            <v-card-actions class="justify-center gap-2">
              <NuxtLink to="/" class="text-none">
                <v-btn color="primary" variant="elevated">
                  <v-icon start>mdi-home</v-icon>
                  Back to Home
                </v-btn>
              </NuxtLink>
              <v-btn
                color="secondary"
                variant="outlined"
                @click="clearError"
              >
                <v-icon start>mdi-reload</v-icon>
                Try Again
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
defineProps({
  error: {
    type: Object,
    default: () => ({
      message: 'An unexpected error occurred',
      statusCode: 500
    })
  }
})

const emit = defineEmits(['clearError'])

const clearError = () => {
  emit('clearError')
}
</script>

<style scoped>
.error-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fill-height {
  min-height: 100%;
}

.h-100 {
  height: 100%;
}

.gap-2 {
  gap: 8px;
}
</style>
