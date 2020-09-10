from functools import wraps

from rwanda.graphql.exceptions import AccountRequiredException


def account_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_anonymous or request.user.is_not_account:
            raise AccountRequiredException

        return view_func(request, *args, **kwargs)

    return wrapped_view
