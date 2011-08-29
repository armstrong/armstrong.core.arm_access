from ._utils import *
from ..models import AccessObject, Assignment, Level
from ..forms import AccessFormField
from django.forms import ModelForm, ValidationError
from django.forms.models import modelformset_factory, ModelForm
import datetime


class AssignmentModelForm(ModelForm):
    class Meta:
        model = Assignment
        exclude = ('access_object', )


AssignmentFormSet = modelformset_factory(Assignment, form=AssignmentModelForm)


class AccessFormFieldTestCase(ArmAccessTestCase):
    def setUp(self):
        super(AccessFormFieldTestCase, self).setUp()
        self.field = AccessFormField()

    def testCleanExistingAccessObject(self):
        obj = AccessObject.objects.create()
        self.assertEqual(self.field.clean(obj.id), obj.id)

    def testCleanEmptyFormSet(self):
        formset = AssignmentFormSet({
                'test-TOTAL_FORMS': 0,
                'test-INITIAL_FORMS': 0,
            }, prefix='test')
        obj_id = self.field.clean(formset)
        obj = AccessObject.objects.get(id=obj_id)
        self.assertEqual(0, obj.assignments.count())

    def testCleanPublic(self):
        obj = self.field.clean(None)
        self.assertTrue(obj is None)

    def testCleanInvalidValue(self):
        with self.assertRaises(ValidationError):
            obj = self.field.clean('invalid')

    def testCleanInvalidFormSet(self):
        formset = AssignmentFormSet({
                'test-TOTAL_FORMS': 1,
                'test-INITIAL_FORMS': 0,
                'test-0-id': '',
                'test-0-level': '',
                'test-0-start_date': datetime.datetime.now(),
                'test-0-end_date': datetime.datetime.now(),
            }, prefix='test')
        with self.assertRaises(ValidationError):
            obj = self.field.clean(formset)

    def testCleanValidFormSet(self):
        foo = Level.objects.create(name='foo')
        bar = Level.objects.create(name='bar')
        formset = AssignmentFormSet({
                'test-TOTAL_FORMS': 2,
                'test-INITIAL_FORMS': 0,
                'test-0-id': '',
                'test-0-level': foo.id,
                'test-0-start_date': datetime.datetime.now(),
                'test-0-end_date': datetime.datetime.now(),
                'test-1-id': '',
                'test-1-level': bar.id,
                'test-1-start_date': datetime.datetime.now(),
                'test-1-end_date': datetime.datetime.now(),
            }, prefix='test')
        self.assertTrue(formset.is_valid())
        obj_id = self.field.clean(formset)
        obj = AccessObject.objects.get(id=obj_id)
        self.assertEqual(2, obj.assignments.count())
        assignments = obj.assignments.all()
        levels = [assignment.level for assignment in assignments]
        self.assertTrue(foo in levels)
        self.assertTrue(bar in levels)
