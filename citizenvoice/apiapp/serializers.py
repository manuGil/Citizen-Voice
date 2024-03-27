from rest_framework import serializers
from .models import (Answer, Question, Survey, PointFeature, 
                     PolygonFeature, LineStringLocation, MapView,
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
    survey = serializers.PrimaryKeyRelatedField(queryset=Survey.objects.all())
    # survey = serializers.HyperlinkedRelatedField(view_name='survey-detail', read_only=True)

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
    Serializes 'created', 'updated', 'survey', 'interview_uuid', 'respondent'
    fields of the Response model for the API.
    """
    survey = serializers.PrimaryKeyRelatedField(queryset=Survey.objects.all())
    respondent = serializers.SerializerMethodField()

    def get_respondent(self, User):
        return UserSerializer(User.respondent).data

    def create(self, validated_data):
        respondent_data = validated_data.pop('respondent')
        respondent = User.objects.create(pk=respondent_data['id'])
        response = ResponseModel.objects.create(respondent=respondent, **validated_data)
        return response
    
    class Meta:
        model = ResponseModel
        fields = ('created', 'updated', 'survey',
                   'interview_uuid', 'url','respondent')



class SurveySerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'id', 'name', 'description', 'is_published', 'need_logged_user',
    'editable_answers', 'publish_date', 'expire_date', 'public_url', 'designer'
    fields of the Survey model for the API.
    """

    class Meta:
        model = Survey
        fields = ('id', 'name', 'description', 'is_published', 'need_logged_user', 'editable_answers',
                  'publish_date', 'expire_date', 'public_url', 'designer', 'url')

# TODO: change this to use serializers.ModelSerializer (PrimaryKeyRelatedField)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'id', 'username', 'first_name', 'last_name', 'email'
    fields of the User model for the API.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')

# TODO: change this to use serializers.ModelSerializer (PrimaryKeyRelatedField)


class LocationCollectionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'name', 'question', 'answer', 'points', 'lines', 'polygons'
    fields of the Location model for the API.
    """
    # survey = serializers.PrimaryKeyRelatedField(queryset=Survey.objects.all())
    # points = serializers.HyperlinkedIdentityField(view_name='pointfeature', read_only=True)
    # question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    points = serializers.PrimaryKeyRelatedField(queryset=PointFeature.objects.all(), required=False)

    # TODO: read DRF documentation to understand how to fix the issues with location-detail
    # https://www.django-rest-framework.org/api-guide/serializers/#modelserializer

    class Meta:
        model = LocationCollection
        fields = ('id', 'url', 'name', 'points')
        read_only_fields = ('id', 'url')


class PointFeatureSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'id', 'name', 'descripton', fields of the PointLocation model for the API.
    """
    class Meta:
        model = PointFeature
        fields = ('id', 'url', 'geom', 'description',)

# TODO: change this to use serializers.ModelSerializer (PrimaryKeyRelatedField)


class PolygonFeatureSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'id', 'geom', 'descripton', fields of the PolygonLocation model for the API.
    """
    class Meta:
        model = PolygonFeature
        fields = ('id', 'url', 'geom', 'description')
        read_only_fields = ('id', 'url')
        
        
# # TODO: change this to use serializers.ModelSerializer (PrimaryKeyRelatedField)


class LineStringLocationSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'id', 'geom', 'description' fields of the LineStringLocation model for the API.
    """
    class Meta:
        model = LineStringLocation
        fields = ('id', 'geom', 'description')
        

class AnswerSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'response', 'question', 'created', 'updated', 'body'
    fields of the Answer model for the API.
    """
    
    locations = serializers.PrimaryKeyRelatedField(queryset=LocationCollection.objects.all(), required=False)
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    
    class Meta:
        model = Answer
        fields = ('id', 'url', 'question', 'locations',  'created', 'updated', 'body', 'response')
        extra_kwargs = {
            'locations': {'required': False}  # this makes the locations field optional. However, the body or a resquest is not consistent. Is this a problem?
        }

    def create(self, validated_data):
        answer = Answer.objects.create(
            response=validated_data['response'],
            question=validated_data['question'],
            locations=validated_data.get('locations', None),
            body=validated_data['body']
        )
        return answer

class MapViewSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'name', 'map_service_url' and 'options'
    fields of the MapView model for the API.
    """
    class Meta:
        model = MapView
        fields = ('id', 'url', 'name', 'map_service_url', 'options', 'geometries', 'location_collection')
