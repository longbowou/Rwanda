from django.core.signing import Signer
from graphql_jwt.shortcuts import get_user_by_token
from graphql_jwt.utils import get_credentials


class JSONWebTokenBackend:

    def authenticate(self, request=None, **kwargs):
        if request is None or getattr(request, '_jwt_token_auth', False):
            return None

        token = get_credentials(request, **kwargs)

        try:
            token = Signer().unsign(token)
            if token is not None:
                return get_user_by_token(token, request)
        except Exception:
            pass

        return None

    def get_user(self, user_id):
        return None
