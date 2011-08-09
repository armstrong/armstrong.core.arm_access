from django.db import models
from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor
from .models import AccessObject


class AccessField(models.OneToOneField):
    def __init__(self):
        super(AccessField, self).__init__(AccessObject, to_field=None,
                null=True, blank=True)

    def contribute_to_class(self, cls, name):
        super(AccessField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, AccessDescriptor(self))


class AccessDescriptor(ReverseSingleRelatedObjectDescriptor):
    def __set__(self, instance, value):
        #accept None, a list of Assignments or a single assignment
        if value is None and instance.access_id is None:
            return
        obj = self.__get__(instance)
        if obj is None:
            obj = AccessObject.objects.create()
            instance.access_id = obj.id

        if value is None:
            instance.access_id = None
            instance.save()
            obj.delete()
        elif hasattr(value, '__iter__'):
            obj.clear()
            obj.add(*value)
        else:
            obj.clear()
            obj.add(value)
