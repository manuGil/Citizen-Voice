from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response as rf_response
from django.middleware import csrf
from .serializers import (
    PointFeatureSerializer,
    LineFeatureSerializer,
    PolygonFeatureSerializer,
    DashboardAnswerSerializer,
    DashboardTopicSerializer,
)
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from voice.models import (
    Answer,
    PointFeature,
    PolygonFeature,
    LineFeature,
    DashboardTopic,
)
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from drf_spectacular.views import SpectacularAPIView


@api_view(["GET"])
def get_csrf_token(request):
    token = csrf.get_token(request)
    return rf_response({"csrf_token": token})


class CivilianSchemaView(SpectacularAPIView):
    @extend_schema(
        summary="API Schema",
        description="Retrieve the OpenAPI 3.0 schema for the CIVILIAN API",
        operation_id="getCivilianAPISchema",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# Custom Pagination for this API
class AnswersPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 10000


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lists all topics, or filters by survey if survey query param is provided.
    """

    @extend_schema(
        summary="List topics",
        description="List all topics registered in the system, optionally filtered by survey",
        parameters=[
            OpenApiParameter(
                name="survey",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Survey ID to filter topics by",
                required=False,
            )
        ],
        responses={200: DashboardTopicSerializer(many=True)},
        examples=[
            OpenApiExample(
                "All Topics Response",
                summary="Example response for listing all topics",
                description="Response when no survey filter is provided",
                value=[
                    {"id": 1, "name": "favorite place"},
                    {"id": 2, "name": "transportation"},
                    {"id": 3, "name": "public services"},
                ],
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Filtered Topics Response",
                summary="Example response for topics filtered by survey",
                description="Response when survey parameter is provided",
                value=[
                    {"id": 1, "name": "favorite place"},
                    {"id": 2, "name": "transportation"},
                ],
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def list(self, request):
        queryset = DashboardTopic.objects.all()

        # Filter by survey Id
        survey_id = request.query_params.get("survey", None)
        if survey_id is not None:
            try:
                survey_id = int(survey_id)
                queryset = queryset.filter(question__survey_id=survey_id)
            except ValueError:
                queryset = queryset.none()

        serializer = DashboardTopicSerializer(queryset, many=True)
        return rf_response(serializer.data)

    @extend_schema(
        summary="Retrieve topic by ID",
        description="Retrieve a specific topic by its ID",
        responses={200: DashboardTopicSerializer(many=False)},
        examples=[
            OpenApiExample(
                "Topic Detail Response",
                summary="Example response for a single topics",
                value=[
                    {"id": 1, "name": "favorite place"},
                    {"id": 2, "name": "transportation"},
                    {"id": 3, "name": "public services"},
                ],
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def retrieve(self, request, pk=None):
        topic = get_object_or_404(DashboardTopic, pk=pk)
        serializer = DashboardTopicSerializer(topic)
        return rf_response(serializer.data)


class PointFeatureViewSet(viewsets.ModelViewSet):
    """
    PointLocation ViewSet used internally to query data from database for all users.
    """

    serializer_class = PointFeatureSerializer

    def get_queryset(response):
        """
        Returns a set of all PointFeature instances in the database.

        Return:
            queryset: containing all PointFeature instances
        """

        queryset = PointFeature.objects.all()
        return queryset


class PolygonFeatureViewSet(viewsets.ModelViewSet):
    """
    PolygonFeature ViewSet used internally to query data from database for all users.
    """

    serializer_class = PolygonFeatureSerializer

    def get_queryset(response):
        """
        Returns a set of all PolygonFeature instances in the database.

        Return:
            queryset: containing all PolygonFeature instances
        """

        queryset = PolygonFeature.objects.all()
        return queryset

    @staticmethod
    def GetLocationsByQuestion(question):
        """
        Get a list of PointFeatures associated to this question.

        Parameters:
            question (int): Question ID to be used for finding related PointFeatures.

        Return:
            queryset: containing the PointFeature instances related to this Question
        """

        queryset = PointFeature.objects.filter(question=question)
        return queryset

    @staticmethod
    def GetLocationsByAnswer(answer):
        """
        Get a list of PolygonFeatures associated to this answer.

        Parameters:
            answer (int): Answer ID to be used for finding related PolygonFeatures.

        Return:
            queryset: containing the PolygonFeature instances related to this Answer
        """

        queryset = PolygonFeature.objects.filter(answer=answer)
        return queryset


class LineFeatureViewSet(viewsets.ModelViewSet):
    """
    LineStringLocation ViewSet used internally to query data from database for all users.
    """

    serializer_class = LineFeatureSerializer

    def get_queryset(response):
        """
        Returns a set of all LineStringLocation instances in the database.

        Return:
            queryset: containing all LineStringLocation instances
        """

        queryset = LineFeature.objects.all()
        return queryset

    @staticmethod
    def GetLocationsByQuestion(question):
        """
        Get a list of LineStringLocations associated to this question.

        Parameters:
            question (int): Question ID to be used for finding related LineStringLocations.

        Return:
            queryset: containing the LineStringLocation instances related to this Question
        """

        queryset = LineFeature.objects.filter(question=question)
        return queryset

    @staticmethod
    def GetLocationsByAnswer(answer):
        """
        Get a list of LineStringLocations associated to this answer.

        Parameters:
            answer (int): Answer ID to be used for finding related LineStringLocations.

        Return:
            queryset: containing the LineStringLocation instances related to this Answer
        """

        queryset = LineFeature.objects.filter(answer=answer)
        return queryset


class DashboardTopicViewSet(viewsets.ModelViewSet):
    """
    A ViewSet that returns the topics associated to a question
    """

    serializer_class = DashboardTopicSerializer

    def get_queryset(self):
        queryset = DashboardTopic.objects.all()
        return queryset


class AnswerGeoJsonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet that returns GeoJSON data for the answers.
    """

    # Figure out the permissions for the answers, do designers to to see them?
    # permission_classes = [IsAuthenticatedAndSelfOrMakeReadOnly]
    pagination_class = AnswersPagination

    @extend_schema(
        summary="List geo-answers",
        description="List all answers with geographic data, optionally filtered by question or survey",
        operation_id="getGeoJsonAnswers",
        parameters=[
            OpenApiParameter(
                name="survey",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Survey ID to filter answers by",
                required=False,
            ),
            OpenApiParameter(
                name="question",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Question ID to filter answers by",
                required=False,
            ),
        ],
        responses={200: DashboardAnswerSerializer(many=True)},
        examples=[
            OpenApiExample(
                "All answers Response",
                summary="Example response for listing all answers",
                value={
                    "count": 1,
                    "next": "http://localhost:8000/api/answers/?page=2",
                    "previous": "http://localhost:8000/api/answers/?page=1",
                    "results": [
                        {
                            "id": 142,
                            "created": "2025-09-08T07:17:46.212873Z",
                            "body": "fadas",
                            "question": {"text": "Map", "topics": []},
                            "mapview": {
                                "location": {
                                    "geojson": {
                                        "type": "FeatureCollection",
                                        "features": [
                                            {
                                                "id": 69,
                                                "type": "Feature",
                                                "geometry": {
                                                    "type": "Point",
                                                    "coordinates": [
                                                        4.366679,
                                                        52.006738,
                                                    ],
                                                },
                                                "properties": {"annotation": ""},
                                            }
                                        ],
                                    }
                                }
                            },
                        }
                    ],
                },
                response_only=True,
                status_codes=["200"],
            )
        ],
    )
    def list(self, request):
        """
        Returns a set of all Answer instances in the database, or
        filters the queryset based on the query parameters.

        Parameters:
            question (int): Question ID to be used for finding related Answers
            survey (int): Survey ID to be used for finding related Answers

        Returns:
            queryset:
        """

        queryset = (
            Answer.objects.select_related("mapview__location")
            .exclude(mapview=None)
            .order_by("id")
        )

        # Filter by question Id
        question_id = self.request.query_params.get("question", None)
        if question_id is not None:
            queryset = queryset.filter(question_id=question_id)

        # Filter by survey Id
        survey_id = self.request.query_params.get("survey", None)
        if survey_id is not None:
            queryset = queryset.filter(question__survey_id=survey_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = DashboardAnswerSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DashboardAnswerSerializer(queryset, many=True)
        return rf_response(serializer.data)

    @extend_schema(exclude=True)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
