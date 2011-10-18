from django.db import models
from django.db.models.fields.related \
        import ReverseSingleRelatedObjectDescriptor
from .models import AccessObject
from .widgets import AccessWidget
from .forms import AccessFormField


class AccessField(models.OneToOneField):
    def __init__(self):
        super(AccessField, self).__init__(AccessObject, to_field=None,
                null=True, blank=True)

    def contribute_to_class(self, cls, name):
        super(AccessField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, AccessDescriptor(self))

    def formfield(self, **kwargs):
        return AccessFormField(**kwargs)

    def south_field_triple(self):
        return ('armstrong.core.arm_access.fields.AccessField', [], {})


class AccessDescriptor(ReverseSingleRelatedObjectDescriptor):
    def __set__(self, instance, value):
        # we accept None, a list of Assignments or a single assignment
        obj = self.__get__(instance)
        if obj is None and value is not None:
            obj = AccessObject.objects.create()
            instance.access_id = obj.id

        if value is None:
            if obj is not None:
                instance.access_id = None
                instance.save()
                obj.delete()
            # use our super class for cache invalidation
            super(AccessDescriptor, self).__set__(instance, None)
        else:
            obj.clear()
            if hasattr(value, '__iter__'):
                obj.add(*value)
            else:
                obj.add(value)
            super(AccessDescriptor, self).__set__(instance, obj)
