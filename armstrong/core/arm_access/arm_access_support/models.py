from django.db import models
from ..models import AccessObject
from ..mixins import AccessMixin


class Content(AccessMixin, models.Model):
    name = models.CharField(max_length=255)
