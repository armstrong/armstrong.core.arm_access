from django.db import models

class Content(models.Model):
    name = models.CharField(max_length=255)
