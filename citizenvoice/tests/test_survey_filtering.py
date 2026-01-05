"""
Tests the authentication-based survey filtering:
- Anonymous users see only public surveys
- Authenticated users see public surveys + their own surveys
- Private surveys only visible to designer
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from voice.models import Survey, Question
from voice.views import SurveyViewSet


class SurveyFilteringTest(TestCase):
    """Test survey filtering based on authentication and ownership"""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests"""
        # Create users
        cls.user1 = User.objects.create_user(
            username='user1', email='user1@test.com', password='testpass123'
        )
        cls.user2 = User.objects.create_user(
            username='user2', email='user2@test.com', password='testpass123'
        )
        
        now = timezone.now()
        future = now + timedelta(days=30)
        
        # Create public published survey (visible to everyone)
        cls.public_survey = Survey.objects.create(
            name='Public Survey',
            description='Public survey description',
            is_published=True,
            need_logged_user=False,
            publish_date=now,
            expire_date=future,
            designer=cls.user1
        )
        
        # Create private published survey (only visible to designer)
        cls.private_survey = Survey.objects.create(
            name='Private Survey',
            description='Private survey description',
            is_published=True,
            need_logged_user=True,
            publish_date=now,
            expire_date=future,
            designer=cls.user1
        )
        
        # Create unpublished survey (only visible to designer)
        cls.unpublished_survey = Survey.objects.create(
            name='Unpublished Survey',
            description='Unpublished survey description',
            is_published=False,
            need_logged_user=False,
            publish_date=now,
            expire_date=future,
            designer=cls.user1
        )
        
        # Create survey owned by user2
        cls.user2_survey = Survey.objects.create(
            name='User2 Survey',
            description='User2 survey description',
            is_published=True,
            need_logged_user=False,
            publish_date=now,
            expire_date=future,
            designer=cls.user2
        )
        
        # Create expired survey (should not appear)
        cls.expired_survey = Survey.objects.create(
            name='Expired Survey',
            description='Expired survey description',
            is_published=True,
            need_logged_user=False,
            publish_date=now - timedelta(days=10),
            expire_date=now - timedelta(days=1),
            designer=cls.user1
        )

    def setUp(self):
        """Set up for each test"""
        self.factory = APIRequestFactory()
        self.viewset = SurveyViewSet.as_view({'get': 'list'})

    def test_anonymous_user_sees_only_public_surveys(self):
        """Anonymous users should only see public published surveys"""
        request = self.factory.get('/voice/v3/surveys/')
        response = self.viewset(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        survey_names = [s['name'] for s in response.data]
        
        # Should see public survey
        self.assertIn('Public Survey', survey_names)
        
        # Should NOT see private survey
        self.assertNotIn('Private Survey', survey_names)
        
        # Should NOT see unpublished survey
        self.assertNotIn('Unpublished Survey', survey_names)
        
        # Should see user2's public survey
        self.assertIn('User2 Survey', survey_names)
        
        # Should NOT see expired survey
        self.assertNotIn('Expired Survey', survey_names)

    def test_authenticated_user_sees_public_and_own_surveys(self):
        """Authenticated users should see public surveys + their own surveys"""
        request = self.factory.get('/voice/v3/surveys/')
        force_authenticate(request, user=self.user1)
        response = self.viewset(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        survey_names = [s['name'] for s in response.data]
        
        # Should see public survey
        self.assertIn('Public Survey', survey_names)
        
        # Should see own private survey
        self.assertIn('Private Survey', survey_names)
        
        # Should see own unpublished survey
        self.assertIn('Unpublished Survey', survey_names)
        
        # Should see user2's public survey
        self.assertIn('User2 Survey', survey_names)
        
        # Should NOT see expired survey
        self.assertNotIn('Expired Survey', survey_names)

    def test_user_cannot_see_other_users_private_surveys(self):
        """User2 should not see user1's private survey"""
        request = self.factory.get('/voice/v3/surveys/')
        force_authenticate(request, user=self.user2)
        response = self.viewset(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        survey_names = [s['name'] for s in response.data]
        
        # Should see public survey
        self.assertIn('Public Survey', survey_names)
        
        # Should NOT see user1's private survey
        self.assertNotIn('Private Survey', survey_names)
        
        # Should see own survey
        self.assertIn('User2 Survey', survey_names)

    def test_my_surveys_endpoint_requires_authentication(self):
        """my_surveys endpoint should require authentication"""
        viewset = SurveyViewSet.as_view({'get': 'my_surveys'})
        request = self.factory.get('/voice/v3/surveys/my-surveys/')
        response = viewset(request)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_my_surveys_returns_only_user_surveys(self):
        """my_surveys should return only surveys created by authenticated user"""
        viewset = SurveyViewSet.as_view({'get': 'my_surveys'})
        request = self.factory.get('/voice/v3/surveys/my-surveys/')
        force_authenticate(request, user=self.user1)
        response = viewset(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        survey_names = [s['name'] for s in response.data]
        
        # Should see own surveys (published and unpublished)
        self.assertIn('Public Survey', survey_names)
        self.assertIn('Private Survey', survey_names)
        self.assertIn('Unpublished Survey', survey_names)
        
        # Should NOT see other user's surveys
        self.assertNotIn('User2 Survey', survey_names)

    def test_create_survey_requires_authentication(self):
        """Survey creation should require authentication"""
        viewset = SurveyViewSet.as_view({'post': 'create_survey'})
        request = self.factory.post(
            '/voice/v3/surveys/create-survey/',
            {'name': 'New Survey', 'description': 'Test description'},
            format='json'
        )
        response = viewset(request)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_survey_sets_designer(self):
        """Created survey should have authenticated user as designer"""
        viewset = SurveyViewSet.as_view({'post': 'create_survey'})
        request = self.factory.post(
            '/voice/v3/surveys/create-survey/',
            {'name': 'New Survey', 'description': 'Test description'},
            format='json'
        )
        force_authenticate(request, user=self.user1)
        response = viewset(request)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Designer URL can be absolute or relative, check that it contains the user ID
        self.assertIn(f'/voice/v3/users/{self.user1.id}/', response.data['designer'])
        self.assertEqual(response.data['name'], 'New Survey')


class SurveyQuestionsAccessTest(TestCase):
    """Test access control for survey questions"""

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
        
        # Create public published survey with questions
        cls.public_survey = Survey.objects.create(
            name='Public Survey',
            description='Public survey',
            is_published=True,
            need_logged_user=False,
            publish_date=now,
            expire_date=future,
            designer=cls.user1
        )
        cls.public_question = Question.objects.create(
            text='Public Question',
            order=1,
            required=True,
            question_type='text',
            survey=cls.public_survey
        )
        
        # Create private published survey with questions
        cls.private_survey = Survey.objects.create(
            name='Private Survey',
            description='Private survey',
            is_published=True,
            need_logged_user=True,
            publish_date=now,
            expire_date=future,
            designer=cls.user1
        )
        cls.private_question = Question.objects.create(
            text='Private Question',
            order=1,
            required=True,
            question_type='text',
            survey=cls.private_survey
        )
        
        # Create unpublished survey with questions
        cls.unpublished_survey = Survey.objects.create(
            name='Unpublished Survey',
            description='Unpublished survey',
            is_published=False,
            need_logged_user=False,
            publish_date=now,
            expire_date=future,
            designer=cls.user1
        )
        cls.unpublished_question = Question.objects.create(
            text='Unpublished Question',
            order=1,
            required=True,
            question_type='text',
            survey=cls.unpublished_survey
        )

    def setUp(self):
        """Set up for each test"""
        self.factory = APIRequestFactory()

    def test_anonymous_can_access_public_survey_questions(self):
        """Anonymous users can access questions of public published surveys"""
        viewset = SurveyViewSet.as_view({'get': 'get_questions_of_survey'})
        request = self.factory.get(f'/voice/v3/surveys/{self.public_survey.id}/questions/')
        response = viewset(request, pk=self.public_survey.id)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['text'], 'Public Question')

    def test_anonymous_cannot_access_private_survey_questions(self):
        """Anonymous users cannot access questions of private surveys"""
        viewset = SurveyViewSet.as_view({'get': 'get_questions_of_survey'})
        request = self.factory.get(f'/voice/v3/surveys/{self.private_survey.id}/questions/')
        response = viewset(request, pk=self.private_survey.id)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_access_unpublished_survey_questions(self):
        """Anonymous users cannot access questions of unpublished surveys"""
        viewset = SurveyViewSet.as_view({'get': 'get_questions_of_survey'})
        request = self.factory.get(f'/voice/v3/surveys/{self.unpublished_survey.id}/questions/')
        response = viewset(request, pk=self.unpublished_survey.id)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_designer_can_access_own_private_survey_questions(self):
        """Survey designer can access questions of their own private survey"""
        viewset = SurveyViewSet.as_view({'get': 'get_questions_of_survey'})
        request = self.factory.get(f'/voice/v3/surveys/{self.private_survey.id}/questions/')
        force_authenticate(request, user=self.user1)
        response = viewset(request, pk=self.private_survey.id)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['text'], 'Private Question')

    def test_designer_can_access_own_unpublished_survey_questions(self):
        """Survey designer can access questions of their own unpublished survey"""
        viewset = SurveyViewSet.as_view({'get': 'get_questions_of_survey'})
        request = self.factory.get(f'/voice/v3/surveys/{self.unpublished_survey.id}/questions/')
        force_authenticate(request, user=self.user1)
        response = viewset(request, pk=self.unpublished_survey.id)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['text'], 'Unpublished Question')

    def test_other_user_cannot_access_private_survey_questions(self):
        """Other users cannot access questions of private surveys they don't own"""
        viewset = SurveyViewSet.as_view({'get': 'get_questions_of_survey'})
        request = self.factory.get(f'/voice/v3/surveys/{self.private_survey.id}/questions/')
        force_authenticate(request, user=self.user2)
        response = viewset(request, pk=self.private_survey.id)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_user_cannot_access_unpublished_survey_questions(self):
        """Other users cannot access questions of unpublished surveys they don't own"""
        viewset = SurveyViewSet.as_view({'get': 'get_questions_of_survey'})
        request = self.factory.get(f'/voice/v3/surveys/{self.unpublished_survey.id}/questions/')
        force_authenticate(request, user=self.user2)
        response = viewset(request, pk=self.unpublished_survey.id)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

