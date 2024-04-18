from rest_framework import serializers
from .models import (Answer, Question, Survey, PointFeature, 
                     PolygonFeature, LineFeature, MapView,
                    LocationCollection)
from .models import Response as ResponseModel
from django.contrib.auth.models import User


# =============================================ß
# Create serializer classes that allow for exposing certain model fields to be used in the API
# =============================================


    
class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes 'text', 'order', 'required', 'question_type', 'choices', 'is_geospatial', 'map_view'
    fields of the Question model for the API.
    """
    # survey = serializers.PrimaryKeyRelatedField(queryset=Survey.objects.all())
    survey = serializers.HyperlinkedRelatedField(view_name='survey-detail',read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'url', 'text', 'order', 'required', 'question_type',
                  'choices', 'survey', 'is_geospatial', 'map_view')
        read_only_fields = ('id', 'url')

    def create(self, validated_data):
        question = Question.objects.create(
            text=validated_data['text'],
            order=validated_data['order'],
            required=validated_data['required'],
            question_type=validated_data['question_type'],
            choices=validated_data.get('choices', None),
            survey=validated_data['survey'],
            is_geospatial=validated_data.get('is_geospatial', False),
            map_view=validated_data.get('map_view', None),
        )
        return question



class ResponseSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes 'response_id', 'url', 'survey', 'respondent', 'created', 'updated'
    fields of the Response model for the API.
    """
    survey = serializers.HyperlinkedRelatedField(queryset=Survey.objects.all(),view_name='survey-detail')
    respondent = serializers.HyperlinkedRelatedField(queryset=User.objects.all(),view_name='user-detail', allow_null=True)

    def get_respondent(self, User):
        return UserSerializer(User.respondent).data
   
    class Meta:
        model = ResponseModel
        fields = ('response_id', 'url', 'created', 'updated', 'survey',
                    'respondent')
        extra_kwargs = {
            'response_id': {'read_only': True},
            'url': {'read_only': True},
            'created': {'read_only': True}
        }


    def create(self, validated_data):
        response = ResponseModel.objects.create(
            **validated_data
        )
        return response


class SurveySerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'id', 'name', 'description', 'is_published', 'need_logged_user',
    'editable_answers', 'publish_date', 'expire_date', 'public_url', 'designer'
    fields of the Survey model for the API.
    """

    designer = serializers.HyperlinkedRelatedField(view_name='user-detail',read_only=True)
    

    class Meta:
        model = Survey
        fields = ('id', 'url', 'name', 'description', 'is_published', 'need_logged_user', 'editable_answers',
                  'publish_date', 'expire_date', 'public_url', 'designer')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'id', 'username', 'first_name', 'last_name', 'email'
    fields of the User model for the API.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class PointFeatureSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'id', 'name', 'descripton', fields of the PointLocation model for the API.
    """
    location = serializers.HyperlinkedRelatedField(view_name='locationcollection-detail',read_only=True)

    class Meta:
        model = PointFeature
        fields = ('id', 'url', 'geom', 'description', 'location')


class PolygonFeatureSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'id', 'geom', 'descripton', fields of the PolygonLocation model for the API.
    """
    location = serializers.HyperlinkedRelatedField(view_name='locationcollection-detail',read_only=True)

    class Meta:
        model = PolygonFeature
        fields = ('id', 'url', 'geom', 'description', 'location')
        read_only_fields = ('id', 'url')
        

class LineFeatureSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'id', 'geom', 'description' fields of the LineStringLocation model for the API.
    """
    location = serializers.HyperlinkedRelatedField(view_name='locationcollection-detail',read_only=True)

    class Meta:
        model = PolygonFeature
        fields = ('id', 'url', 'geom', 'description', 'location')
        read_only_fields = ('id', 'url')
        

class LocationCollectionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'name', 'question', 'answer', 'points', 'lines', 'polygons'
    fields of the Location model for the API.
    """

    # TODO: read DRF documentation to understand how to fix the issues with location-detail
    # https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
   

    class Meta:
        model = LocationCollection
        fields = ('id', 'url', 'name')
        read_only_fields = ('id', 'url')


class AnswerSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'response', 'question', 'created', 'updated', 'body'
    fields of the Answer model for the API.
    """
    
    response = serializers.HyperlinkedRelatedField(queryset=ResponseModel.objects.all(),view_name='response-detail')
    location = serializers.HyperlinkedRelatedField(queryset=LocationCollection.objects.all(), view_name='locationcollection-detail', allow_null=True)
    question = serializers.HyperlinkedRelatedField(queryset=Question.objects.all(), view_name='question-detail')
    
    class Meta:
        model = Answer
        fields = ('id', 'url', 'created', 'updated', 'body',  'question', 'response', 'location')
        read_only_fields = ('id', 'url', 'created')

    def create(self, validated_data):
        response = Answer.objects.create(
            **validated_data
        )
        return response

class MapViewSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'name', 'map_service_url' and 'options'
    fields of the MapView model for the API.
    """
    class Meta:
        model = MapView
        fields = ('id', 'url', 'name', 'map_service_url', 'options', 'location')
