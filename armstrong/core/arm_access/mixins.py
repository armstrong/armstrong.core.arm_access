from django.db import models
from .fields import AccessField


class AccessMixin(models.Model):
    access = AccessField()

    class Meta:
        abstract = True
