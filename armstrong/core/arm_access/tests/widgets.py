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
                    name + '_is_public': True
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
        self.assertTrue(value.is_valid())

    def testContextWithId(self):
        name = '%i' % random.randint(1000, 10000)
        foo = Level.objects.create(name='foo')
        bar = Level.objects.create(name='bar')
        obj = AccessObject.objects.create()
        obj.create(level=foo, start_date=datetime.datetime(2011, 8, 12, 12, 50, 56))
        obj.create(level=bar, start_date=datetime.datetime.now())
        context = self.widget.get_context(name, obj.id)
        self.assertFalse(context['hidden'])
        self.assertEqual(name, context['name'])
        self.assertFalse(context['is_public'])
        self.assertEqual(2, len(context['assignments']))
        self.assertEqual(datetime.datetime(2011, 8, 12, 12, 50, 56),
                context['assignments'][0].initial['start_date'])

    def testContextWithLongId(self):
        name = '%i' % random.randint(1000, 10000)
        foo = Level.objects.create(name='foo')
        bar = Level.objects.create(name='bar')
        obj = AccessObject.objects.create()
        obj.create(level=foo, start_date=datetime.datetime(2011, 8, 12, 12, 50, 56))
        obj.create(level=bar, start_date=datetime.datetime.now())
        context = self.widget.get_context(name, long(obj.id))
        self.assertFalse(context['hidden'])
        self.assertEqual(name, context['name'])
        self.assertFalse(context['is_public'])
        self.assertEqual(2, len(context['assignments']))
        self.assertEqual(datetime.datetime(2011, 8, 12, 12, 50, 56),
                context['assignments'][0].initial['start_date'])

    def testContextWithIntId(self):
        name = '%i' % random.randint(1000, 10000)
        foo = Level.objects.create(name='foo')
        bar = Level.objects.create(name='bar')
        obj = AccessObject.objects.create()
        obj.create(level=foo, start_date=datetime.datetime.now())
        obj.create(level=bar, start_date=datetime.datetime.now())
        context = self.widget.get_context(name, int(obj.id))
        self.assertFalse(context['hidden'])
        self.assertEqual(name, context['name'])
        self.assertFalse(context['is_public'])
        self.assertEqual(2, len(context['assignments']))

    def testContextWithNone(self):
        name = '%i' % random.randint(1000, 10000)
        context = self.widget.get_context(name, None)
        self.assertFalse(context['hidden'])
        self.assertEqual(name, context['name'])
        self.assertTrue(context['is_public'])
        # we want a blank field with a default start_date
        self.assertEqual(1, len(context['assignments']))
        now = datetime.datetime.now()
        form = context['assignments'][0]
        self.assertTrue(-20 < (now - form.initial['start_date']).seconds < 20)

    def testContextWithFormset(self):
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
                 name + '-assignments-2-start_date_0': u'',
                 name + '-assignments-2-start_date_1': u'',
                 name + '-assignments-2-end_date_0': u'',
                 name + '-assignments-2-end_date_1': u'',
             }
        value = self.widget.value_from_datadict(data, [], name)
        context = self.widget.get_context(name, value)
        self.assertEqual(name, context['name'])
        self.assertFalse(context['is_public'])
        self.assertEqual(3, len(context['assignments']))
