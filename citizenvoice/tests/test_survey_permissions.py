"""
Unit tests for Phase 1.3: Survey Permissions

Tests the CanAccessSurvey permission class:
- Public surveys: anyone can read, only designer can write
- Private surveys: only designer can read/write
- Unpublished surveys: only designer can read/write
"""

from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from voice.models import Survey
from voice.views import SurveyViewSet
from voice.permissions import CanAccessSurvey


class SurveyPermissionsTest(TestCase):
    """Test CanAccessSurvey permission class"""

    @classmethod
    def setUpTestData(cls):
        """Set up test data"""
        cls.user1 = User.objects.create_user(
            username='user1', email='user1@test.com', password='testpass123'
        )
        cls.user2 = User.objects.create_user(
            username='user2', email='user2@test.com', password='testpass123'
        )
        
        now = timezone.now()
        future = now + timedelta(days=30)
        
        # Create public published survey
        cls.public_survey = Survey.objects.create(
            name='Public Survey',
            description='Public survey',
            is_published=True,
            need_logged_user=False,
            publish_date=now,
            expire_date=future,
            designer=cls.user1
        )
        
        # Create private published survey
        cls.private_survey = Survey.objects.create(
            name='Private Survey',
            description='Private survey',
            is_published=True,
            need_logged_user=True,
            publish_date=now,
            expire_date=future,
            designer=cls.user1
        )
        
        # Create unpublished survey
        cls.unpublished_survey = Survey.objects.create(
            name='Unpublished Survey',
            description='Unpublished survey',
            is_published=False,
            need_logged_user=False,
            publish_date=now,
            expire_date=future,
            designer=cls.user1
        )

    def setUp(self):
        """Set up for each test"""
        self.factory = APIRequestFactory()
        self.permission = CanAccessSurvey()

    def test_anonymous_can_read_public_survey(self):
        """Anonymous users can read public published surveys"""
        request = self.factory.get('/voice/v3/surveys/1/')
        request.user = AnonymousUser()
        
        has_permission = self.permission.has_object_permission(
            request, None, self.public_survey
        )
        self.assertTrue(has_permission)

    def test_anonymous_cannot_read_private_survey(self):
        """Anonymous users cannot read private surveys"""
        request = self.factory.get('/voice/v3/surveys/1/')
        request.user = AnonymousUser()
        
        has_permission = self.permission.has_object_permission(
            request, None, self.private_survey
        )
        self.assertFalse(has_permission)

    def test_anonymous_cannot_read_unpublished_survey(self):
        """Anonymous users cannot read unpublished surveys"""
        request = self.factory.get('/voice/v3/surveys/1/')
        request.user = AnonymousUser()
        
        has_permission = self.permission.has_object_permission(
            request, None, self.unpublished_survey
        )
        self.assertFalse(has_permission)

    def test_anonymous_cannot_write_public_survey(self):
        """Anonymous users cannot write to any survey"""
        request = self.factory.patch('/voice/v3/surveys/1/')
        request.user = AnonymousUser()
        
        has_permission = self.permission.has_object_permission(
            request, None, self.public_survey
        )
        self.assertFalse(has_permission)

    def test_designer_can_read_own_private_survey(self):
        """Survey designer can read their own private survey"""
        request = self.factory.get('/voice/v3/surveys/1/')
        request.user = self.user1
        
        has_permission = self.permission.has_object_permission(
            request, None, self.private_survey
        )
        self.assertTrue(has_permission)

    def test_designer_can_read_own_unpublished_survey(self):
        """Survey designer can read their own unpublished survey"""
        request = self.factory.get('/voice/v3/surveys/1/')
        request.user = self.user1
        
        has_permission = self.permission.has_object_permission(
            request, None, self.unpublished_survey
        )
        self.assertTrue(has_permission)

    def test_designer_can_write_own_survey(self):
        """Survey designer can write to their own survey"""
        request = self.factory.patch('/voice/v3/surveys/1/')
        request.user = self.user1
        
        has_permission = self.permission.has_object_permission(
            request, None, self.public_survey
        )
        self.assertTrue(has_permission)

    def test_other_user_cannot_read_private_survey(self):
        """Other users cannot read private surveys they don't own"""
        request = self.factory.get('/voice/v3/surveys/1/')
        request.user = self.user2
        
        has_permission = self.permission.has_object_permission(
            request, None, self.private_survey
        )
        self.assertFalse(has_permission)

    def test_other_user_cannot_read_unpublished_survey(self):
        """Other users cannot read unpublished surveys they don't own"""
        request = self.factory.get('/voice/v3/surveys/1/')
        request.user = self.user2
        
        has_permission = self.permission.has_object_permission(
            request, None, self.unpublished_survey
        )
        self.assertFalse(has_permission)

    def test_other_user_cannot_write_public_survey(self):
        """Other users cannot write to surveys they don't own"""
        request = self.factory.patch('/voice/v3/surveys/1/')
        request.user = self.user2
        
        has_permission = self.permission.has_object_permission(
            request, None, self.public_survey
        )
        self.assertFalse(has_permission)

    def test_other_user_can_read_public_survey(self):
        """Other users can read public surveys"""
        request = self.factory.get('/voice/v3/surveys/1/')
        request.user = self.user2
        
        has_permission = self.permission.has_object_permission(
            request, None, self.public_survey
        )
        self.assertTrue(has_permission)


class SurveyViewSetPermissionsTest(TestCase):
    """Test permissions applied to SurveyViewSet endpoints"""

    @classmethod
    def setUpTestData(cls):
        """Set up test data"""
        cls.user1 = User.objects.create_user(
            username='user1', email='user1@test.com', password='testpass123'
        )
        cls.user2 = User.objects.create_user(
            username='user2', email='user2@test.com', password='testpass123'
        )
        
        now = timezone.now()
        future = now + timedelta(days=30)
        
        cls.private_survey = Survey.objects.create(
            name='Private Survey',
            description='Private survey',
            is_published=True,
            need_logged_user=True,
            publish_date=now,
            expire_date=future,
            designer=cls.user1
        )

    def setUp(self):
        """Set up for each test"""
        self.factory = APIRequestFactory()

    def test_anonymous_cannot_retrieve_private_survey(self):
        """Anonymous users cannot retrieve private survey details"""
        viewset = SurveyViewSet.as_view({'get': 'retrieve'})
        request = self.factory.get(f'/voice/v3/surveys/{self.private_survey.id}/')
        response = viewset(request, pk=self.private_survey.id)
        
        # REST Framework returns 401 (Unauthorized) for anonymous users
        # when default permission requires authentication
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_designer_can_retrieve_own_private_survey(self):
        """Survey designer can retrieve their own private survey"""
        viewset = SurveyViewSet.as_view({'get': 'retrieve'})
        request = self.factory.get(f'/voice/v3/surveys/{self.private_survey.id}/')
        force_authenticate(request, user=self.user1)
        response = viewset(request, pk=self.private_survey.id)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Private Survey')

    def test_other_user_cannot_retrieve_private_survey(self):
        """Other users cannot retrieve private survey they don't own"""
        viewset = SurveyViewSet.as_view({'get': 'retrieve'})
        request = self.factory.get(f'/voice/v3/surveys/{self.private_survey.id}/')
        force_authenticate(request, user=self.user2)
        response = viewset(request, pk=self.private_survey.id)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_update_survey(self):
        """Anonymous users cannot update any survey"""
        viewset = SurveyViewSet.as_view({'patch': 'partial_update'})
        request = self.factory.patch(
            f'/voice/v3/surveys/{self.private_survey.id}/',
            {'name': 'Updated Name'},
            format='json'
        )
        response = viewset(request, pk=self.private_survey.id)
        
        # REST Framework returns 401 (Unauthorized) for anonymous users
        # when default permission requires authentication for write operations
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_designer_can_update_own_survey(self):
        """Survey designer can update their own survey"""
        viewset = SurveyViewSet.as_view({'patch': 'partial_update'})
        request = self.factory.patch(
            f'/voice/v3/surveys/{self.private_survey.id}/',
            {'name': 'Updated Name'},
            format='json'
        )
        force_authenticate(request, user=self.user1)
        response = viewset(request, pk=self.private_survey.id)
        
        # Should succeed (200 or 204 depending on implementation)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT])

    def test_other_user_cannot_update_survey(self):
        """Other users cannot update surveys they don't own"""
        viewset = SurveyViewSet.as_view({'patch': 'partial_update'})
        request = self.factory.patch(
            f'/voice/v3/surveys/{self.private_survey.id}/',
            {'name': 'Updated Name'},
            format='json'
        )
        force_authenticate(request, user=self.user2)
        response = viewset(request, pk=self.private_survey.id)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_delete_survey(self):
        """Anonymous users cannot delete any survey"""
        viewset = SurveyViewSet.as_view({'delete': 'destroy'})
        request = self.factory.delete(f'/voice/v3/surveys/{self.private_survey.id}/')
        response = viewset(request, pk=self.private_survey.id)
        
        # REST Framework returns 401 (Unauthorized) for anonymous users
        # when default permission requires authentication for write operations
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_designer_can_delete_own_survey(self):
        """Survey designer can delete their own survey"""
        # Create a new survey for deletion test
        now = timezone.now()
        future = now + timedelta(days=30)
        survey_to_delete = Survey.objects.create(
            name='Survey To Delete',
            description='Will be deleted',
            is_published=True,
            need_logged_user=False,
            publish_date=now,
            expire_date=future,
            designer=self.user1
        )
        
        viewset = SurveyViewSet.as_view({'delete': 'destroy'})
        request = self.factory.delete(f'/voice/v3/surveys/{survey_to_delete.id}/')
        force_authenticate(request, user=self.user1)
        response = viewset(request, pk=survey_to_delete.id)
        
        # Should succeed (204 No Content)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_user_cannot_delete_survey(self):
        """Other users cannot delete surveys they don't own"""
        viewset = SurveyViewSet.as_view({'delete': 'destroy'})
        request = self.factory.delete(f'/voice/v3/surveys/{self.private_survey.id}/')
        force_authenticate(request, user=self.user2)
        response = viewset(request, pk=self.private_survey.id)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

