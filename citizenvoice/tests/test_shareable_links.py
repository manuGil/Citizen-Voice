"""
Unit tests for shareable link feature (Phase 1.6).

Critical test cases:
1. Generate shareable link (designer only)
2. Disable shareable link (designer only)
3. Access survey via shareable link (valid/invalid/expired/disabled/requires auth)
4. Get questions via shareable link
5. Submit response via shareable link
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from voice.models import Survey, Question, Response as ResponseModel
from voice.views import SurveyViewSet, ResponseViewSet
from voice.permissions import CanAccessViaShareableLink


class ShareableLinkGenerationTest(TestCase):
    """Test shareable link generation and management"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.designer = User.objects.create_user(
            username="designer", email="designer@test.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="other", email="other@test.com", password="testpass123"
        )
        self.survey = Survey.objects.create(
            name="Test Survey",
            description="Test Description",
            is_published=True,
            need_logged_user=True,
            publish_date=timezone.now() - timedelta(days=1),
            expire_date=timezone.now() + timedelta(days=30),
            designer=self.designer,
        )

    def test_generate_shareable_link_as_designer(self):
        """Designer can generate shareable link"""
        request = self.factory.post(
            f"/voice/v3/surveys/{self.survey.id}/generate-shareable-link/",
            {"requires_auth": False},
            format="json",
        )
        force_authenticate(request, user=self.designer)
        view = SurveyViewSet.as_view({"post": "generate_shareable_link"})
        response = view(request, pk=self.survey.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("shareable_token", response.data)
        self.assertIn("shareable_url", response.data)
        self.assertEqual(response.data["requires_auth"], False)

        # Verify survey was updated
        self.survey.refresh_from_db()
        self.assertTrue(self.survey.shareable_link_enabled)
        self.assertIsNotNone(self.survey.shareable_token)
        self.assertEqual(self.survey.shareable_link_requires_auth, False)

    def test_generate_shareable_link_with_expiration(self):
        """Designer can generate shareable link with expiration"""
        expires_at = timezone.now() + timedelta(days=7)
        request = self.factory.post(
            f"/voice/v3/surveys/{self.survey.id}/generate-shareable-link/",
            {
                "requires_auth": True,
                "expires_at": expires_at.isoformat(),
            },
            format="json",
        )
        force_authenticate(request, user=self.designer)
        view = SurveyViewSet.as_view({"post": "generate_shareable_link"})
        response = view(request, pk=self.survey.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.survey.refresh_from_db()
        self.assertEqual(self.survey.shareable_link_requires_auth, True)
        self.assertIsNotNone(self.survey.shareable_link_expires_at)

    def test_generate_shareable_link_as_non_designer(self):
        """Non-designer cannot generate shareable link"""
        request = self.factory.post(
            f"/voice/v3/surveys/{self.survey.id}/generate-shareable-link/",
            {"requires_auth": False},
            format="json",
        )
        force_authenticate(request, user=self.other_user)
        view = SurveyViewSet.as_view({"post": "generate_shareable_link"})
        response = view(request, pk=self.survey.id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_generate_shareable_link_anonymous(self):
        """Anonymous user cannot generate shareable link"""
        request = self.factory.post(
            f"/voice/v3/surveys/{self.survey.id}/generate-shareable-link/",
            {"requires_auth": False},
            format="json",
        )
        view = SurveyViewSet.as_view({"post": "generate_shareable_link"})
        response = view(request, pk=self.survey.id)

        # DRF's IsAuthenticated permission returns 403 (Forbidden) for unauthenticated users
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_disable_shareable_link_as_designer(self):
        """Designer can disable shareable link"""
        # First generate a link
        self.survey.shareable_token = self.survey.generate_shareable_token()
        self.survey.shareable_link_enabled = True
        self.survey.save()

        request = self.factory.post(
            f"/voice/v3/surveys/{self.survey.id}/disable-shareable-link/",
            format="json",
        )
        force_authenticate(request, user=self.designer)
        view = SurveyViewSet.as_view({"post": "disable_shareable_link"})
        response = view(request, pk=self.survey.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.survey.refresh_from_db()
        self.assertFalse(self.survey.shareable_link_enabled)

    def test_disable_shareable_link_as_non_designer(self):
        """Non-designer cannot disable shareable link"""
        self.survey.shareable_token = self.survey.generate_shareable_token()
        self.survey.shareable_link_enabled = True
        self.survey.save()

        request = self.factory.post(
            f"/voice/v3/surveys/{self.survey.id}/disable-shareable-link/",
            format="json",
        )
        force_authenticate(request, user=self.other_user)
        view = SurveyViewSet.as_view({"post": "disable_shareable_link"})
        response = view(request, pk=self.survey.id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ShareableLinkAccessTest(TestCase):
    """Test accessing surveys via shareable links"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.designer = User.objects.create_user(
            username="designer", email="designer@test.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="other", email="other@test.com", password="testpass123"
        )
        self.survey = Survey.objects.create(
            name="Private Survey",
            description="Private Description",
            is_published=True,
            need_logged_user=True,  # Private survey
            publish_date=timezone.now() - timedelta(days=1),
            expire_date=timezone.now() + timedelta(days=30),
            designer=self.designer,
        )
        self.survey.shareable_token = self.survey.generate_shareable_token()
        self.survey.shareable_link_enabled = True
        self.survey.shareable_link_requires_auth = False
        self.survey.save()

    def test_access_survey_via_valid_token_anonymous(self):
        """Anonymous user can access survey via valid shareable link (no auth required)"""
        request = self.factory.get(f"/voice/v3/surveys/share/{self.survey.shareable_token}/")
        view = SurveyViewSet.as_view({"get": "access_via_shareable_link"})
        response = view(request, token=self.survey.shareable_token)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.survey.name)

    def test_access_survey_via_invalid_token(self):
        """Invalid token returns 404"""
        request = self.factory.get("/voice/v3/surveys/share/invalid_token/")
        view = SurveyViewSet.as_view({"get": "access_via_shareable_link"})
        response = view(request, token="invalid_token")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_access_survey_via_disabled_link(self):
        """Disabled shareable link returns 403"""
        self.survey.shareable_link_enabled = False
        self.survey.save()

        request = self.factory.get(f"/voice/v3/surveys/share/{self.survey.shareable_token}/")
        view = SurveyViewSet.as_view({"get": "access_via_shareable_link"})
        response = view(request, token=self.survey.shareable_token)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_survey_via_expired_link(self):
        """Expired shareable link returns 403"""
        self.survey.shareable_link_expires_at = timezone.now() - timedelta(days=1)
        self.survey.save()

        request = self.factory.get(f"/voice/v3/surveys/share/{self.survey.shareable_token}/")
        view = SurveyViewSet.as_view({"get": "access_via_shareable_link"})
        response = view(request, token=self.survey.shareable_token)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_survey_via_link_requires_auth_anonymous(self):
        """Shareable link requiring auth returns 401 for anonymous user"""
        self.survey.shareable_link_requires_auth = True
        self.survey.save()

        request = self.factory.get(f"/voice/v3/surveys/share/{self.survey.shareable_token}/")
        view = SurveyViewSet.as_view({"get": "access_via_shareable_link"})
        response = view(request, token=self.survey.shareable_token)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_survey_via_link_requires_auth_authenticated(self):
        """Shareable link requiring auth allows authenticated user"""
        self.survey.shareable_link_requires_auth = True
        self.survey.save()

        request = self.factory.get(f"/voice/v3/surveys/share/{self.survey.shareable_token}/")
        force_authenticate(request, user=self.other_user)
        view = SurveyViewSet.as_view({"get": "access_via_shareable_link"})
        response = view(request, token=self.survey.shareable_token)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_questions_via_shareable_link(self):
        """Can get survey questions via shareable link"""
        # Create a question
        Question.objects.create(
            survey=self.survey,
            text="Test Question",
            question_type=Question.SHORT_TEXT,
            order=1,
        )

        request = self.factory.get(
            f"/voice/v3/surveys/share/{self.survey.shareable_token}/questions/"
        )
        view = SurveyViewSet.as_view({"get": "get_questions_via_shareable_link"})
        response = view(request, token=self.survey.shareable_token)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["text"], "Test Question")

    def test_access_survey_via_expired_survey(self):
        """Expired survey cannot be accessed via shareable link"""
        # Set survey expiration date to past
        self.survey.expire_date = timezone.now() - timedelta(days=1)
        self.survey.save()

        request = self.factory.get(f"/voice/v3/surveys/share/{self.survey.shareable_token}/")
        view = SurveyViewSet.as_view({"get": "access_via_shareable_link"})
        response = view(request, token=self.survey.shareable_token)

        # Should return 403 because survey is expired
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ShareableLinkResponseSubmissionTest(TestCase):
    """Test submitting responses via shareable links"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.designer = User.objects.create_user(
            username="designer", email="designer@test.com", password="testpass123"
        )
        self.survey = Survey.objects.create(
            name="Private Survey",
            description="Private Description",
            is_published=True,
            need_logged_user=True,  # Private survey
            publish_date=timezone.now() - timedelta(days=1),
            expire_date=timezone.now() + timedelta(days=30),
            designer=self.designer,
        )
        self.survey.shareable_token = self.survey.generate_shareable_token()
        self.survey.shareable_link_enabled = True
        self.survey.shareable_link_requires_auth = False
        self.survey.save()

        # Create a question
        self.question = Question.objects.create(
            survey=self.survey,
            text="Test Question",
            question_type=Question.SHORT_TEXT,
            order=1,
        )

    def test_submit_response_via_shareable_link_anonymous(self):
        """Anonymous user can submit response via shareable link (no auth required)"""
        # First create a response
        response_obj = ResponseModel.objects.create(
            survey=self.survey,
            respondent=None,  # Anonymous
        )

        request = self.factory.post(
            "/voice/v3/responses/submit-response/",
            {
                "responseId": str(response_obj.response_id),
                "answers": [
                    {
                        "question": self.question.id,
                        "body": "Test Answer",
                    }
                ],
                "shareable_token": self.survey.shareable_token,
            },
            format="json",
        )
        view = ResponseViewSet.as_view({"post": "submit_response"})
        response = view(request)

        # Should succeed (200 or 201) - anonymous access allowed via shareable link
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])

    def test_submit_response_via_shareable_link_invalid_token(self):
        """Invalid shareable token returns 403"""
        response_obj = ResponseModel.objects.create(
            survey=self.survey,
            respondent=None,
        )

        request = self.factory.post(
            "/voice/v3/responses/submit-response/",
            {
                "responseId": str(response_obj.response_id),
                "answers": [{"question": self.question.id, "body": "Test Answer"}],
                "shareable_token": "invalid_token",
            },
            format="json",
        )
        view = ResponseViewSet.as_view({"post": "submit_response"})
        response = view(request)

        # Invalid shareable token should return 403 (Forbidden)
        # The permission class validates the token and returns False for invalid tokens
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_submit_response_via_shareable_link_requires_auth_anonymous(self):
        """Shareable link requiring auth returns 401 for anonymous response submission"""
        self.survey.shareable_link_requires_auth = True
        self.survey.save()

        response_obj = ResponseModel.objects.create(
            survey=self.survey,
            respondent=None,
        )

        request = self.factory.post(
            "/voice/v3/responses/submit-response/",
            {
                "responseId": str(response_obj.response_id),
                "answers": [{"question": self.question.id, "body": "Test Answer"}],
                "shareable_token": self.survey.shareable_token,
            },
            format="json",
        )
        view = ResponseViewSet.as_view({"post": "submit_response"})
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_submit_response_via_shareable_link_requires_auth_authenticated(self):
        """Shareable link requiring auth allows authenticated response submission"""
        self.survey.shareable_link_requires_auth = True
        self.survey.save()

        other_user = User.objects.create_user(
            username="respondent", email="respondent@test.com", password="testpass123"
        )

        response_obj = ResponseModel.objects.create(
            survey=self.survey,
            respondent=other_user,
        )

        request = self.factory.post(
            "/voice/v3/responses/submit-response/",
            {
                "responseId": str(response_obj.response_id),
                "answers": [{"question": self.question.id, "body": "Test Answer"}],
                "shareable_token": self.survey.shareable_token,
            },
            format="json",
        )
        force_authenticate(request, user=other_user)
        view = ResponseViewSet.as_view({"post": "submit_response"})
        response = view(request)

        # Should succeed
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])


class ShareableLinkPermissionTest(TestCase):
    """Test CanAccessViaShareableLink permission class directly"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.designer = User.objects.create_user(
            username="designer", email="designer@test.com", password="testpass123"
        )
        self.survey = Survey.objects.create(
            name="Test Survey",
            description="Test Description",
            is_published=True,
            need_logged_user=True,
            publish_date=timezone.now() - timedelta(days=1),
            expire_date=timezone.now() + timedelta(days=30),
            designer=self.designer,
        )
        self.survey.shareable_token = self.survey.generate_shareable_token()
        self.survey.shareable_link_enabled = True
        self.survey.shareable_link_requires_auth = False
        self.survey.save()

    def test_permission_valid_token(self):
        """Permission allows access with valid token"""
        permission = CanAccessViaShareableLink()
        request = self.factory.get("/")
        request.user = AnonymousUser()

        # Mock view with token in kwargs
        class MockView:
            def __init__(self, token):
                self.kwargs = {"token": token}

        view = MockView(self.survey.shareable_token)
        result = permission.has_object_permission(request, view, self.survey)

        self.assertTrue(result)

    def test_permission_invalid_token(self):
        """Permission denies access with invalid token"""
        permission = CanAccessViaShareableLink()
        request = self.factory.get("/")
        request.user = AnonymousUser()

        class MockView:
            def __init__(self, token):
                self.kwargs = {"token": token}

        view = MockView("invalid_token")
        result = permission.has_object_permission(request, view, self.survey)

        self.assertFalse(result)

    def test_permission_disabled_link(self):
        """Permission denies access when link is disabled"""
        self.survey.shareable_link_enabled = False
        self.survey.save()

        permission = CanAccessViaShareableLink()
        request = self.factory.get("/")
        request.user = AnonymousUser()

        class MockView:
            def __init__(self, token):
                self.kwargs = {"token": token}

        view = MockView(self.survey.shareable_token)
        result = permission.has_object_permission(request, view, self.survey)

        self.assertFalse(result)

    def test_permission_expired_link(self):
        """Permission denies access when link is expired"""
        self.survey.shareable_link_expires_at = timezone.now() - timedelta(days=1)
        self.survey.save()

        permission = CanAccessViaShareableLink()
        request = self.factory.get("/")
        request.user = AnonymousUser()

        class MockView:
            def __init__(self, token):
                self.kwargs = {"token": token}

        view = MockView(self.survey.shareable_token)
        result = permission.has_object_permission(request, view, self.survey)

        self.assertFalse(result)

    def test_permission_requires_auth_anonymous(self):
        """Permission denies access when link requires auth and user is anonymous"""
        self.survey.shareable_link_requires_auth = True
        self.survey.save()

        permission = CanAccessViaShareableLink()
        request = self.factory.get("/")
        request.user = AnonymousUser()

        class MockView:
            def __init__(self, token):
                self.kwargs = {"token": token}

        view = MockView(self.survey.shareable_token)
        result = permission.has_object_permission(request, view, self.survey)

        self.assertFalse(result)

    def test_permission_requires_auth_authenticated(self):
        """Permission allows access when link requires auth and user is authenticated"""
        self.survey.shareable_link_requires_auth = True
        self.survey.save()

        other_user = User.objects.create_user(
            username="user", email="user@test.com", password="testpass123"
        )

        permission = CanAccessViaShareableLink()
        request = self.factory.get("/")
        request.user = other_user

        class MockView:
            def __init__(self, token):
                self.kwargs = {"token": token}

        view = MockView(self.survey.shareable_token)
        result = permission.has_object_permission(request, view, self.survey)

        self.assertTrue(result)

    def test_permission_expired_survey(self):
        """Permission denies access when survey is expired"""
        self.survey.expire_date = timezone.now() - timedelta(days=1)
        self.survey.save()

        permission = CanAccessViaShareableLink()
        request = self.factory.get("/")
        request.user = AnonymousUser()

        class MockView:
            def __init__(self, token):
                self.kwargs = {"token": token}

        view = MockView(self.survey.shareable_token)
        result = permission.has_object_permission(request, view, self.survey)

        self.assertFalse(result)


class ShareableLinkTokenRegenerationTest(TestCase):
    """Test token regeneration and invalidation"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.designer = User.objects.create_user(
            username="designer", email="designer@test.com", password="testpass123"
        )
        self.survey = Survey.objects.create(
            name="Test Survey",
            description="Test Description",
            is_published=True,
            need_logged_user=True,
            publish_date=timezone.now() - timedelta(days=1),
            expire_date=timezone.now() + timedelta(days=30),
            designer=self.designer,
        )

    def test_token_regeneration_invalidates_old_token(self):
        """Regenerating a shareable link token invalidates the old token"""
        # Generate initial shareable link
        request1 = self.factory.post(
            f"/voice/v3/surveys/{self.survey.id}/generate-shareable-link/",
            {"requires_auth": False},
            format="json",
        )
        force_authenticate(request1, user=self.designer)
        view = SurveyViewSet.as_view({"post": "generate_shareable_link"})
        response1 = view(request1, pk=self.survey.id)

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        old_token = response1.data["shareable_token"]
        self.survey.refresh_from_db()
        self.assertEqual(self.survey.shareable_token, old_token)

        # Verify old token works
        request_old = self.factory.get(f"/voice/v3/surveys/share/{old_token}/")
        view_access = SurveyViewSet.as_view({"get": "access_via_shareable_link"})
        response_old = view_access(request_old, token=old_token)
        self.assertEqual(response_old.status_code, status.HTTP_200_OK)

        # Regenerate shareable link (should create new token)
        request2 = self.factory.post(
            f"/voice/v3/surveys/{self.survey.id}/generate-shareable-link/",
            {"requires_auth": False},
            format="json",
        )
        force_authenticate(request2, user=self.designer)
        response2 = view(request2, pk=self.survey.id)

        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        new_token = response2.data["shareable_token"]
        self.assertNotEqual(old_token, new_token)
        self.survey.refresh_from_db()
        self.assertEqual(self.survey.shareable_token, new_token)

        # Old token should no longer work
        request_old_invalid = self.factory.get(f"/voice/v3/surveys/share/{old_token}/")
        response_old_invalid = view_access(request_old_invalid, token=old_token)
        self.assertEqual(response_old_invalid.status_code, status.HTTP_404_NOT_FOUND)

        # New token should work
        request_new = self.factory.get(f"/voice/v3/surveys/share/{new_token}/")
        response_new = view_access(request_new, token=new_token)
        self.assertEqual(response_new.status_code, status.HTTP_200_OK)


class ShareableLinkIntegrationTest(TestCase):
    """Integration tests for shareable link workflows"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.designer = User.objects.create_user(
            username="designer", email="designer@test.com", password="testpass123"
        )
        self.respondent = User.objects.create_user(
            username="respondent", email="respondent@test.com", password="testpass123"
        )
        self.survey = Survey.objects.create(
            name="Integration Test Survey",
            description="Test Description",
            is_published=True,
            need_logged_user=True,  # Private survey
            publish_date=timezone.now() - timedelta(days=1),
            expire_date=timezone.now() + timedelta(days=30),
            designer=self.designer,
        )

        # Create a question
        self.question = Question.objects.create(
            survey=self.survey,
            text="Integration Test Question",
            question_type=Question.SHORT_TEXT,
            order=1,
        )

    def test_generate_link_access_survey_submit_response_workflow(self):
        """Integration test: Generate shareable link → Access survey → Submit response"""
        # Step 1: Designer generates shareable link
        request_generate = self.factory.post(
            f"/voice/v3/surveys/{self.survey.id}/generate-shareable-link/",
            {"requires_auth": False},
            format="json",
        )
        force_authenticate(request_generate, user=self.designer)
        view_generate = SurveyViewSet.as_view({"post": "generate_shareable_link"})
        response_generate = view_generate(request_generate, pk=self.survey.id)

        self.assertEqual(response_generate.status_code, status.HTTP_200_OK)
        shareable_token = response_generate.data["shareable_token"]

        # Step 2: Anonymous user accesses survey via shareable link
        request_access = self.factory.get(f"/voice/v3/surveys/share/{shareable_token}/")
        view_access = SurveyViewSet.as_view({"get": "access_via_shareable_link"})
        response_access = view_access(request_access, token=shareable_token)

        self.assertEqual(response_access.status_code, status.HTTP_200_OK)
        self.assertEqual(response_access.data["name"], self.survey.name)

        # Step 3: Anonymous user gets questions via shareable link
        request_questions = self.factory.get(
            f"/voice/v3/surveys/share/{shareable_token}/questions/"
        )
        view_questions = SurveyViewSet.as_view({"get": "get_questions_via_shareable_link"})
        response_questions = view_questions(request_questions, token=shareable_token)

        self.assertEqual(response_questions.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_questions.data), 1)

        # Step 4: Anonymous user creates a response
        response_obj = ResponseModel.objects.create(
            survey=self.survey,
            respondent=None,  # Anonymous
        )

        # Step 5: Anonymous user submits response via shareable link
        request_submit = self.factory.post(
            "/voice/v3/responses/submit-response/",
            {
                "responseId": str(response_obj.response_id),
                "answers": [
                    {
                        "question": self.question.id,
                        "body": "Integration Test Answer",
                    }
                ],
                "shareable_token": shareable_token,
            },
            format="json",
        )
        view_submit = ResponseViewSet.as_view({"post": "submit_response"})
        response_submit = view_submit(request_submit)

        self.assertIn(
            response_submit.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED]
        )

    def test_shareable_link_with_auth_requirement_workflow(self):
        """Integration test: Shareable link with auth requirement → Login → Access survey"""
        # Step 1: Designer generates shareable link requiring authentication
        request_generate = self.factory.post(
            f"/voice/v3/surveys/{self.survey.id}/generate-shareable-link/",
            {"requires_auth": True},
            format="json",
        )
        force_authenticate(request_generate, user=self.designer)
        view_generate = SurveyViewSet.as_view({"post": "generate_shareable_link"})
        response_generate = view_generate(request_generate, pk=self.survey.id)

        self.assertEqual(response_generate.status_code, status.HTTP_200_OK)
        shareable_token = response_generate.data["shareable_token"]
        self.assertEqual(response_generate.data["requires_auth"], True)

        # Step 2: Anonymous user tries to access survey (should fail)
        request_access_anon = self.factory.get(
            f"/voice/v3/surveys/share/{shareable_token}/"
        )
        view_access = SurveyViewSet.as_view({"get": "access_via_shareable_link"})
        response_access_anon = view_access(request_access_anon, token=shareable_token)

        self.assertEqual(response_access_anon.status_code, status.HTTP_401_UNAUTHORIZED)

        # Step 3: Authenticated user accesses survey (should succeed)
        request_access_auth = self.factory.get(
            f"/voice/v3/surveys/share/{shareable_token}/"
        )
        force_authenticate(request_access_auth, user=self.respondent)
        response_access_auth = view_access(request_access_auth, token=shareable_token)

        self.assertEqual(response_access_auth.status_code, status.HTTP_200_OK)
        self.assertEqual(response_access_auth.data["name"], self.survey.name)

        # Step 4: Authenticated user gets questions
        request_questions = self.factory.get(
            f"/voice/v3/surveys/share/{shareable_token}/questions/"
        )
        force_authenticate(request_questions, user=self.respondent)
        view_questions = SurveyViewSet.as_view({"get": "get_questions_via_shareable_link"})
        response_questions = view_questions(request_questions, token=shareable_token)

        self.assertEqual(response_questions.status_code, status.HTTP_200_OK)

        # Step 5: Authenticated user submits response
        response_obj = ResponseModel.objects.create(
            survey=self.survey,
            respondent=self.respondent,
        )

        request_submit = self.factory.post(
            "/voice/v3/responses/submit-response/",
            {
                "responseId": str(response_obj.response_id),
                "answers": [
                    {
                        "question": self.question.id,
                        "body": "Authenticated Answer",
                    }
                ],
                "shareable_token": shareable_token,
            },
            format="json",
        )
        force_authenticate(request_submit, user=self.respondent)
        view_submit = ResponseViewSet.as_view({"post": "submit_response"})
        response_submit = view_submit(request_submit)

        self.assertIn(
            response_submit.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED]
        )

    def test_token_regeneration_workflow(self):
        """Integration test: Token regeneration workflow"""
        # Step 1: Generate initial shareable link
        request1 = self.factory.post(
            f"/voice/v3/surveys/{self.survey.id}/generate-shareable-link/",
            {"requires_auth": False},
            format="json",
        )
        force_authenticate(request1, user=self.designer)
        view_generate = SurveyViewSet.as_view({"post": "generate_shareable_link"})
        response1 = view_generate(request1, pk=self.survey.id)

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        token1 = response1.data["shareable_token"]

        # Step 2: Verify initial token works
        request_access1 = self.factory.get(f"/voice/v3/surveys/share/{token1}/")
        view_access = SurveyViewSet.as_view({"get": "access_via_shareable_link"})
        response_access1 = view_access(request_access1, token=token1)
        self.assertEqual(response_access1.status_code, status.HTTP_200_OK)

        # Step 3: Regenerate shareable link
        request2 = self.factory.post(
            f"/voice/v3/surveys/{self.survey.id}/generate-shareable-link/",
            {"requires_auth": False},
            format="json",
        )
        force_authenticate(request2, user=self.designer)
        response2 = view_generate(request2, pk=self.survey.id)

        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        token2 = response2.data["shareable_token"]
        self.assertNotEqual(token1, token2)

        # Step 4: Verify old token no longer works
        request_access_old = self.factory.get(f"/voice/v3/surveys/share/{token1}/")
        response_access_old = view_access(request_access_old, token=token1)
        self.assertEqual(response_access_old.status_code, status.HTTP_404_NOT_FOUND)

        # Step 5: Verify new token works
        request_access_new = self.factory.get(f"/voice/v3/surveys/share/{token2}/")
        response_access_new = view_access(request_access_new, token=token2)
        self.assertEqual(response_access_new.status_code, status.HTTP_200_OK)

        # Step 6: Disable shareable link
        request_disable = self.factory.post(
            f"/voice/v3/surveys/{self.survey.id}/disable-shareable-link/",
            format="json",
        )
        force_authenticate(request_disable, user=self.designer)
        view_disable = SurveyViewSet.as_view({"post": "disable_shareable_link"})
        response_disable = view_disable(request_disable, pk=self.survey.id)

        self.assertEqual(response_disable.status_code, status.HTTP_200_OK)

        # Step 7: Verify disabled link no longer works
        request_access_disabled = self.factory.get(f"/voice/v3/surveys/share/{token2}/")
        response_access_disabled = view_access(request_access_disabled, token=token2)
        self.assertEqual(response_access_disabled.status_code, status.HTTP_403_FORBIDDEN)
