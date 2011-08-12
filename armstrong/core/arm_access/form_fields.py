from django import forms
from .widgets import AccessWidget
from .models import AccessObject

class AccessFormField(forms.Field):
    widget = AccessWidget

    def __init__(self, *args, **kwargs):
        super(AccessFormField, self).__init__(self, *args, **kwargs)

    def clean(self, value):
        if isinstance(value, AccessObject):
            if value.id is None:
                value.save()
            return value.id
        if type(value) == int:
            print "ODD CODE PATH %s" % (__FILE__, )
            return value
        if hasattr(value, 'is_valid'):
            if not value.is_valid():
                raise forms.ValidationError("Invalid Access Definition")
            obj = AccessObject.objects.create()
            obj.add(*(value.save(commit=False)))
            return obj.id

    def prepare_value(self, value):
        return value
