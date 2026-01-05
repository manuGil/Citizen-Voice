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

