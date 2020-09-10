from django.contrib.auth import authenticate
from graphql_jwt.middleware import _authenticate


class JSONWebTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if _authenticate(request):
            user = authenticate(request)
            if user is not None:
                request.user = user

        response = self.get_response(request)
        return response
