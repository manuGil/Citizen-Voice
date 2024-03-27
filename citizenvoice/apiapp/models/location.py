from django.contrib.gis.db.models  import PointField, PolygonField, LineStringField

from django.db import models
from django.utils.translation import gettext_lazy as _



class PointFeature(models.Model)   :
    """
    Represents the location of a question or answer as a POINT
    """
    geom = PointField()
    description = models.CharField(max_length=100, blank=True, null=True)
    location = models.ForeignKey('LocationCollection', on_delete=models.CASCADE)

class PolygonFeature(models.Model):
    """
    Represents the location of a question or answer as a POLYGON
    """
    geom = PolygonField()
    description = models.CharField(max_length=100, blank=True, null=True)
    location = models.ForeignKey('LocationCollection', on_delete=models.CASCADE)


class LineStringLocation(models.Model):
    """
    Represents the location of a question or answer as a LINESTRING
    """
    geom = LineStringField()
    description = models.CharField(max_length=100, blank=True, null=True)
    location = models.ForeignKey('LocationCollection', on_delete=models.CASCADE)


class LocationCollection(models.Model):
    """
    class for representing geographic locations of
    Questions and Answers.

    Attributes:
    - name: name for the location
    - question: a location may belong to a question
    - answer: a location may belong to an answer
    """

    name = models.CharField(max_length=100, blank=True)
    descripion = models.CharField(max_length=300, blank=True)

    def __str__(self):
        "Returs the name of the location"
        return str(self.name)
