import datetime

from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.template.response import HttpResponse, TemplateResponse
from django.test import TestCase
from django.utils.unittest import skip

from ._utils import *
from ..models import *
from ..backends.subscription import SubscriptionPaywall, ImproperResponse
from ..arm_access_support.models import *


class DummyRequest(object):
    def __init__(self, user):
        self.user = user


class SubscriptionTestCase(ArmAccessTestCase):
    def setUp(self):
        super(SubscriptionTestCase, self).setUp()
        self.user = User.objects.create_user("bob",
                                             "bob@example.com", "secret")
        self.level1 = Level.objects.create(name='Level 1', is_protected=True)
        self.level2 = Level.objects.create(name='Level 2', is_protected=False)
        self.dummy_content = Content.objects.create()
        self.dummy_content.access = []
        self.dummy_content.access.create(
            level=self.level1, start_date=datetime.datetime.now())

        def dummy_content_view(request, content_object=self.dummy_content):
            return TemplateResponse(request, 'content_detail.html', {
                'content_object': content_object,
            })
        self.dummy_view = dummy_content_view

    def test_subscription_paywall_denies_content_by_default(self):
        paywall = SubscriptionPaywall(template_object_name='content_object')
        protected_view = paywall.protect(self.dummy_view)
        request = DummyRequest(self.user)
        self.assertRaises(PermissionDenied, protected_view, request)

    def test_subscription_paywall_can_change_template(self):
        paywall = SubscriptionPaywall(template_object_name='content_object',
                                      paywall_template_name='paywall.html')
        protected_view = paywall.protect(self.dummy_view)
        response = protected_view(DummyRequest(self.user))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_rendered, False)
        self.assertEqual(response.template_name, 'paywall.html')

    def test_subscription_paywall_can_redirect(self):
        paywall = SubscriptionPaywall(template_object_name='content_object',
                                      redirect_uri='/login/')
        protected_view = paywall.protect(self.dummy_view)
        response = protected_view(DummyRequest(self.user))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/login/')

    def test_access_granted_by_current_subscription(self):
        paywall = SubscriptionPaywall(template_object_name='content_object')
        protected_view = paywall.protect(self.dummy_view)
        request = DummyRequest(self.user)
        self.assertRaises(PermissionDenied, protected_view, request)
        today = datetime.date.today()
        year_end = today + datetime.timedelta(days=365)
        AccessMembership.objects.create(user=self.user, level=self.level1,
                                    start_date=today, end_date=year_end)
        response = protected_view(request)
        AccessMembership.objects.filter(user=self.user).update(active=False)
        request.user = User.objects.get(pk=self.user.pk)
        self.assertRaises(PermissionDenied, protected_view, request)

    def test_non_template_response_raises_improper_response(self):
        def well_intentioned_view(request):
            return HttpResponse('Protect me!')

        paywall = SubscriptionPaywall(template_object_name='content_object')
        protected_view = paywall.protect(well_intentioned_view)
        request = DummyRequest(self.user)
        self.assertRaises(ImproperResponse, protected_view, request)

    def test_content_only_in_protected_pub_is_marked_as_protected(self):
        c = Content.objects.create()
        paywall = SubscriptionPaywall(template_object_name='content_object')

        def dummy_content_view(request, content_object=c):
            return TemplateResponse(request, 'content_detail.html', {
                'content_object': content_object,
            })
        paywall.protect(dummy_content_view)
        #no publication = not protected
        self.assertFalse(paywall.is_content_protected(c))
        c.access = Assignment(level=self.level1,
                              start_date=datetime.datetime.now())
        self.assertTrue(paywall.is_content_protected(c))

    def test_content_only_in_unprotected_pub_is_not_protected(self):
        c = Content.objects.create()
        paywall = SubscriptionPaywall(template_object_name='content_object')

        def dummy_content_view(request, content_object=c):
            return TemplateResponse(request, 'content_detail.html', {
                'content_object': content_object,
            })
        paywall.protect(dummy_content_view)
        c.access = [Assignment(level=self.level1,
                               start_date=datetime.datetime.now()),
                    Assignment(level=self.level2,
                               start_date=datetime.datetime.now()),
                   ]
        self.assertFalse(paywall.is_content_protected(c))

    def test_content_published_in_free_pub_is_not_protected(self):
        c = Content.objects.create()
        paywall = SubscriptionPaywall(template_object_name='content_object')

        def dummy_content_view(request, content_object=c):
            return TemplateResponse(request, 'content_detail.html', {
                'content_object': content_object,
            })
        paywall.protect(dummy_content_view)
        c.access = []
        c.access.create(level=self.level1, start_date=datetime.datetime.now())
        #level1 = protected
        self.assertTrue(paywall.is_content_protected(c))
        c.access.create(level=self.level2, start_date=datetime.datetime.now())
        #adding level2 unprotects content
        self.assertFalse(paywall.is_content_protected(c))
        #sanity check that we added two publications in this test
        self.assertEqual(c.access.assignments.count(), 2)

    def test_content_unpublished_in_free_pub_is_still_protected(self):
        c = Content.objects.create()
        paywall = SubscriptionPaywall(template_object_name='content_object')

        def dummy_content_view(request, content_object=c):
            return TemplateResponse(request, 'content_detail.html', {
                'content_object': content_object,
            })
        paywall.protect(dummy_content_view)
        c.access = Assignment(level=self.level1,
                              start_date=datetime.datetime.now())
        #level1 = protected
        self.assertTrue(paywall.is_content_protected(c))
        c.access.add(Assignment(level=self.level2,
                                start_date=datetime.datetime.now() +
                                           datetime.timedelta(days=999)))
        #since it's not published in level2, it's still protected
        self.assertTrue(paywall.is_content_protected(c))
