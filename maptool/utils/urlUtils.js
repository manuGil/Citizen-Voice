/**
 * Utility functions for URL handling in the application
 */

/**
 * Converts an absolute URL to a relative path suitable for the API proxy
 * @param {string} absoluteUrl - The absolute URL to convert
 * @returns {string} - The relative path
 */
export const extractRelativePath = (absoluteUrl) => {
    try {
        // If it's already a relative path, return as-is
        if (!absoluteUrl.startsWith('http')) {
            return absoluteUrl;
        }

        const url = new URL(absoluteUrl);
        // Extract the path and remove any leading slash if it starts with /voice/v3
        let path = url.pathname;
        if (path.startsWith('/voice/v3/')) {
            path = path.substring('/voice/v3/'.length);
        } else if (path.startsWith('/')) {
            path = path.substring(1);
        }
        return path;
    } catch (error) {
        console.error('Error extracting relative path from URL:', absoluteUrl, error);
        return absoluteUrl; // Return original if parsing fails
    }
};

/**
 * Wrapper for $cmsApi that automatically handles absolute URLs by converting them to relative paths
 * @param {Function} $cmsApi - The CMS API function
 * @param {string} url - The URL to call (can be absolute or relative)
 * @param {Object} options - Request options
 * @returns {Promise} - API response
 */
export const cmsApiCall = async ($cmsApi, url, options = {}) => {
    const relativePath = extractRelativePath(url);
    return await $cmsApi(relativePath, options);
};