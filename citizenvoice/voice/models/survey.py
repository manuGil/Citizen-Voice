"""
This code is based on the source code of the django-survey application
by Pierre Sassoulas, 2022, version 1.4.0.
Available at https://github.com/Pierre-Sassoulas/django-survey
"""

import secrets
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

# Represents all the responses from every respondent


class Survey(models.Model):
    """
    The Survey class represents a collection of questions that are to be answered by respondents.
    It also represents all the responses made by respondents (users) for this specific Survey.
    """

    name = models.CharField(_("Name of the survey"), max_length=150)
    description = models.TextField(_("Description"), blank=True)
    is_published = models.BooleanField(
        _("Survey is visible and accessible to users"), default=False
    )
    need_logged_user = models.BooleanField(
        _("Only authenticated users have access to this survey"), default=False
    )
    editable_answers = models.BooleanField(
        _("Answers can be edited after submission"), default=True
    )
    submit_message = models.TextField(
        _("Message to be displayed after survey is submitted"),
        blank=True,
        default="Thank you for your participation!",
    )
    publish_date = models.DateTimeField(_("Date that survey was made available"))
    expire_date = models.DateTimeField(_("Expiry date of survey"))
    public_url = models.CharField(
        _("Public URL"), max_length=255, blank=True
    )  # TODO: this should be auto-generated when chosen by the designer
    designer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Shareable link fields
    shareable_token = models.CharField(
        _("Shareable Link Token"), max_length=64, blank=True, null=True, unique=True, db_index=True,
        help_text="Cryptographically secure token for shareable link access"
    )
    shareable_link_enabled = models.BooleanField(
        _("Shareable Link Enabled"), default=False,
        help_text="Whether the shareable link is active"
    )
    shareable_link_requires_auth = models.BooleanField(
        _("Shareable Link Requires Authentication"), default=False,
        help_text="Whether users must be authenticated to access via shareable link"
    )
    shareable_link_created_at = models.DateTimeField(
        _("Shareable Link Created At"), auto_now_add=True, null=True, blank=True
    )
    shareable_link_expires_at = models.DateTimeField(
        _("Shareable Link Expires At"), null=True, blank=True,
        help_text="Optional expiration date for the shareable link"
    )

    def generate_shareable_token(self):
        """Generate a cryptographically secure token for shareable link"""
        return secrets.token_urlsafe(32)

    def __str__(self):
        return str(self.name)

    def question_count(self):
        return self.question_set.count()
