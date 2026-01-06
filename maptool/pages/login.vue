<template>
    <NuxtLayout name="default">
        <div class="custom-login-form">
            <h1 class="text-h6">Login or <br>
                <NuxtLink to="/register">Create an account</NuxtLink>
            </h1>

            <!-- Email verification message -->
            <v-alert 
                v-if="showVerificationMessage" 
                type="info" 
                variant="tonal" 
                class="mt-4"
                closable
                @click:close="showVerificationMessage = false"
            >
                <template v-slot:title>Check Your Email</template>
                Please check your email and click the verification link to activate your account.
                <template v-slot:append>
                    <v-btn 
                        variant="text" 
                        size="small" 
                        @click="navigateTo('/verify-email')"
                    >
                        Resend
                    </v-btn>
                </template>
            </v-alert>

            <form class="mt-4" @submit.prevent="onSubmit">
                <v-text-field 
                    name="email" 
                    v-model="email" 
                    :error-messages="errorEmail"
                    label="E-mail"
                    type="email"
                    autocomplete="email"
                ></v-text-field>

                <v-text-field 
                    class="mb-2" 
                    name="password"  
                    @click:append="showPass = !showPass" 
                    :append-icon="showPass ? 'mdi-eye' : 'mdi-eye-off'" 
                    :type="showPass ? 'text' : 'password'" 
                    v-model="password" 
                    :error-messages="errorPassword"
                    label="Password"
                    autocomplete="current-password"
                ></v-text-field>

                <VBtn variant="outlined" class="me-4" type="submit" :loading="isSubmitting">
                    Submit
                </VBtn>

                <v-btn variant="outlined" @click="resetForm">
                    Clear
                </v-btn>
            </form>
        </div>
    </NuxtLayout>
</template>

<script setup>
import { Form, useForm, useField } from 'vee-validate';
import CenterDiv from "../layouts/centerDiv";
import { useUserStore } from "~/stores/user"
import * as yup from 'yup'

const route = useRoute()
const showPass = ref(false)
const isSubmitting = ref(false)
const showVerificationMessage = ref(false)

// Check if coming from registration with verification required
onMounted(() => {
    if (route.query.verify === 'true') {
        showVerificationMessage.value = true
    }
})

const schema = yup.object({
    email: yup.string().email().required(),
    password: yup.string().required(),
});

const { handleSubmit, resetForm } = useForm({
    validationSchema: schema,
});

// Use useField and not useFieldModel for error messages because it doesn't get triggered on mount
const { value: email, errorMessage: errorEmail } = useField('email')
const { value: password, errorMessage: errorPassword } = useField('password')

const userStore = useUserStore()

const onSubmit = handleSubmit(async (values) => {
    isSubmitting.value = true
    try {
        await userStore.loginUser(values.email, values.password)
        
        // Check if email verification is still required
        if (userStore.needsEmailVerification) {
            showVerificationMessage.value = true
        }
    } finally {
        isSubmitting.value = false
    }
});
</script>

<style lang="scss" scoped>
.padding-16 {
    width: 100%;
    height: 100%;
    padding: 16px;
}

.custom-container {
    width: 100%;
    height: 100vh;
}

.custom-login-form {
    width: 33%;
    min-width: 300px;
}
</style>
