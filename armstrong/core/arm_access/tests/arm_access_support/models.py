from django.db import models
from ...models import AccessObject
from ...mixins import AccessMixin


class ArmAccessSupportContent(AccessMixin, models.Model):
    name = models.CharField(max_length=255)
