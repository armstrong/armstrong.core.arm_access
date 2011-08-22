from functools import wraps
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse


class ImproperResponse(Exception):
    "An unexpected response type was returned from the view"
    pass


def redirect_on_deny(redirect_uri):
    def redirect(response):
        redirect = HttpResponseRedirect(redirect_uri)
        response.status_code = redirect.status_code
        response['Location'] = redirect['Location']
        return response
    return redirect


def render_on_deny(template_name):
    def rerender(response):
        response.template_name = template_name
        return response
    return rerender


def raise_on_deny(response):
    raise PermissionDenied


def protect(view,
            permission_check,
            permission_denied=raise_on_deny,
            template_object_name=None):
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

        if template_object_name is None:
            content_object = view.get_object()
        else:
            content_object = response.context_data[template_object_name]

        if not permission_check(request, content_object):
            return permission_denied(response)
        else:
            return response

    return wrapped
