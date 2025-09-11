from django.test import TestCase
from voice.models import Question, Survey, Answer, Response, PointFeature, PolygonFeature, LineFeature, LocationCollection
from django.contrib.auth.models import User
from datetime import date, timedelta
from django.utils import timezone
from voice.views import SurveyViewSet


class APIMethodsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Run once to set up non-modified data for all class methods.")

        # Create a new user
        user = User.objects.create_user(username='testuser', password='testpass')

        # Create a new survey
        today = timezone.now().date()
        survey = Survey(name='Test Survey 1', description='This is used to test things',
                        publish_date=timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time())), 
                        expire_date=timezone.make_aware(timezone.datetime.combine(today + timedelta(days=10), timezone.datetime.min.time())), 
                        public_url='www.google.com', designer=user)
        survey.save()

        # Create a new (expired) survey
        survey = Survey(name='Test Survey 2', description='This is used to test some other things',
                        publish_date=timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time())), 
                        expire_date=timezone.make_aware(timezone.datetime.combine(today - timedelta(days=10), timezone.datetime.min.time())), 
                        public_url='www.bing.com', designer=user)
        survey.save()

        # Create a new question
        question = Question(text='Testing question', order=1, required=True,
                                question_type='text', choices='', survey=survey)
        question.save()

        # Create a new locationCollection
        location_collection = LocationCollection(name='Test Location', description='This is a test location')
        location_collection.save()

        # Create a new point feature
        point_feature = PointFeature(geom='SRID=4326;POINT (0.0075149652548134 0.0322341867016535)', annotation='Test point', location=location_collection)
        point_feature.save()

        
    def test_get_non_expired_surveys(self):
        """Test the GetSurveyByAvailable static method returns non-expired surveys."""
        available_surveys = SurveyViewSet.GetSurveyByAvailable()
        self.assertTrue(available_surveys.exists())
        
        # The first survey should be available (not expired)
        available_survey = available_surveys.first()
        survey = Survey.objects.get(name='Test Survey 1')
        self.assertEqual(available_survey.id, survey.id)
        
        # The expired survey should not be in the available surveys
        expired_survey_name = 'Test Survey 2'
        available_survey_names = [s.name for s in available_surveys]
        self.assertNotIn(expired_survey_name, available_survey_names)

