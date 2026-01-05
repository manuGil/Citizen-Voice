# Authentication Integration Plan

## Overview
This plan outlines the integration of django-allauth headless authentication into the CitizenVoice application, with JWT authentication, proper survey filtering, and user-specific access controls.

## Requirements Summary
1. **Authentication Method**: django-allauth headless (Option B)
2. **Survey Listing**: All public surveys + user's own surveys (Option B)
3. **Private Surveys**: Only visible/accessible to survey designer (Option B)
4. **Survey Creation**: Always requires authentication (Option A)
5. **Auth Token**: Switch to JWT immediately (Option B - immediate switch)
6. **Email Verification**: Mandatory for all new accounts
7. **User Migration**: No migration needed for existing users

## django-allauth Headless Endpoints

Based on django-allauth headless API structure, the following endpoints are available at `/_allauth/browser/v1/auth/`:

### Authentication Endpoints
- **Login**: `POST /_allauth/browser/v1/auth/login/`
- **Signup/Register**: `POST /_allauth/browser/v1/auth/signup/`
- **Logout**: `POST /_allauth/browser/v1/auth/logout/`
- **User Details**: `GET /_allauth/browser/v1/auth/user/`
- **Update User**: `PATCH /_allauth/browser/v1/auth/user/`

### Email Verification Endpoints
- **Request Email Verification**: `POST /_allauth/browser/v1/auth/email/verify/`
- **Confirm Email**: `POST /_allauth/browser/v1/auth/email/confirm/`
- **Resend Verification**: `POST /_allauth/browser/v1/auth/email/resend/`

### Password Management Endpoints
- **Password Reset Request**: `POST /_allauth/browser/v1/auth/password/reset/`
- **Password Reset Confirm**: `POST /_allauth/browser/v1/auth/password/reset/confirm/`
- **Change Password**: `POST /_allauth/browser/v1/auth/password/change/`

### Token Endpoints (JWT)
- **Token Obtain**: `POST /_allauth/browser/v1/auth/token/` (returns access + refresh tokens)
- **Token Refresh**: `POST /_allauth/browser/v1/auth/token/refresh/`
- **Token Verify**: `POST /_allauth/browser/v1/auth/token/verify/`

### OpenAPI Documentation
- **OpenAPI Schema**: `GET /_allauth/openapi.html` (already configured in settings)

**Note**: These endpoints follow django-allauth headless conventions and are OpenAPI-compliant. The exact request/response formats should be verified against the OpenAPI schema at `/_allauth/openapi.html`.

---

## Phase 1: Backend Configuration (Django)

### 1.1 Configure JWT Authentication with django-allauth Headless

**Files to modify:**
- `citizenvoice/citizenvoice/settings.py`

**Changes:**
1. Add JWT authentication classes to REST_FRAMEWORK settings (immediate switch, no transition)
2. Configure django-allauth headless to use JWT tokens
3. Add JWT settings (access/refresh token lifetimes)
4. Configure CORS to allow JWT tokens in headers
5. Configure mandatory email verification
6. Remove or disable dj-rest-auth Token authentication

**Details:**
```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",  # Keep for admin
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
}

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
}

# django-allauth Configuration
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # REQUIRED: Mandatory email verification
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

# django-allauth Headless Configuration
HEADLESS_ONLY = True  # Use headless mode only
HEADLESS_TOKEN_AUTHENTICATION = True  # Enable JWT token authentication

# Email Configuration (for email verification)
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"  # Development
EMAIL_FILE_PATH = BASE_DIR / "emails"
# For production, configure SMTP:
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
# DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@citizenvoice.org")
```

### 1.2 Update Survey ViewSet Filtering Logic

**Files to modify:**
- `citizenvoice/voice/views.py`

**Changes:**
1. Update `get_queryset()` in `SurveyViewSet` to filter based on authentication:
   - If authenticated: Return public surveys (`is_published=True`, `need_logged_user=False`) + user's own surveys
   - If not authenticated: Return only public surveys (`is_published=True`, `need_logged_user=False`)
   - Private surveys (`need_logged_user=True`) should only be visible to their designer

2. Fix `my_surveys` action to properly handle authentication

3. Update `get_questions_of_survey` to check:
   - If survey is published and public: allow access
   - If survey is private (`need_logged_user=True`): only allow designer
   - If survey is not published: only allow designer

**Implementation:**
```python
def get_queryset(self):
    """
    Returns surveys based on user authentication:
    - Authenticated users: public surveys + their own surveys
    - Anonymous users: only public surveys
    - Private surveys (need_logged_user=True) only visible to designer
    """
    user = self.request.user
    now = timezone.now()
    
    # Base queryset: published and not expired
    base_queryset = Survey.objects.filter(
        is_published=True,
        expire_date__gte=now
    )
    
    if user.is_authenticated:
        # Authenticated users see:
        # 1. Public surveys (need_logged_user=False)
        # 2. Their own surveys (regardless of need_logged_user)
        public_surveys = base_queryset.filter(need_logged_user=False)
        own_surveys = Survey.objects.filter(designer=user)
        
        # Combine and remove duplicates
        queryset = (public_surveys | own_surveys).distinct().order_by("name")
    else:
        # Anonymous users only see public surveys
        queryset = base_queryset.filter(need_logged_user=False).order_by("name")
    
    return queryset
```

### 1.3 Update Permissions for Private Surveys

**Files to modify:**
- `citizenvoice/voice/permissions.py`
- `citizenvoice/voice/views.py`

**Changes:**
1. Create new permission class for private survey access
2. Apply to survey detail and question endpoints

**New Permission Class:**
```python
class CanAccessSurvey(permissions.BasePermission):
    """
    Permission to access surveys:
    - Public surveys: anyone can access
    - Private surveys: only designer can access
    """
    def has_object_permission(self, request, view, obj):
        # Public surveys are accessible to everyone
        if not obj.need_logged_user:
            return True
        
        # Private surveys require authentication and ownership
        if not request.user.is_authenticated:
            return False
        
        return obj.designer == request.user
```

### 1.4 Ensure Survey Creation Requires Authentication

**Files to modify:**
- `citizenvoice/voice/views.py`

**Changes:**
1. Add `@permission_classes([IsAuthenticated])` to `create_survey` action
2. Verify that anonymous users cannot create surveys

### 1.5 Update Response Submission for Private Surveys

**Files to modify:**
- `citizenvoice/voice/views.py` (ResponseViewSet)

**Changes:**
1. Check if survey requires authentication before allowing response submission
2. Ensure only authenticated users can submit to private surveys

---

## Phase 1.6: Shareable Link Feature for Surveys

### Overview
Allow survey designers to create shareable links for their surveys, enabling controlled access to private surveys. Links can be configured to allow anonymous access or require authentication.

### 1.6.1 Database Schema Updates

**Files to modify:**
- `citizenvoice/voice/models/survey.py`
- Create migration file

**Changes:**
1. Add new fields to Survey model:
   - `shareable_token` - CharField, unique, indexed, for secure link token
   - `shareable_link_enabled` - BooleanField, default=False, enables/disables shareable link
   - `shareable_link_requires_auth` - BooleanField, default=False, requires authentication for link access
   - `shareable_link_created_at` - DateTimeField, auto_now_add, tracks when link was created
   - `shareable_link_expires_at` - DateTimeField, nullable, optional expiration for link

2. Update `public_url` field:
   - Keep existing field for backward compatibility
   - Mark as deprecated in favor of shareable_token-based URLs
   - Or remove if not used elsewhere

**Security Considerations:**
- Use `secrets.token_urlsafe(32)` or similar for token generation (cryptographically secure)
- Token should be at least 32 characters long
- Add database index on `shareable_token` for performance
- Consider token rotation capability (regenerate token)

**Migration Strategy:**
- Create migration to add new fields
- Set default values for existing surveys (shareable_link_enabled=False)
- Generate tokens for surveys that already have public_url (if needed)

### 1.6.2 Backend API Endpoints

**Files to modify:**
- `citizenvoice/voice/views.py` (SurveyViewSet)
- `citizenvoice/voice/urls.py` (if needed)
- `citizenvoice/voice/serializers.py`

**New Endpoints:**

1. **Generate/Regenerate Shareable Link**
   - `POST /voice/v3/surveys/{id}/generate-shareable-link/`
   - Requires: Survey designer authentication
   - Request body: `{"requires_auth": true/false, "expires_at": "2024-12-31T23:59:59Z" (optional)}`
   - Response: `{"shareable_token": "...", "shareable_url": "...", "requires_auth": true/false}`
   - Action: Generates new token or regenerates existing one

2. **Disable Shareable Link**
   - `POST /voice/v3/surveys/{id}/disable-shareable-link/`
   - Requires: Survey designer authentication
   - Action: Sets `shareable_link_enabled=False`, invalidates link

3. **Access Survey via Shareable Link**
   - `GET /voice/v3/surveys/share/{token}/`
   - No authentication required (unless link requires auth)
   - Returns: Survey details if token is valid and link is enabled
   - Validates: token exists, link enabled, not expired, survey not expired

4. **Get Survey Questions via Shareable Link**
   - `GET /voice/v3/surveys/share/{token}/questions/`
   - No authentication required (unless link requires auth)
   - Returns: Questions for survey accessible via shareable link

**Implementation Details:**
- Token validation helper function
- Check link expiration
- Check survey expiration
- Respect `shareable_link_requires_auth` setting
- Rate limiting on shareable link endpoints (prevent brute force)

### 1.6.3 Update Permissions for Shareable Links

**Files to modify:**
- `citizenvoice/voice/permissions.py`
- `citizenvoice/voice/views.py`

**Changes:**
1. Create new permission class `CanAccessViaShareableLink`:
   - Checks if request has valid shareable token
   - Validates token, link enabled, expiration
   - Respects authentication requirement

2. Update `CanAccessSurvey` permission:
   - Add check for shareable link access
   - Allow access if valid shareable token is provided
   - Maintain existing logic for normal access

3. Create custom view/action for shareable link access:
   - Bypass normal permission checks
   - Use token-based permission instead

**Permission Logic:**
```python
# Pseudo-code
if shareable_token_provided:
    if token_valid and link_enabled and not_expired:
        if link_requires_auth and not user.is_authenticated:
            return 401 (redirect to login)
        return True (allow access)
    return False (invalid token)
else:
    # Use existing permission logic
    return existing_can_access_survey_logic()
```

### 1.6.4 Update Response Submission for Shareable Links

**Files to modify:**
- `citizenvoice/voice/views.py` (ResponseViewSet)

**Changes:**
1. Allow response creation via shareable link:
   - Accept shareable token in request
   - Validate token and link access
   - Create response even if survey is private
   - Link response to survey via token validation

2. Update response submission endpoint:
   - Accept optional `shareable_token` parameter
   - Validate token if provided
   - Allow anonymous responses if link doesn't require auth

**Security:**
- Validate token on every request
- Prevent token reuse abuse (rate limiting)
- Log access attempts for security monitoring

### 1.6.5 Serializer Updates

**Files to modify:**
- `citizenvoice/voice/serializers.py`

**Changes:**
1. Update `SurveySerializer`:
   - Add `shareable_token` field (read-only, only for designer)
   - Add `shareable_link_enabled` field
   - Add `shareable_link_requires_auth` field
   - Add `shareable_url` computed field (read-only)
   - Add `shareable_link_created_at` field
   - Add `shareable_link_expires_at` field

2. Create `ShareableLinkSerializer`:
   - For generating/managing shareable links
   - Includes token, URL, settings

3. Update `ResponseSerializer`:
   - Add optional `shareable_token` field for link-based submissions

### 1.6.6 Frontend Updates (Maptool)

**Files to modify/create:**
- `maptool/pages/design/surveys/[_id]/index.vue` (survey management page)
- `maptool/pages/survey/share/[token].vue` (new page for shareable link access)
- `maptool/stores/survey.js`
- `maptool/components/` (new component for shareable link management)

**Changes:**

1. **Survey Management UI:**
   - Add "Shareable Link" section in survey edit page
   - Button to generate/enable shareable link
   - Toggle for "Require authentication"
   - Display shareable URL (copyable)
   - Option to disable/regenerate link
   - Show link expiration date if set

2. **Shareable Link Access Page:**
   - Route: `/survey/share/:token`
   - Validate token on page load
   - Show survey details
   - If requires auth: redirect to login, then return to survey
   - Display questions and allow response submission
   - Handle expired/invalid tokens gracefully

3. **Survey Store Updates:**
   - Add `generateShareableLink(surveyId, options)` method
   - Add `disableShareableLink(surveyId)` method
   - Add `getSurveyByShareableToken(token)` method
   - Add `submitResponseViaShareableLink(token, responseData)` method

4. **Response Submission:**
   - Update response submission to include shareable token if present
   - Handle anonymous responses for non-auth-required links

### 1.6.7 Security Best Practices

**Implementation Requirements:**

1. **Token Generation:**
   - Use `secrets.token_urlsafe(32)` (Python) or equivalent
   - Minimum 32 characters, URL-safe
   - Cryptographically secure random generation
   - Store hashed tokens in database (optional, for extra security)

2. **Token Validation:**
   - Validate token format before database lookup
   - Use database index on token field
   - Implement rate limiting on token validation endpoints
   - Log failed token attempts (security monitoring)

3. **Access Control:**
   - Validate token on every request (no caching of validation)
   - Check link expiration
   - Check survey expiration
   - Respect authentication requirements
   - Prevent token enumeration attacks

4. **Rate Limiting:**
   - Limit requests per IP on shareable link endpoints
   - Limit token validation attempts
   - Use Django REST Framework throttling

5. **Audit Logging:**
   - Log shareable link generation/disable events
   - Log access attempts (successful and failed)
   - Track response submissions via shareable links

6. **Token Rotation:**
   - Allow designers to regenerate tokens
   - Invalidate old tokens when regenerating
   - Notify if token is being used (optional)

### 1.6.8 URL Structure

**Shareable Link Format:**
- Frontend: `https://maptool.example.com/survey/share/{token}`
- Backend API: `/voice/v3/surveys/share/{token}/`
- Questions API: `/voice/v3/surveys/share/{token}/questions/`

**Alternative (if using existing public_url):**
- Keep `public_url` field for backward compatibility
- Generate URL: `https://maptool.example.com/survey/{public_url}`
- Validate against `shareable_token` in database

### 1.6.9 Testing Requirements

**Unit Tests:**
- Token generation uniqueness
- Token validation logic
- Link expiration handling
- Authentication requirement enforcement
- Permission checks for shareable links
- Response submission via shareable link

**Integration Tests:**
- End-to-end shareable link generation
- Access survey via shareable link (with/without auth)
- Submit response via shareable link
- Link expiration behavior
- Token regeneration

**Security Tests:**
- Token enumeration prevention
- Rate limiting effectiveness
- Invalid token handling
- Expired link handling

---

## Phase 1.7: Testing for Shareable Link Feature

### 1.7.1 Unit Tests

**Files to create:**
- `citizenvoice/tests/test_shareable_links.py`

**Test Cases:**
1. Token generation creates unique tokens
2. Token validation works correctly
3. Link expiration is enforced
4. Authentication requirement is enforced
5. Disabled links are rejected
6. Expired surveys cannot be accessed via link
7. Response submission via shareable link works
8. Anonymous responses allowed when link doesn't require auth
9. Token regeneration invalidates old token
10. Designer can manage shareable links for own surveys only

### 1.7.2 Integration Tests

**Test Cases:**
1. Generate shareable link → Access survey → Submit response
2. Shareable link with auth requirement → Login flow → Access survey
3. Expired link cannot access survey
4. Disabled link cannot access survey
5. Token regeneration workflow

---

## Phase 2: Frontend Updates (Maptool)

### 2.1 Fix Authentication Store

**Files to modify:**
- `maptool/stores/user.js`

**Changes:**
1. Update authentication endpoints to use django-allauth headless:
   - Login: `POST /_allauth/browser/v1/auth/login/`
   - Register/Signup: `POST /_allauth/browser/v1/auth/signup/`
   - Logout: `POST /_allauth/browser/v1/auth/logout/`
   - User details: `GET /_allauth/browser/v1/auth/user/`
   - Token obtain: `POST /_allauth/browser/v1/auth/token/` (for JWT)
   - Token refresh: `POST /_allauth/browser/v1/auth/token/refresh/`

2. Fix bug in `loginUser` method (currently calls `/register/` instead of `/login/`)

3. Switch from Token to JWT immediately:
   - Remove Token authentication code
   - Store `access_token` and `refresh_token` in localStorage
   - Update Authorization header to use `Bearer {access_token}`
   - Implement automatic token refresh on 401 responses
   - Add token refresh interceptor

4. Update `loadUser` to use correct endpoint and handle JWT

5. Handle email verification flow:
   - After signup, check if email verification is required
   - Show appropriate message to user
   - Handle email verification confirmation

**Implementation notes:**
- django-allauth headless request format: `{ "email": "...", "password": "..." }`
- Response format: `{ "user": {...}, "access": "...", "refresh": "..." }` (JWT)
- CSRF tokens may still be needed for some endpoints
- JWT tokens need automatic refresh mechanism
- Email verification status should be checked after login

### 2.2 Update API Configuration

**Files to modify:**
- `maptool/nuxt.config.js`
- `maptool/stores/utils/setRequestConfig.js`
- `maptool/plugins/` (may need new plugin for token refresh)

**Changes:**
1. Update `AUTH_API_URL` to point to `/_allauth/browser/v1/auth` (already configured)
2. Update request config to use `Bearer` token format (remove `Token` format)
3. Add automatic token refresh interceptor on 401 responses
4. Create token refresh utility/plugin

**Implementation:**
```javascript
// In setRequestConfig.js
if (token) {
    config.headers['Authorization'] = `Bearer ${token}`  // Changed from Token
}

// Add token refresh interceptor
// Intercept 401 responses, refresh token, retry request
```

### 2.3 Update Survey Store

**Files to modify:**
- `maptool/stores/survey.js`

**Changes:**
1. Update `getSurveys()` to use filtered endpoint (will automatically filter based on auth)
2. Ensure `getSurveysOfCurrentUser()` works correctly
3. Add error handling for authentication failures

### 2.4 Update Survey Listing Pages

**Files to modify:**
- `maptool/pages/surveys.vue` (public survey listing)
- `maptool/pages/design/index.vue` (user's surveys)

**Changes:**
1. Ensure public surveys page shows filtered results (public + user's own)
2. Ensure design page only shows user's surveys
3. Add UI indicators for private vs public surveys
4. Handle authentication state properly

### 2.5 Update Survey Access Control

**Files to modify:**
- `maptool/pages/survey/[id]/index.vue`
- `maptool/middleware/validate-survey.js` (if exists)

**Changes:**
1. Check authentication before allowing access to private surveys
2. Redirect to login if user tries to access private survey without auth
3. Show appropriate error messages

### 2.6 Update Survey Creation Flow

**Files to modify:**
- `maptool/pages/design/surveys/create.vue` (or similar)

**Changes:**
1. Ensure authentication is required (use middleware)
2. Verify user is authenticated before allowing creation
3. Show appropriate error if not authenticated

### 2.7 Add Email Verification UI

**Files to modify:**
- `maptool/pages/register.vue` (or signup page)
- `maptool/pages/verify-email.vue` (new page)
- `maptool/stores/user.js`

**Changes:**
1. After signup, check if email verification is required
2. Show message: "Please check your email to verify your account"
3. Create email verification confirmation page
4. Handle email verification token from URL
5. Redirect to login after successful verification
6. Add "Resend verification email" functionality

**Implementation:**
- After signup, if `email_verified: false`, show verification message
- Create route: `/verify-email/:token` or `/verify-email?token=...`
- Call `POST /_allauth/browser/v1/auth/email/confirm/` with token
- Show success/error messages appropriately

---

## Phase 3: Testing & Validation

### 3.1 Backend Tests

**Test cases:**
1. Anonymous user can see public surveys
2. Anonymous user cannot see private surveys
3. Anonymous user cannot create surveys
4. Authenticated user can see public + own surveys
5. Authenticated user can see their own private surveys
6. Authenticated user cannot see other users' private surveys
7. Survey creation requires authentication
8. Private survey questions only accessible to designer
9. Response submission to private surveys requires authentication

### 3.2 Frontend Tests

**Test cases:**
1. Login/logout flow works correctly
2. JWT tokens are stored and used properly
3. Token refresh works automatically
4. Survey listing shows correct surveys based on auth state
5. Private surveys are hidden from unauthorized users
6. Survey creation requires login
7. Accessing private survey without auth redirects to login

### 3.3 Integration Tests

**Test cases:**
1. End-to-end survey creation flow
2. End-to-end survey response submission
3. User switching (login/logout) maintains correct state
4. Token expiration handling

---

## Phase 4: Migration & Deployment

### 4.1 Database Migrations

**Actions:**
- No database migrations needed (using existing User model)
- Verify existing surveys have correct `designer` and `need_logged_user` values
- Existing users can log in immediately with new JWT system (no migration needed)
- Email verification will be required for new signups only

### 4.2 Environment Variables

**New variables needed:**
- `JWT_SECRET_KEY` (optional - defaults to Django SECRET_KEY)
- `JWT_ALGORITHM` (default: HS256)
- `EMAIL_HOST_USER` (for production email sending)
- `EMAIL_HOST_PASSWORD` (for production email sending)
- `DEFAULT_FROM_EMAIL` (for production email sending)

### 4.3 Documentation Updates

**Files to update:**
- `AI_CONTEXT.md` - Update authentication section
- `CLAUDE.md` - Update authentication commands
- API documentation - Update authentication endpoints

---

## Pre-Implementation: Verify Endpoints

**Before starting implementation:**
1. Start Django development server
2. Access OpenAPI schema at: `http://localhost:8000/_allauth/openapi.html`
3. Verify exact endpoint paths, request/response formats
4. Test authentication endpoints manually (using curl/Postman)
5. Document any discrepancies between expected and actual API

**Endpoint Verification Checklist:**
- [ ] Login endpoint path and format
- [ ] Signup endpoint path and format
- [ ] JWT token response structure
- [ ] Email verification endpoint flow
- [ ] Token refresh endpoint
- [ ] User details endpoint
- [ ] Logout endpoint

## Implementation Order

### Original Authentication Integration:
1. **Verify Endpoints** (Pre-Implementation step above)
2. **Backend JWT Configuration** (Phase 1.1)
3. **Backend Survey Filtering** (Phase 1.2, 1.3)
4. **Backend Permissions** (Phase 1.4, 1.5)
5. **Frontend Authentication Store** (Phase 2.1, 2.2)
6. **Frontend Survey Integration** (Phase 2.3, 2.4, 2.5, 2.6)
7. **Email Verification UI** (Phase 2.7)
8. **Testing** (Phase 3)
9. **Documentation** (Phase 4.3)

### Shareable Link Feature (Phase 1.6):
1. **Database Schema Updates** (Phase 1.6.1)
2. **Backend API Endpoints** (Phase 1.6.2)
3. **Permission Updates** (Phase 1.6.3)
4. **Response Submission Updates** (Phase 1.6.4)
5. **Serializer Updates** (Phase 1.6.5)
6. **Frontend Shareable Link Management** (Phase 1.6.6)
7. **Frontend Shareable Link Access** (Phase 1.6.6)
8. **Testing** (Phase 1.7)

---

## Risk Mitigation

### Breaking Changes
- **Risk**: Existing Token-based auth will break immediately
- **Mitigation**: 
  - Remove all Token authentication code
  - Update frontend to use JWT immediately
  - Test thoroughly before deployment
  - Provide clear migration path for any external API consumers

### Survey Access
- **Risk**: Users may lose access to surveys they should see
- **Mitigation**: Test filtering logic thoroughly, ensure public surveys remain accessible

### Frontend Compatibility
- **Risk**: django-allauth headless API may differ from current implementation
- **Mitigation**: Test API endpoints first, adjust frontend accordingly

---

## Implementation Decisions (Confirmed)

1. **Token Migration**: ✅ Switch immediately to JWT (no transition period)
2. **Email Verification**: ✅ Mandatory for all new accounts
3. **Password Reset**: To be implemented (django-allauth headless provides endpoints)
4. **Social Login**: Available via django-allauth (Google/GitHub OAuth configured)
5. **Existing Users**: ✅ No migration needed - existing users can log in with new system

---

## Success Criteria

### Authentication Integration:
✅ Users can log in using django-allauth headless with JWT
✅ Authenticated users see: public surveys + their own surveys
✅ Anonymous users see: only public surveys
✅ Private surveys are only visible to their designer
✅ Survey creation requires authentication
✅ Survey responses to private surveys require authentication
✅ Existing functionality (public surveys, responses) continues to work
✅ No breaking changes to public API endpoints

### Shareable Link Feature:
✅ Designers can generate shareable links for their surveys
✅ Shareable links can be configured to require authentication or allow anonymous access
✅ Respondents can access surveys via shareable link
✅ Respondents can submit responses via shareable link
✅ Shareable links respect survey expiration dates
✅ Shareable links can be disabled/regenerated by designers
✅ Token-based access is secure (cryptographically secure tokens, rate limiting)
✅ Invalid/expired links are handled gracefully
✅ Shareable link access is logged for security monitoring

---

## Notes

- django-allauth headless endpoints are standardized at `/_allauth/browser/v1/auth/`
- OpenAPI schema available at `/_allauth/openapi.html` for exact request/response formats
- JWT refresh tokens should be handled automatically via interceptor
- Consider adding rate limiting for authentication endpoints
- CORS settings already configured for localhost:3000
- Email verification emails will be sent (file-based in dev, SMTP in production)
- dj-rest-auth endpoints in `authentication/urls.py` should be removed or kept disabled
- All authentication should go through django-allauth headless endpoints only

