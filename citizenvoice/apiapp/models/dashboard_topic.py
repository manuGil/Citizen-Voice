from django.db import models
from django.utils.translation import gettext_lazy as _
from .question import Question

class DashboardTopic(models.Model):
    """
    The DashboardTopic class provides a way to classify questions using topics. These topics can be used by 
    the CIVILIAN dashboard to create catetories of geospatial questions.
    """
    name = models.CharField(_("topic name"), max_length=150, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)
