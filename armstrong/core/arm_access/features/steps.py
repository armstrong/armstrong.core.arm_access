# -*- coding: utf-8 -*-
from lettuce import *

from django.conf import settings
from django.contrib.auth.models import User
import fudge
import random
import sys
import datetime as dt

from armstrong.core.arm_access.tests.arm_access_support.models import Content
from armstrong.core.arm_access.models import *
from armstrong.core.arm_access.paywalls.subscription import (
        SubscriptionPaywall, SubscriptionChecker)


@before.all
def setup_everything():
    world.everyone = Level.objects.create(name="everyone",
                                                is_protected=False)
    world.premium = Level.objects.create(name="premium",
                                               is_protected=True)
    world.user = User.objects.create(username="jjohnson", is_active=True)
    world.user.set_password('1234')


@before.each_scenario
def setup_scenario(scenario):
    pass


@after.each_scenario
def teardown_scenario(scenario):
    Content.objects.all().delete()
    AccessMembership.objects.all().delete()
    Assignment.objects.all().delete()


@step(u'A piece of content exists')
def a_piece_of_content_exists(step):
    world.content = Content.objects.create(name="The content")
    world.content.access = []


@step(u'it has no access defined')
def it_has_no_access_defined(step):
    world.content.access = None


@step(u'a user has no access levels defined')
def a_user_has_no_access_levels_defined(step):
    pass


@step(u'the default has_access backend is configured')
def the_default_has_access_backend_is_configured(step):
    world.backend = SubscriptionPaywall()


@step(u'the access check is performed')
def the_access_check_is_performed(step):
    request = fudge.Fake().has_attr(user=world.user)
    world.result = SubscriptionChecker.has_permission(request, world.content)


@step(u'access should be (.*)')
def access_should_be_denied(step, allowed_or_denied):
    if allowed_or_denied == 'allowed':
        assert world.result == True
    else:
        assert world.result == False


@step(u'it has a (.*) access node with a date in the (.*)')
def it_has_an_access_node_with_a_date(step, node_type, date):
    access_level = Level.objects.get(name=node_type)
    if date == 'future':
        access_date = dt.datetime.now() + dt.timedelta(days=5)
    else:
        access_date = dt.datetime.now() + dt.timedelta(days=-5)
    world.content.access.create(level=access_level, start_date=access_date)


@step(u'a user has the premium access level')
def a_user_has_the_premium_access_level(step):
    kwargs = {}
    kwargs['active'] = True
    kwargs['start_date'] = dt.datetime.now() + dt.timedelta(days=-5)
    kwargs['end_date'] = dt.datetime.now() + dt.timedelta(days=5)
    kwargs['level'] = world.premium
    kwargs['user'] = world.user
    AccessMembership.objects.create(**kwargs)
