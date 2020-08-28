from graphql_jwt.decorators import user_passes_test

from rwanda.graphql.exceptions import AccountRequiredException, AnonymousAccountRequiredException

account_required = user_passes_test(lambda user: user.is_authenticated and user.is_account, AccountRequiredException)

anonymous_account_required = user_passes_test(
    lambda user: user.is_anonymous or user.is_authenticated and user.is_not_account, AnonymousAccountRequiredException)
