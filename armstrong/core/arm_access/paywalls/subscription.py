import datetime
import sys

from django.db.models import ObjectDoesNotExist
from ..models import Assignment
from .base import protect, redirect_on_deny, render_on_deny, raise_on_deny


class SubscriptionPaywall(object):
    """
    This content authorization backend is used to restrict access to content
    based on a user's subscription to the content's access level.

    Subscriptions will only be checked for content which is published
    exclusively in an access level with subscription_required set to True

    This paywall requires a TemplateResponse.

    :param permission_denied: a method that takes in a response for a content
        object that has been denied and returns a response appropriate for
        denied content
    """

    def __init__(self, permission_denied=None):
        if permission_denied is not None:
            self.permission_denied = permission_denied
        else:
            self.permission_denied = raise_on_deny

    def protect(self, view, permission_denied=None, **kwargs):
        if permission_denied is None:
            permission_denied = self.permission_denied
        return protect(view,
                       SubscriptionChecker.has_permission,
                       permission_denied,
                       **kwargs)


class SubscriptionChecker:
    @classmethod
    def required_permissions(cls, content_object):
        if content_object.access is None:
            return None
        assignments = content_object.access.current_assignments
        permissions = []
        for assignment in assignments:
            if assignment.level.is_protected:
                permissions.append(assignment.level)
            else:
                # there is an unprotected level with access
                return None
        return permissions

    @classmethod
    def has_permission(cls, request, content_object):
        required = SubscriptionChecker.required_permissions(content_object)

        # Only check content with subscription required
        if required is None:
            return True

        # Anonymous users can't view subscription content
        if not request.user.is_authenticated():
            return False

        # All staff can view subscription content
        if request.user.is_staff:
            return True

        # Also users with an active subscription to this level
        try:
            today = datetime.date.today()
            memberships = request.user.access_memberships.current()
            for membership in memberships:
                if membership.level in required:
                    return True
            return False
        except ObjectDoesNotExist:
            return False
