<template>
    <NuxtLayout name="default">
        <div class="padding-16">
            <center-div>
                <div class="q-pa-md custom-login-form">
                    <h1 class="text-h6">Create an Account</h1>
                    <p class="text-body-2 mt-2 mb-4 text-grey-darken-1">
                        Already have an account? 
                        <NuxtLink to="/login" class="text-primary">Login here</NuxtLink>
                    </p>
                    
                    <form class="mt-4" @submit="onSubmit">
                        <v-text-field 
                            class="mb-2" 
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
                            autocomplete="new-password"
                            hint="At least 8 characters"
                        ></v-text-field>

                        <v-text-field 
                            class="mb-2" 
                            name="confirmPassword"  
                            @click:append="showConfirmPass = !showConfirmPass" 
                            :append-icon="showConfirmPass ? 'mdi-eye' : 'mdi-eye-off'" 
                            :type="showConfirmPass ? 'text' : 'password'" 
                            v-model="confirmPassword" 
                            :error-messages="errorConfirmPassword"
                            label="Confirm Password"
                            autocomplete="new-password"
                        ></v-text-field>

                        <div class="flex flex-row mt-4">
                            <v-btn class="mr-4" variant="outlined" type="submit" :loading="isSubmitting">
                                Register
                            </v-btn>

                            <v-btn variant="outlined" @click="resetForm">
                                Clear
                            </v-btn>
                        </div>
                    </form>

                </div>
            </center-div>
        </div>
    </NuxtLayout>
</template>

<script setup>
import { Form, useForm, useField } from 'vee-validate';
import CenterDiv from "../layouts/centerDiv";
import { useUserStore } from "~/stores/user"
import * as yup from 'yup'

const showPass = ref(false)
const showConfirmPass = ref(false)
const isSubmitting = ref(false)
const userStore = useUserStore()

const schema = yup.object({
    email: yup.string().email('Please enter a valid email address').required('Email is required'),
    password: yup.string().required('Password is required').min(8, 'Password must be at least 8 characters'),
    confirmPassword: yup.string()
        .required('Please confirm your password')
        .oneOf([yup.ref('password')], 'Passwords must match'),
});

const { handleSubmit, resetForm } = useForm({
    validationSchema: schema,
});

// Use useField and not useFieldModel for error messages because it doesn't get triggered on mount
const { value: email, errorMessage: errorEmail } = useField('email')
const { value: password, errorMessage: errorPassword } = useField('password')
const { value: confirmPassword, errorMessage: errorConfirmPassword } = useField('confirmPassword')

const onSubmit = handleSubmit(async (values) => {
    isSubmitting.value = true
    try {
        await userStore.registerUser({ 
            email: values.email, 
            password: values.password 
        })
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
