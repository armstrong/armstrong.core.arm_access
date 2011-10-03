import datetime

from django.contrib.auth.models import User, AnonymousUser
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.template.response import HttpResponse, TemplateResponse
from django.test import TestCase
from django.utils.unittest import skip

from ._utils import *
from ..models import *
from ..paywalls.base import *
from ..paywalls.subscription import SubscriptionPaywall, SubscriptionChecker
from .arm_access_support.models import *


class DummyRequest(object):
    def __init__(self, user):
        self.user = user


class DummyRedirect(object):
    status_code = 301


def dummy_content_view(content_object):
    def inner(request):
        return TemplateResponse(request, 'content_detail.html', {
            'content_object': content_object,
        })
    return inner


class SubscriptionTestCase(ArmAccessTestCase):
    def setUp(self):
        super(SubscriptionTestCase, self).setUp()
        self.user = User.objects.create_user("bob",
                                             "bob@example.com", "secret")
        self.protected = Level.objects.create(name='Level 1',
                                              is_protected=True)
        self.public = Level.objects.create(name='Level 2', is_protected=False)
        self.now = datetime.datetime.now()
        self.dummy_content = ArmAccessSupportContent.objects.create()
        self.dummy_content.access = []
        self.dummy_content.access.create(
            level=self.protected, start_date=datetime.datetime.now())

        self.dummy_view = dummy_content_view(self.dummy_content)

    def test_subscription_paywall_denies_content_by_default(self):
        paywall = SubscriptionPaywall()
        protected_view = paywall.protect(self.dummy_view,
                template_object_name='content_object')
        request = DummyRequest(self.user)
        self.assertRaises(PermissionDenied, protected_view, request)

    def test_subscription_paywall_can_change_template(self):
        paywall = SubscriptionPaywall(render_on_deny('paywall.html'))
        protected_view = paywall.protect(self.dummy_view,
                template_object_name='content_object')
        response = protected_view(DummyRequest(self.user))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_rendered, False)
        self.assertEqual(response.template_name, 'paywall.html')

    def test_subscription_paywall_can_redirect(self):
        paywall = SubscriptionPaywall(redirect_on_deny('/login/'))
        protected_view = paywall.protect(self.dummy_view,
                template_object_name='content_object')
        response = protected_view(DummyRequest(self.user))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/login/')

    def test_subscription_paywall_allows_redirects_through(self):
        paywall = SubscriptionPaywall(redirect_on_deny('/login/'))
        protected_view = paywall.protect(lambda req: DummyRedirect())
        response = protected_view(DummyRequest(self.user))
        self.assertEqual(response.status_code, 301)

    def test_access_granted_by_current_subscription(self):
        paywall = SubscriptionPaywall()
        protected_view = paywall.protect(self.dummy_view,
                template_object_name='content_object')
        request = DummyRequest(self.user)
        self.assertRaises(PermissionDenied, protected_view, request)
        today = datetime.date.today()
        year_end = today + datetime.timedelta(days=365)
        AccessMembership.objects.create(user=self.user, level=self.protected,
                                    start_date=today, end_date=year_end)
        response = protected_view(request)
        AccessMembership.objects.filter(user=self.user).update(active=False)
        request.user = User.objects.get(pk=self.user.pk)
        self.assertRaises(PermissionDenied, protected_view, request)

    def test_non_template_response_raises_improper_response(self):
        def well_intentioned_view(request):
            return HttpResponse('Protect me!')

        paywall = SubscriptionPaywall()
        protected_view = paywall.protect(well_intentioned_view,
                template_object_name='object')
        request = DummyRequest(self.user)
        self.assertRaises(ImproperResponse, protected_view, request)

    def test_content_only_in_protected_pub_is_marked_as_protected(self):
        c = ArmAccessSupportContent.objects.create()

        #no publication = not protected
        self.assertFalse(SubscriptionChecker.required_permissions(c)
                is not None)
        c.access = Assignment(level=self.protected,
                              start_date=datetime.datetime.now())
        self.assertTrue(SubscriptionChecker.required_permissions(c)
                is not None)

    def test_content_only_in_unprotected_pub_is_not_protected(self):
        c = ArmAccessSupportContent.objects.create()
        c.access = [Assignment(level=self.protected,
                               start_date=datetime.datetime.now()),
                    Assignment(level=self.public,
                               start_date=datetime.datetime.now()),
                   ]
        self.assertFalse(SubscriptionChecker.required_permissions(c)
                is not None)

    def test_content_published_in_free_pub_is_not_protected(self):
        c = ArmAccessSupportContent.objects.create()

        c.access = []
        c.access.create(level=self.protected,
                        start_date=datetime.datetime.now())
        self.assertTrue(SubscriptionChecker.required_permissions(c)
                is not None)
        c.access.create(level=self.public, start_date=datetime.datetime.now())
        self.assertFalse(SubscriptionChecker.required_permissions(c)
                is not None)
        #sanity check that we added two publications in this test
        self.assertEqual(c.access.assignments.count(), 2)

    def test_content_unpublished_in_free_pub_is_still_protected(self):
        c = ArmAccessSupportContent.objects.create()

        c.access = Assignment(level=self.protected,
                              start_date=datetime.datetime.now())
        self.assertTrue(SubscriptionChecker.required_permissions(c)
                is not None)
        c.access.add(Assignment(level=self.public,
                                start_date=datetime.datetime.now() +
                                           datetime.timedelta(days=999)))
        #since it's not published in public, it's still protected
        self.assertTrue(SubscriptionChecker.required_permissions(c)
                is not None)

    def test_anonymous_user_has_access_to_unprotected_content(self):
        c = ArmAccessSupportContent.objects.create()
        self.assertTrue(SubscriptionChecker.has_permission(
                        DummyRequest(AnonymousUser()), c))

    def test_anonymous_user_has_access_to_content_with_unprotected(self):
        c = ArmAccessSupportContent.objects.create()
        c.access = Assignment(level=self.public, start_date=self.now)
        self.assertTrue(SubscriptionChecker.has_permission(
            DummyRequest(AnonymousUser()), c))

    def test_anonymous_user_has_no_access_to_protected_content(self):
        c = ArmAccessSupportContent.objects.create()
        c.access = Assignment(level=self.protected, start_date=self.now)
        self.assertFalse(SubscriptionChecker.has_permission(
                        DummyRequest(AnonymousUser()), c))

    def test_staff_user_has_access_to_protected_content(self):
        c = ArmAccessSupportContent.objects.create()
        c.access = Assignment(level=self.protected, start_date=self.now)
        self.user.is_staff = True
        self.assertTrue(SubscriptionChecker.has_permission(
                                            DummyRequest(self.user), c))

    def test_user_with_unrelated_access_cant_access_protected_content(self):
        c = ArmAccessSupportContent.objects.create()
        c.access = Assignment(level=self.protected, start_date=self.now)
        new_level = Level.objects.create(name="Magic Pony")
        today = datetime.date.today()
        year_end = today + datetime.timedelta(days=365)
        AccessMembership.objects.create(user=self.user, level=new_level,
                                    start_date=today, end_date=year_end)
        self.assertFalse(SubscriptionChecker.has_permission(
                                        DummyRequest(self.user), c))
