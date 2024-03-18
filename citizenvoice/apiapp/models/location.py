from django.contrib.gis.db.models  import PointField, PolygonField, LineStringField

from django.db import models
from django.utils.translation import gettext_lazy as _
from .question import Question



class PointLocation(models.Model)   :
    """
    Represents the location of a question or answer as a POINT
    """
    geom = PointField()
    description = models.CharField(max_length=100, blank=True, null=True)

class PolygonLocation(models.Model):
    """
    Represents the location of a question or answer as a POLYGON
    """
    geom = PolygonField()
    description = models.CharField(max_length=100, blank=True, null=True)


class LineStringLocation(models.Model):
    """
    Represents the location of a question or answer as a LINESTRING
    """
    geom = LineStringField()
    description = models.CharField(max_length=100, blank=True, null=True)


class Location(models.Model):
    """
    class for representing geographic locations of
    Questions and Answers.

    Attributes:
    - name: name for the location
    - question: a location may belong to a question
    - answer: a location may belong to an answer
    """

    name = models.CharField(max_length=100, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, blank=True, null=True)
    points = models.ManyToManyField(PointLocation, blank=True)
    lines = models.ManyToManyField(LineStringLocation,  blank=True)
    polygons = models.ManyToManyField(PolygonLocation, blank=True)

    def __str__(self):
        "Returs the name of the location"
        return str(self.name)

