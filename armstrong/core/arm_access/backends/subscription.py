import datetime
import sys
from functools import wraps

from django.db.models import ObjectDoesNotExist
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from ..models import Assignment


class ImproperResponse(Exception):
    "An unexpected response type was returned from the view"
    pass


class SubscriptionPaywall(object):
    """
    This content authorization backend is used to restrict access to content
    based on a user's subscription to the content's access level.

    Subscriptions will only be checked for content which is published
    exclusively in an access level with subscription_required set to True

    This paywall requires a TemplateResponse.

    :param template_object_name: The name of the content object in the
    response context.
    :param redirect_uri: The path to redirect to if permission is denied.
    :param paywall_template_name: The template used to render the response if
    permission is denied. Only used if `redirect_uri` is not provided.
    """

    def __init__(self, template_object_name='object', redirect_uri=None,
                 paywall_template_name=None):
        self.template_object_name = template_object_name
        self.paywall_template_name = paywall_template_name
        self.redirect_uri = redirect_uri

    def protect(self, view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            response = view(request, *args, **kwargs)

            if response.status_code != 200:
                # Redirects, errors, etc. should pass through.
                return response

            # Can't handle non-template responses
            if not isinstance(response, TemplateResponse):
                raise ImproperResponse('Protected view must return'
                                       ' a TemplateResponse object')

            content_object = response.context_data[self.template_object_name]
            if not self.has_permission(request, content_object):
                return self.deny_permission(response)
            else:
                return response

        return wrapped

    def required_permissions(self, content_object):
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

    def is_content_protected(self, content_object):
        return self.required_permissions(content_object) is not None

    def has_permission(self, request, content_object):
        required = self.required_permissions(content_object)

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

    def deny_permission(self, response):
        if self.redirect_uri:
            redirect = HttpResponseRedirect(self.redirect_uri)
            response.status_code = redirect.status_code
            response['Location'] = redirect['Location']
            return response
        elif self.paywall_template_name:
            response.template_name = self.paywall_template_name
            return response

        raise PermissionDenied
