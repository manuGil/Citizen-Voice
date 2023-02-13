# ====================================================================================================================
#
# Created with reference "Build a REST API in 30 minutes with Django REST Framework" by Bennett Garner, May 17, 2019
# https://medium.com/swlh/build-your-first-rest-api-with-django-rest-framework-e394e39a482c
#
# ====================================================================================================================

from rest_framework import serializers
from .models import Answer, Question, Survey, Response, PointLocation, PolygonLocation, LineStringLocation, MapView
from django.contrib.auth.models import User

#=============================================
# Create serializer classes that allow for exposing certain model fields to be used in the API
#=============================================

class AnswerSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'response', 'question', 'created', 'updated', 'body'
    fields of the Answer model for the API.
    """
    class Meta:
        model = Answer
        fields = ('response', 'question', 'created', 'updated', 'body')

class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'text', 'order', 'required', 'question_type', 'choices', 'is_geospatial', 'map_view'
    fields of the Question model for the API.
    """
    class Meta:
        model = Question
        fields = ('text', 'order', 'required', 'question_type', 'choices', 'survey', 'is_geospatial') # 'map_view')
        #TODO: map_view is commented out for now because it was causing "ImproperlyConfigured" error


class ResponseSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'created', 'updated', 'survey', 'interview_uuid', 'respondent'
    fields of the Response model for the API.
    """
    class Meta:
        model = Response
        fields = ('created', 'updated', 'survey', 'interview_uuid', 'respondent')

class SurveySerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'id', 'name', 'description', 'is_published', 'need_logged_user',
    'editable_answers', 'publish_date', 'expire_date', 'public_url', 'designer'
    fields of the Survey model for the API.
    """
    class Meta:
        model = Survey
        fields = ('id', 'name', 'description', 'is_published', 'need_logged_user', 'editable_answers',
         'publish_date', 'expire_date', 'public_url', 'designer')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'id', 'username', 'first_name', 'last_name', 'email'
    fields of the User model for the API.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')

class PointLocationSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'location', 'name', 'question', 'answer' fields of the PointLocation model for the API.
    """
    class Meta:
        model = PointLocation
        fields = ('location', 'name', 'question', 'answer')

class PolygonLocationSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'location', 'name', 'question', 'answer' fields of the PolygonLocation model for the API.
    """
    class Meta:
        model = PolygonLocation
        fields = ('location', 'name', 'question', 'answer')

class LineStringLocationSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'location', 'name', 'question', 'answer' fields of the LineStringLocation model for the API.
    """
    class Meta:
        model = LineStringLocation
        fields = ('location', 'name', 'question', 'answer')

class MapViewSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'name', 'map_service_url' and 'options'
    fields of the MapView model for the API.
    """
    class Meta:
        model = MapView
        fields = ('name', 'map_service_url', 'options')
