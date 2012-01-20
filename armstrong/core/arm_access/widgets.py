from django.forms import Widget, Form, SplitDateTimeField
from django.forms.models import modelformset_factory, ModelForm
from django.template import loader, Context
from django.contrib.admin.widgets import AdminSplitDateTime
from .models import Assignment
from datetime import datetime
from functools import partial
from itertools import count
import re


class InlineAssignmentForm(ModelForm):
    start_date = SplitDateTimeField(widget=AdminSplitDateTime)
    end_date = SplitDateTimeField(widget=AdminSplitDateTime,
                                  required=False)

    def __init__(self, *args, **kwargs):
        super(InlineAssignmentForm, self).__init__(*args, **kwargs)
        # necessary because SplitDateTimeWidget doesn't follow the spec and
        # call callables, instead it tries to unpack the value
        if self.initial is not None and not 'start_date' in self.initial:
            self.initial['start_date'] = datetime.now()

    class Meta:
        exclude = ('access_object', 'id')

    def clean(self):
        data = super(InlineAssignmentForm, self).clean()
        if data['end_date'] is None:
            data['end_date'] = datetime.max
        return data

    # we want to always create new Assignments because we create a new access
    # object
    def has_changed(self):
        return True


EmptyAssignmentFormSet = modelformset_factory(Assignment,
                                         form=InlineAssignmentForm,
                                         extra=1,
                                        )


AssignmentFormSet = modelformset_factory(Assignment,
                                         form=InlineAssignmentForm,
                                         extra=0,
                                        )


class AccessWidget(Widget):
    template_name = 'arm_access/access_object_widget.html'

    # pulled from https://github.com/brutasse/django/blob/15667-template-widgets/django/forms/widgets.py
    # hoping that it becomes the new django widget API
    def render(self, name, value, attrs=None):
        context = self.get_context(name, value, attrs=attrs)
        return loader.render_to_string(self.template_name, context)

    def get_context(self, name, value, attrs=None):
        prefix = name + '-assignments'
        if value is None:
            # if object.access is None
            assignments = EmptyAssignmentFormSet(prefix=prefix,
                    queryset=Assignment.objects.none())
        elif type(value) in (int, long):
            # initial code path, we get the ID of the access object
            assignments = AssignmentFormSet(prefix=prefix,
                    queryset=Assignment.objects.filter(access_object=value))
        else:
            # if form submit failed with validation errors, we are passed an
            # AssignmentFormSet, so we just want to pass it through
            assignments = value

        return Context({
            'hidden': self.is_hidden,
            'name': name,
            'required': self.is_required,
            'is_public': value is None,
            'assignments': assignments
        })

    def value_from_datadict(self, data, files, name):
        if name + '_is_public' in data:
            return None
        return AssignmentFormSet(data, prefix=name + '-assignments')

    # We need a choices property because the django admin decides to wrap us in
    # a RelatedFieldWidgetWrapper if our field inherits from ForeignKey, which
    # AccessField does
    def _set_choices(self, value):
        return

    def _get_choices(self):
        return []

    choices = property(_get_choices, _set_choices)
