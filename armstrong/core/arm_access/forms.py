from django import forms
from .widgets import AccessWidget
from .models import AccessObject


class AccessFormField(forms.Field):
    widget = AccessWidget

    def __init__(self, *args, **kwargs):
        super(AccessFormField, self).__init__(self, *args, **kwargs)

    def clean(self, value):
        if value is None:
            return None
        if hasattr(value, 'is_valid'):
            if not value.is_valid():
                raise forms.ValidationError("Invalid Access Definition")
            obj = AccessObject.objects.create()
            obj.add(*(value.save(commit=False)))
            return obj.id
        try:
            return int(value)
        except:
            raise forms.ValidationError("Value could not be converted")
