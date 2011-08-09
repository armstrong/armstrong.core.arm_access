import datetime

from django.contrib.auth.models import User

from ..models import Level, AccessMembership
from ._utils import *


class TestAccessMemberships(ArmAccessTestCase):
    def setUp(self):
        self.user1 = User.objects.create_user("bob",
                                              "bob@example.com", "secret")
        self.user2 = User.objects.create_user("jim",
                                              "jim@example.com", "secret")
        self.al1 = Level.objects.create(name='Level 1')
        self.al2 = Level.objects.create(name='Level 2')

    def test_model(self):
        self.assertEqual(AccessMembership.objects.count(), 0)
        today = datetime.date.today()
        year_end = today + datetime.timedelta(days=365)
        s = AccessMembership(user=self.user1, level=self.al1,
                         start_date=today, end_date=year_end)
        s.save()
        self.assertEqual(s.active, True)
        self.assertEqual(AccessMembership.objects.count(), 1)
        self.assertEqual(self.al1.access_memberships.count(), 1)
        self.assertEqual(self.user1.access_memberships.count(), 1)

    def test_current_manager(self):
        self.assertEqual(AccessMembership.objects.count(), 0)
        self.assertEqual(AccessMembership.objects.current().count(), 0)
        today = datetime.date.today()
        year_end = today + datetime.timedelta(days=365)
        s = AccessMembership(user=self.user1, level=self.al1,
                         start_date=today, end_date=year_end)
        s.save()
        self.assertEqual(AccessMembership.objects.count(), 1)
        self.assertEqual(AccessMembership.objects.current().count(), 1)
        s.start_date = today + datetime.timedelta(days=1)
        s.save()
        self.assertEqual(AccessMembership.objects.count(), 1)
        self.assertEqual(AccessMembership.objects.current().count(), 0)
        s.start_date = s.end_date = today - datetime.timedelta(days=1)
        s.save()
        self.assertEqual(AccessMembership.objects.count(), 1)
        self.assertEqual(AccessMembership.objects.current().count(), 0)
        s.end_date = today + datetime.timedelta(days=1)
        s.save()
        self.assertEqual(AccessMembership.objects.count(), 1)
        self.assertEqual(AccessMembership.objects.current().count(), 1)
        s.active = False
        s.save()
        self.assertEqual(AccessMembership.objects.count(), 1)
        self.assertEqual(AccessMembership.objects.current().count(), 0)

    def test_current_manager_is_available_through_user(self):
        self.assertEqual(self.user1.access_memberships.count(), 0)
        today = datetime.date.today()
        year_end = today + datetime.timedelta(days=365)
        s = AccessMembership(user=self.user1, level=self.al1,
                         start_date=today, end_date=year_end)
        s.save()
        self.assertEqual(self.user1.access_memberships.count(), 1)
        self.assertEqual(
                self.user1.access_memberships.current().count(), 1)

    # Regression
    def test_users_have_different_current_query_sets(self):
        today = datetime.date.today()
        year_end = today + datetime.timedelta(days=365)
        user1_access_levels = self.user1.access_memberships.current()
        user2_access_levels = self.user2.access_memberships.current()
        self.assertEqual(user1_access_levels.count(), 0)
        self.assertEqual(user2_access_levels.count(), 0)
        s1 = AccessMembership(user=self.user1, level=self.al1,
                          start_date=today, end_date=year_end)
        s1.save()
        self.assertEqual(user1_access_levels.count(), 1)
        self.assertEqual(user2_access_levels.count(), 0)
        s2 = AccessMembership(user=self.user2, level=self.al1,
                          start_date=today, end_date=year_end)
        s2.save()
        self.assertEqual(user1_access_levels.count(), 1)
        self.assertEqual(user2_access_levels.count(), 1)
