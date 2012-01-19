import datetime

from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _


class Level(models.Model):
    """
    Represents a discrete access level that can be granted to a user
    """
    name = models.CharField(_('name'), max_length=50, unique=True)
    is_protected = models.BooleanField()

    class Meta:
        verbose_name = _('access level')
        verbose_name_plural = _('access levels')
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class AccessObject(models.Model):
    """
    An access model represents a set of access assignments. A content object
    that needs to be access restricted should have relate to exactly one
    AccessModel
    """
    @property
    def current_assignments(self):
        now = datetime.datetime.now()
        return self.assignments.filter(end_date__gte=now,
                                       start_date__lte=now).select_related()

    def add(self, *args, **kwargs):
        return self.assignments.add(*args, **kwargs)

    def create(self, *args, **kwargs):
        return self.assignments.create(*args, **kwargs)

    def clear(self):
        return self.assignments.all().delete()

    def __unicode__(self):
        return u'AccessObject - %i' % self.id

    def is_protected(self):
        for assignment in self.current_assignments:
            if not assignment.level.is_protected:
                return False
        return True



class Assignment(models.Model):
    """
    An access assignment grants access to an AccessModel for a set period of
    time
    """
    access_object = models.ForeignKey(AccessObject, related_name='assignments')
    level = models.ForeignKey(Level,
                              verbose_name=_("access level"),
                              related_name='assignments')
    start_date = models.DateTimeField(_('start date'))
    end_date = models.DateTimeField(_('end date'),
            default=datetime.datetime.max)

    def __unicode__(self):
        return u"%s - %s" % (self.level, self.access_object)


class AccessMembershipQuerySet(QuerySet):
    def current(self):
        today = datetime.date.today()
        return self.filter(active=True,
                           start_date__lte=today, end_date__gte=today)


class AccessMembershipManager(models.Manager):
    """
    Manager that provides current and active access level memberships.
    """
    use_for_related_fields = True

    def get_query_set(self):
        return AccessMembershipQuerySet(self.model)

    def current(self):
        return self.get_query_set().current()


class AccessMembership(models.Model):
    """
    A user subcription to a particular access level.
    """
    objects = AccessMembershipManager()

    user = models.ForeignKey('auth.User',
                             related_name='access_memberships')
    level = models.ForeignKey(Level, related_name='access_memberships')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s (%s)" % (self.user, self.level)

    @property
    def remaining(self):
        now = datetime.datetime.now()
        return self.end_date - now
