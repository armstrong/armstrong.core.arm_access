import datetime
import StringIO
import sys
import shutil

from south.migration import Migrations

from django.contrib.auth.models import User
from django.core import management

from ._utils import *
from ..models import *
from .arm_access_support.models import *


class AccessFieldTestCase(ArmAccessTestCase):
    def setUp(self):
        super(AccessFieldTestCase, self).setUp()
        self.foo_level = Level.objects.create(name='foo')
        self.bar_level = Level.objects.create(name='bar')
        self.now = datetime.datetime.now()
        self.past = self.now + datetime.timedelta(days=-5)
        self.far_past = self.now + datetime.timedelta(days=-15)
        self.future = self.now + datetime.timedelta(days=-5)

    def testNoInteractionMeansNullAccessObject(self):
        obj = ArmAccessSupportContent.objects.create()
        self.assertEquals(0, AccessObject.objects.count())
        self.assertEquals(None, obj.access)

    def testSettingAccessToNoneExplicitly(self):
        obj = ArmAccessSupportContent.objects.create()
        obj.access = None
        self.assertEquals(0, AccessObject.objects.count())
        self.assertEquals(None, obj.access)

    def testSettingAccessToEmptyList(self):
        obj = ArmAccessSupportContent.objects.create()
        obj.access = []
        self.assertEquals(1, AccessObject.objects.count())
        self.assertEquals(0, Assignment.objects.count())
        self.assertNotEquals(None, obj.access)
        self.assertEquals([], list(obj.access.current_assignments))

    def testSettingAccessToSingleAssignment(self):
        obj = ArmAccessSupportContent.objects.create()
        assign = Assignment(level=self.foo_level, start_date=self.past)
        obj.access = assign
        self.assertEquals(1, AccessObject.objects.count())
        self.assertEquals(1, Assignment.objects.count())
        self.assertNotEquals(None, obj.access)
        self.assertEquals([assign], list(obj.access.current_assignments))

    def testSettingAccessToSingleAssignmentInArray(self):
        obj = ArmAccessSupportContent.objects.create()
        assign = Assignment(level=self.foo_level, start_date=self.past)
        obj.access = [assign]
        self.assertEquals(1, AccessObject.objects.count())
        self.assertEquals(1, Assignment.objects.count())
        self.assertNotEquals(None, obj.access)
        self.assertEquals([assign], list(obj.access.current_assignments))

    def testSettingAccessToMultipleAssignmentInArray(self):
        obj = ArmAccessSupportContent.objects.create()
        assign_foo = Assignment(level=self.foo_level, start_date=self.past)
        assign_bar = Assignment(level=self.bar_level, start_date=self.past)
        obj.access = [assign_foo, assign_bar]
        self.assertEquals(1, AccessObject.objects.count())
        self.assertEquals(2, Assignment.objects.count())
        self.assertNotEquals(None, obj.access)
        self.assertEquals([assign_foo, assign_bar],
                list(obj.access.current_assignments))

    def testSettingAccessToNull(self):
        obj = ArmAccessSupportContent.objects.create()
        assign_foo = Assignment(level=self.foo_level, start_date=self.past)
        assign_bar = Assignment(level=self.bar_level, start_date=self.past)
        obj.access = [assign_foo, assign_bar]
        obj.access = None
        self.assertEquals(0, AccessObject.objects.count())
        self.assertEquals(0, Assignment.objects.count())
        self.assertEquals(None, obj.access)

class AccessFieldSouthTestCase(ArmAccessTestCase):
    def testGenerateSouthMigration(self):
        tmp = StringIO.StringIO()
        sys.stdout = tmp
        sys.stderr = tmp

        management.call_command(
            "schemamigration",
            "arm_access_support",
            "-",
            initial=True,
        )
        migrations = Migrations("arm_access_support")
        shutil.rmtree(migrations.migrations_dir())

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
