from ._utils import *
from ..models import AccessObject, Assignment, Level
from ..widgets import *
from django.forms import ModelForm, ValidationError
from django.forms.models import modelformset_factory, ModelForm
import datetime


class AccessWidgetTestCase(ArmAccessTestCase):
    def setUp(self):
        super(AccessWidgetTestCase, self).setUp()
        self.widget = AccessWidget()

    def testParseForPublic(self):
        name = '%i' % random.randint(1000, 10000)
        data = {
                    name+'_is_public': True
                }
        value = self.widget.value_from_datadict(data, [], name)

    def testParseForEmptyAssignments(self):
        name = '%i' % random.randint(1000, 10000)
        data = {
                 name + '-assignments-TOTAL_FORMS': u'0',
                 name + '-assignments-INITIAL_FORMS': u'0',
                 name + '-assignments-MAX_NUM_FORMS': u'',
                }
        value = self.widget.value_from_datadict(data, [], name)
        self.assertEqual(0, len(value))

    def testParseFor3Assignments(self):
        name = '%i' % random.randint(1000, 10000)
        foo = Level.objects.create(name='foo')
        bar = Level.objects.create(name='bar')
        baz = Level.objects.create(name='baz')
        data = {
                 name + '-assignments-TOTAL_FORMS': u'3',
                 name + '-assignments-INITIAL_FORMS': u'0',
                 name + '-assignments-MAX_NUM_FORMS': u'',
                 name + '-assignments-0-id': u'',
                 name + '-assignments-0-level': u'%i' % foo.id,
                 name + '-assignments-0-start_date_0': u'2011-08-12',
                 name + '-assignments-0-start_date_1': u'12:50:56',
                 name + '-assignments-0-end_date_1': u'23:59:59',
                 name + '-assignments-0-end_date_0': u'9999-12-31',
                 name + '-assignments-1-id': u'',
                 name + '-assignments-1-level': u'%i' % baz.id,
                 name + '-assignments-1-start_date_0': u'2011-08-12',
                 name + '-assignments-1-start_date_1': u'13:13:14',
                 name + '-assignments-1-end_date_0': u'',
                 name + '-assignments-1-end_date_1': u'',
                 name + '-assignments-2-id': u'',
                 name + '-assignments-2-level': u'%i' % bar.id,
                 name + '-assignments-2-start_date_0': u'2011-08-12',
                 name + '-assignments-2-start_date_1': u'13:13:14',
                 name + '-assignments-2-end_date_0': u'',
                 name + '-assignments-2-end_date_1': u'',
             }
        value = self.widget.value_from_datadict(data, [], name)
        self.assertEqual(3, len(value))
