from graphql_jwt.decorators import user_passes_test

account_required = user_passes_test(lambda user: user.is_authenticated and user.is_account)

anonymous_account = user_passes_test(
    lambda user: user.is_anonymous or user.is_authenticated and user.is_not_account)
