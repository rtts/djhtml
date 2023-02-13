from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from djhtml.modes import DjHTML

try:
    TABWIDTH = settings.TABWIDTH
except AttributeError:
    TABWIDTH = 4


class DjHTMLMiddleware:
    """
    Django middleware class to indent HTML responses.

    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            "Content-Type" in response
            and response["Content-Type"] == "text/html; charset=utf-8"
        ):
            if "Content-Length" in response:
                raise ImproperlyConfigured(
                    "Please load DjHTMLMiddleware _after_ CommonMiddleware (otherwise"
                    ' the "Content-Length" header will be incorrect)'
                )
            response.content = (
                DjHTML(response.content.decode()).indent(TABWIDTH).encode()
            )
        return response
