import datetime

from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _


class AccessLevel(models.Model):
    """
    A model for content access.
    """
    name = models.CharField(_('name'), max_length=50, unique=True)
    is_protected = models.BooleanField()

    class Meta:
        verbose_name = _('access level')
        verbose_name_plural = _('access levels')
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class AccessNodeManager(models.Manager):
    def for_content(self, content_object):
        content_type = ContentType.objects.get_for_model(
                                content_object.__class__)
        return self.filter(
                        content_type=content_type,
                        object_id=content_object.id,
                    )


class AccessNode(models.Model):
    objects = AccessNodeManager()

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content = generic.GenericForeignKey('content_type', 'object_id')
    access_level = models.ForeignKey(AccessLevel, verbose_name=_("access level"))
    access_date = models.DateTimeField(_('access date'))

    class Meta:
        unique_together = ('object_id', 'content_type', 'access_level')

    def __unicode__(self):
        return u"%s - %s" % (self.access_level, self.content)


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
    access_level = models.ForeignKey(AccessLevel,
                                    related_name='access_memberships')
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s (%s)" % (self.user, self.access_level)

    @property
    def remaining(self):
        today = datetime.date.today()
        return self.end_date - today
