"""
Serializers for the API endpoints of the dashboard app.
"""

import copy
from rest_framework import serializers
from apiapp.models import (Answer, Question, Survey, PointFeature, 
                     PolygonFeature, LineFeature, MapView,
                    LocationCollection, DashboardTopic)
from rest_framework_gis.serializers import GeoFeatureModelSerializer
    
class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes 'text', 'order', 'required', 'question_type', 'choices', 'is_geospatial', 'map_view'
    fields of the Question model for the API.
    """
    survey = serializers.HyperlinkedRelatedField(view_name='survey-detail',read_only=True)
    topics = serializers.HyperlinkedRelatedField(view_name='topics-detail', read_only=True, many=True)

    class Meta:
        model = Question
        fields = ('id', 'url', 'text', 'explanation', 'has_text_input', 'order', 'required', 'question_type',
                  'choices', 'survey', 'is_geospatial', 'mapview', 'topics')
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
             has_text_input=validated_data.get('has_text_input', True),
            mapview=validated_data.get('mapview', None),
        )
        return question



class PointFeatureSerializer(GeoFeatureModelSerializer):
    """
    GeoJson serializer for 'id', 'url', 'geom', 'name', 'annotation', 'location' 
    fields of the PointLocation model for the API.
    """
    location = serializers.HyperlinkedRelatedField(queryset=LocationCollection.objects.all(),
                                                   view_name='locationcollection-detail')

    class Meta:
        model = PointFeature
        geo_field = 'geom'
        fields = ('id', 'url', 'annotation', 'location', 'geom')
        read_only_fields = ('id', 'url')
    
    def create(self, validated_data):
        response = PointFeature.objects.create(
            **validated_data
        )
        return response


class PolygonFeatureSerializer(GeoFeatureModelSerializer):
    """
    GeoJson serializer for 'id', 'geom', 'annotation', 'location' fields of the PolygonLocation model for the API.
    The 'geom' field is serialized as a GeoJSON field.
    """
    location = serializers.HyperlinkedRelatedField(queryset=LocationCollection.objects.all(),
                                                   view_name='locationcollection-detail')

    class Meta:
        model = PolygonFeature
        geo_field = 'geom'
        fields = ('id', 'url', 'annotation', 'location', 'geom')
        read_only_fields = ('id', 'url')
    
    def create(self, validated_data):
        response = PolygonFeature.objects.create(
            **validated_data
        )
        return response

class LineFeatureSerializer(GeoFeatureModelSerializer):
    """
    Serialises 'id', 'geom', 'annotation' fields of the LineStringLocation model for the API.
    The 'geom' field is serialized as a GeoJSON field.
    """
    location = serializers.HyperlinkedRelatedField(queryset=LocationCollection.objects.all(),
                                                   view_name='locationcollection-detail')

    class Meta:
        model = LineFeature
        geo_field = 'geom'
        fields = ('id', 'url', 'annotation', 'location', 'geom')
        read_only_fields = ('id', 'url')
    

    def create(self, validated_data):
        response = LineFeature.objects.create(
            **validated_data
        )
        return response

class LocationCollectionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'name', 'question', 'answer', 'points', 'lines', 'polygons'
    fields of the Location model for the API.
    """

    geojson = serializers.SerializerMethodField()

    class Meta:
        model = LocationCollection
        fields = ('id', 'url', 'name', 'description', 'geojson')
        read_only_fields = ('id', 'url')
    
    def get_geojson(self, obj):
        """
        Returns a list of URLs of all the features (points, lines, polygons)
        associated with the location collection.
        """
        points = PointFeatureSerializer(PointFeature.objects.filter(location__id=obj.pk), 
                                       many=True,
                                       context={'request': self.context.get('request')}).data
        lines = LineFeatureSerializer(LineFeature.objects.filter(location__id=obj.pk), 
                                       many=True,
                                       context={'request': self.context.get('request')}).data
        polygons = PolygonFeatureSerializer(PolygonFeature.objects.filter(location__id=obj.pk), 
                                       many=True,
                                       context={'request': self.context.get('request')}).data
        features = copy.deepcopy(points)
        features['features'].extend(lines['features'])
        features['features'].extend(polygons['features'])

        return  features

class DashboardMapViewSerializer(serializers.ModelSerializer):
    """
    A serializer class for the MapView model used in the dashboard endpoint.
    """

    location = LocationCollectionSerializer()

    class Meta:
        model = MapView
        fields = ['location']
        depth = 2

class DashboardAnswerSerializer(serializers.ModelSerializer):
    """
    A serializer class for the Answer model that serializes the 'geom' field as a GeoJSON field.
    """

    # response = serializers.HyperlinkedRelatedField(queryset=ResponseModel.objects.all(),view_name='response-detail')
    question = serializers.SerializerMethodField()
    mapview = DashboardMapViewSerializer()

    class Meta:
        model = Answer
        geo_field = None
        fields = ('id',  'created', 'body', 'question', 'mapview')
        read_only_fields = ('id', 'created')
        depth = 2


    # def get_mapview(self, obj):
    #     serializer = MapViewSerializer(MapView.objects.filter(answer__id=obj.pk), 
    #                                    many=True,
    #                                    context={'request': self.context.get('request')}).data
    #     return serializer
    
    def get_question(self, obj):
        serializer = QuestionSerializer(Question.objects.filter(answer__id=obj.pk), 
                                       many=True,
                                       context={'request': self.context.get('request')}).data
        
        extracted_items = ['text', 'topics'] # this items will be part of the serialized data
        serializer = {key: value for key, value in serializer[0].items() if key in extracted_items}
        return serializer
    

    
class DashboardTopicSerializer(serializers.ModelSerializer):
    """
    A serializer class for the DashboardTopic model.
    """
    
    class Meta:
        model = DashboardTopic
        fields = ['name']
        depth = 2