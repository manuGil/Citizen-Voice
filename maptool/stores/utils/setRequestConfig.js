import { useUserStore } from '../user.js'

const setRequestConfig = (params = { method: "GET" }) => {
    const user = useUserStore()
    const csrftoken = user.getCookieSync('csrftoken')
    const token = user.getAuthToken

    const config = {
        headers: {},
        credentials: 'include',  // Include cookies in requests
        ...params,
    }

    // Add CSRF token for non-GET requests
    if (csrftoken && params.method !== 'GET') {
        config.headers['X-CSRFToken'] = csrftoken
    }

    // Only set Content-Type for JSON if body is not FormData
    if (params.body && !(params.body instanceof FormData)) {
        config.headers['Content-Type'] = 'application/json';
    }

    // Use Bearer token format for JWT authentication
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`
    }

    return config
}

export default setRequestConfig
