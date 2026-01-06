import { defineStore } from 'pinia'
import { useGlobalStore } from './global'

// Base URL for auth API (direct client-side requests to include cookies)
const AUTH_API_BASE = 'http://localhost:8000/_allauth/browser/v1/auth'
const CMS_API_BASE = 'http://localhost:8000/voice/v3'

export const useUserStore = defineStore('user', {
    state: () => {
        return {
            userData: {
                accessToken: null,
                refreshToken: null,
                isAuthenticated: false,
                pending: false,
                error: '',
                emailVerificationRequired: false,
                user: {
                    id: null,
                    url: '',
                    email: '',
                },
            },
            register: {
                errorMessage: '',
                success: '',
            },
            csrfToken: null,
        }
    },
    getters: {
        isAuthenticated: (state) => state.userData.isAuthenticated,
        getAuthToken: (state) => process.client ? localStorage.getItem('accessToken') : state.userData.accessToken,
        getRefreshToken: (state) => process.client ? localStorage.getItem('refreshToken') : state.userData.refreshToken,
        needsEmailVerification: (state) => state.userData.emailVerificationRequired,
    },
    actions: {
        /**
         * Fetch CSRF token from the backend
         * This sets the CSRF cookie and returns the token
         */
        async ensureCsrfToken() {
            if (!process.client) return null
            
            // First check if we have a CSRF token in cookies
            let csrfToken = this.getCookieSync('csrftoken')
            
            if (!csrfToken) {
                try {
                    // Fetch CSRF token from backend - this sets the cookie
                    // Use direct $fetch to ensure cookies are handled properly
                    const response = await $fetch(`${CMS_API_BASE}/csrf/`, {
                        method: 'GET',
                        credentials: 'include',
                    })
                    
                    // The cookie should now be set, read it
                    csrfToken = this.getCookieSync('csrftoken')
                    
                    // Also store the token from response if available
                    if (response?.csrf_token) {
                        this.csrfToken = response.csrf_token
                        csrfToken = response.csrf_token
                    }
                } catch (e) {
                    console.error('Failed to fetch CSRF token:', e)
                }
            }
            
            this.csrfToken = csrfToken
            return csrfToken
        },

        /**
         * Get CSRF token synchronously from cookie
         */
        getCookieSync(name) {
            if (!process.client) return null
            
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        },

        /**
         * See if user is logged-in
         * Remember this only works client side, make sure to use `if (process.client) {}` or the `onMounted()` hook in a vue component
         */
        async loadUser() {
            this.userData.error = ''
            this.userData.pending = true
            const token = this.userData.accessToken || localStorage.getItem('accessToken')

            if (!token) {
                this.userData.pending = false
                this.userData.isAuthenticated = false
                return
            }

            const csrfToken = await this.ensureCsrfToken()

            try {
                // django-allauth headless endpoint for getting current session/user
                // Use direct $fetch to ensure cookies are handled properly
                const response = await $fetch(`${AUTH_API_BASE}/session`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                        ...(csrfToken && { 'X-CSRFToken': csrfToken }),
                    },
                    credentials: 'include',
                })
                
                if (response?.data?.user) {
                    this.userData = {
                        ...this.userData,
                        isAuthenticated: true,
                        user: {
                            id: response.data.user.id,
                            email: response.data.user.email,
                            url: response.data.user.url || '',
                        },
                    }
                } else {
                    this.resetUser()
                    this.userData.isAuthenticated = false
                }
            } catch (error) {
                console.log('loadUser error //> ', error)
                // Try to refresh token on 401
                if (error?.statusCode === 401) {
                    const refreshed = await this.refreshAccessToken()
                    if (refreshed) {
                        // Retry loadUser after successful refresh
                        return await this.loadUser()
                    }
                }
                this.resetUser()
                this.userData.error = error
                this.userData.isAuthenticated = false
            } finally {
                this.userData.pending = false
            }
        },

        /**
         * Refresh the access token using the refresh token
         */
        async refreshAccessToken() {
            const refreshToken = this.userData.refreshToken || localStorage.getItem('refreshToken')
            
            if (!refreshToken) {
                return false
            }

            try {
                // Use simplejwt token refresh endpoint
                const response = await $fetch('http://localhost:8000/api/token/refresh/', {
                    method: 'POST',
                    body: { refresh: refreshToken },
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                })

                if (response?.access) {
                    this.userData.accessToken = response.access
                    localStorage.setItem('accessToken', response.access)
                    
                    // If new refresh token is provided, update it
                    if (response?.refresh) {
                        this.userData.refreshToken = response.refresh
                        localStorage.setItem('refreshToken', response.refresh)
                    }
                    return true
                }
            } catch (error) {
                console.log('Token refresh failed:', error)
                // Clear tokens on refresh failure
                this.clearTokens()
            }
            return false
        },

        /**
         * Clear all stored tokens
         */
        clearTokens() {
            this.userData.accessToken = null
            this.userData.refreshToken = null
            if (process.client) {
                localStorage.removeItem('accessToken')
                localStorage.removeItem('refreshToken')
            }
        },

        /**
         * Register user with email and password
         * @param {email, password} body 
         */
        async registerUser(body) {
            const global = useGlobalStore()

            // Ensure we have a CSRF token before making the request
            const csrfToken = await this.ensureCsrfToken()

            try {
                // django-allauth headless signup endpoint
                // Use direct $fetch to ensure cookies are handled properly
                // Headless API expects 'password', not 'password1'/'password2'
                const res = await $fetch(`${AUTH_API_BASE}/signup`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...(csrfToken && { 'X-CSRFToken': csrfToken }),
                    },
                    body: {
                        email: body.email,
                        password: body.password,
                    },
                    credentials: 'include',
                })

                // Check response - allauth headless returns different flows
                // Status 401 with verify_email pending means user created, needs verification
                if (res?.status === 401 && res?.data?.flows) {
                    const verifyFlow = res.data.flows.find(f => f.id === 'verify_email')
                    if (verifyFlow?.is_pending) {
                        // User created, email verification required
                        this.userData.emailVerificationRequired = true
                        this.register.success = true
                        global.succes('Registration complete! Please check your email to verify your account.')
                        await navigateTo('/login?verify=true')
                        return
                    }
                }

                // Status 200 with user data means immediate login (if no email verification)
                if (res?.data?.user) {
                    this.register.success = true
                    if (res?.meta?.access_token) {
                        // JWT tokens available - user is fully registered and logged in
                        this.userData.isAuthenticated = true
                        this.userData.accessToken = res.meta.access_token
                        localStorage.setItem('accessToken', res.meta.access_token)
                        global.succes('Registration complete!')
                        await navigateTo('/design')
                    } else {
                        // Email verification might still be required
                        this.userData.emailVerificationRequired = true
                        global.succes('Registration complete! Please check your email to verify your account.')
                        await navigateTo('/login?verify=true')
                    }
                }
            } catch (e) {
                console.error('Register error:', e)

                // Check if this is actually a success case (401 with verify_email pending)
                // $fetch throws for non-2xx status codes, but 401 with pending verification is expected
                if (e?.data?.status === 401 && e?.data?.data?.flows) {
                    const verifyFlow = e.data.data.flows.find(f => f.id === 'verify_email')
                    if (verifyFlow?.is_pending) {
                        // User created successfully, email verification required
                        this.userData.emailVerificationRequired = true
                        this.register.success = true
                        global.succes('Registration complete! Please check your email to verify your account.')
                        await navigateTo('/login?verify=true')
                        return
                    }
                }

                let warnMessage = null
                if (e?.data?.errors) {
                    // django-allauth error format
                    for (const error of e.data.errors) {
                        warnMessage = warnMessage ? `${warnMessage}\n${error.message}` : error.message
                    }
                } else if (e?.data?.data) {
                    // Legacy format
                    for (const [key, value] of Object.entries(e.data.data)) {
                        warnMessage = warnMessage ? `${warnMessage}\n${key}: ${value}` : `${key}: ${value}`
                    }
                } else {
                    warnMessage = 'Registration failed. Please try again.'
                }

                this.userData.isAuthenticated = false
                global.warning(warnMessage)
            }
        },

        /**
         * Login user with email and password
         * @param {string} email 
         * @param {string} password 
         */
        async loginUser(email, password) {
            const global = useGlobalStore()
            this.userData.error = ''
            this.userData.pending = true

            // Ensure we have a CSRF token before making the request
            const csrfToken = await this.ensureCsrfToken()

            try {
                // django-allauth headless login endpoint
                // Use direct $fetch to ensure cookies are handled properly
                const res = await $fetch(`${AUTH_API_BASE}/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...(csrfToken && { 'X-CSRFToken': csrfToken }),
                    },
                    body: {
                        email,
                        password,
                    },
                    credentials: 'include',
                })

                // Check if email verification is required
                if (res?.status === 401 && res?.data?.flows) {
                    const verifyFlow = res.data.flows.find(f => f.id === 'verify_email')
                    if (verifyFlow) {
                        this.userData.emailVerificationRequired = true
                        global.warning('Please verify your email before logging in.')
                        this.userData.pending = false
                        return
                    }
                }

                // Successful login - extract tokens
                if (res?.meta?.access_token) {
                    // JWT tokens from allauth headless
                    this.userData = {
                        ...this.userData,
                        isAuthenticated: true,
                        accessToken: res.meta.access_token,
                        refreshToken: res.meta.refresh_token || null,
                        user: res.data?.user || {},
                    }
                    localStorage.setItem('accessToken', res.meta.access_token)
                    if (res.meta.refresh_token) {
                        localStorage.setItem('refreshToken', res.meta.refresh_token)
                    }

                    await navigateTo('/design')
                    global.succes('Login complete')
                } else if (res?.data?.user) {
                    // Session-based auth fallback
                    this.userData = {
                        ...this.userData,
                        isAuthenticated: true,
                        user: res.data.user,
                    }
                    await navigateTo('/design')
                    global.succes('Login complete')
                }
            } catch (e) {
                console.error('Login error:', e)

                this.userData.isAuthenticated = false

                let warnMessage = null
                if (e?.data?.errors) {
                    // django-allauth error format
                    for (const error of e.data.errors) {
                        warnMessage = warnMessage ? `${warnMessage}\n${error.message}` : error.message
                    }
                } else if (e?.data?.data?.non_field_errors) {
                    warnMessage = e.data.data.non_field_errors[0]
                } else {
                    warnMessage = 'Something went wrong with the login'
                }
                
                global.warning(warnMessage)
            } finally {
                this.userData.pending = false
            }
        },

        /**
         * User logout
         */
        async logout() {
            const global = useGlobalStore()
            const token = this.userData.accessToken || localStorage.getItem('accessToken')

            if (!token) {
                this.resetUser()
                global.info('You are already logged-out')
                return
            }

            const csrfToken = await this.ensureCsrfToken()

            try {
                // django-allauth headless logout endpoint (uses DELETE on session)
                // Use direct $fetch to ensure cookies are handled properly
                await $fetch(`${AUTH_API_BASE}/session`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                        ...(csrfToken && { 'X-CSRFToken': csrfToken }),
                    },
                    credentials: 'include',
                })
                this.clearTokens()
                this.$reset()
                await navigateTo('/')
                global.succes('Logged-out successfully')
            } catch (err) {
                console.error('Logout error:', err)
                // Clear tokens anyway on error
                this.clearTokens()
                this.$reset()
                await navigateTo('/')
                global.info('Logged out')
            }
        },

        /**
         * Resend email verification
         */
        async resendVerificationEmail(email) {
            const global = useGlobalStore()
            const csrfToken = await this.ensureCsrfToken()

            try {
                await $fetch(`${AUTH_API_BASE}/email/verify/resend`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...(csrfToken && { 'X-CSRFToken': csrfToken }),
                    },
                    body: { email },
                    credentials: 'include',
                })
                global.succes('Verification email sent! Please check your inbox.')
            } catch (e) {
                console.error('Resend verification error:', e)
                global.warning('Failed to resend verification email. Please try again.')
            }
        },

        /**
         * Verify email with token
         */
        async verifyEmail(key) {
            const global = useGlobalStore()
            const csrfToken = await this.ensureCsrfToken()

            try {
                await $fetch(`${AUTH_API_BASE}/email/verify`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...(csrfToken && { 'X-CSRFToken': csrfToken }),
                    },
                    body: { key },
                    credentials: 'include',
                })
                
                this.userData.emailVerificationRequired = false
                global.succes('Email verified successfully! You can now log in.')
                await navigateTo('/login')
                return true
            } catch (e) {
                console.error('Email verification error:', e)
                global.warning('Email verification failed. The link may be expired or invalid.')
                return false
            }
        },

        /**
         * Resets all store values to initial data
         */
        async resetUser() {
            this.clearTokens()
            this.$reset()
        },

        /**
         * Get the CSRF token in the cookie stored in the browser (async version for compatibility)
         */
        async getCookie(name) {
            return this.getCookieSync(name)
        }
    },
})
