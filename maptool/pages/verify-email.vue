<template>
    <NuxtLayout name="default">
        <div class="padding-16">
            <center-div>
                <div class="q-pa-md custom-verify-form">
                    <!-- Verifying state -->
                    <div v-if="isVerifying" class="text-center">
                        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
                        <h2 class="text-h6 mt-4">Verifying your email...</h2>
                        <p class="text-body-2 mt-2 text-grey-darken-1">Please wait while we verify your email address.</p>
                    </div>

                    <!-- Success state -->
                    <div v-else-if="verificationSuccess" class="text-center">
                        <v-icon icon="mdi-check-circle" color="success" size="64"></v-icon>
                        <h2 class="text-h6 mt-4">Email Verified!</h2>
                        <p class="text-body-2 mt-2 text-grey-darken-1">
                            Your email has been successfully verified. You can now log in to your account.
                        </p>
                        <v-btn class="mt-4" color="primary" variant="outlined" to="/login">
                            Go to Login
                        </v-btn>
                    </div>

                    <!-- Error state -->
                    <div v-else-if="verificationError" class="text-center">
                        <v-icon icon="mdi-alert-circle" color="error" size="64"></v-icon>
                        <h2 class="text-h6 mt-4">Verification Failed</h2>
                        <p class="text-body-2 mt-2 text-grey-darken-1">
                            {{ errorMessage }}
                        </p>
                        <div class="mt-4">
                            <v-btn color="primary" variant="outlined" to="/login">
                                Go to Login
                            </v-btn>
                        </div>
                    </div>

                    <!-- No token - resend verification -->
                    <div v-else class="text-center">
                        <v-icon icon="mdi-email-outline" color="primary" size="64"></v-icon>
                        <h2 class="text-h6 mt-4">Verify Your Email</h2>
                        <p class="text-body-2 mt-2 text-grey-darken-1">
                            Didn't receive the verification email? Enter your email address below to resend it.
                        </p>
                        
                        <form class="mt-4" @submit.prevent="resendVerification">
                            <v-text-field 
                                v-model="resendEmail" 
                                label="Email Address"
                                type="email"
                                :error-messages="resendError"
                                :disabled="isResending"
                            ></v-text-field>
                            
                            <v-btn 
                                class="mt-2" 
                                color="primary" 
                                variant="outlined" 
                                type="submit"
                                :loading="isResending"
                            >
                                Resend Verification Email
                            </v-btn>
                        </form>
                        
                        <p class="mt-4 text-body-2">
                            <NuxtLink to="/login">Back to Login</NuxtLink>
                        </p>
                    </div>
                </div>
            </center-div>
        </div>
    </NuxtLayout>
</template>

<script setup>
import CenterDiv from "../layouts/centerDiv";
import { useUserStore } from "~/stores/user"

const route = useRoute()
const userStore = useUserStore()

const isVerifying = ref(false)
const verificationSuccess = ref(false)
const verificationError = ref(false)
const errorMessage = ref('')
const resendEmail = ref('')
const resendError = ref('')
const isResending = ref(false)

// Check for verification key in URL
onMounted(async () => {
    const key = route.query.key || route.params.key
    
    if (key) {
        isVerifying.value = true
        try {
            const success = await userStore.verifyEmail(key)
            if (success) {
                verificationSuccess.value = true
            } else {
                verificationError.value = true
                errorMessage.value = 'The verification link is invalid or has expired. Please request a new verification email.'
            }
        } catch (e) {
            verificationError.value = true
            errorMessage.value = 'An error occurred during verification. Please try again.'
        } finally {
            isVerifying.value = false
        }
    }
})

const resendVerification = async () => {
    if (!resendEmail.value) {
        resendError.value = 'Please enter your email address'
        return
    }
    
    resendError.value = ''
    isResending.value = true
    
    try {
        await userStore.resendVerificationEmail(resendEmail.value)
    } finally {
        isResending.value = false
    }
}
</script>

<style lang="scss" scoped>
.padding-16 {
    width: 100%;
    height: 100%;
    padding: 16px;
}

.custom-verify-form {
    width: 400px;
    max-width: 100%;
}
</style>

