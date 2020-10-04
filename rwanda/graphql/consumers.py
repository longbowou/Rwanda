import channels_graphql_ws
from graphql_jwt.shortcuts import get_user_by_token

from rwanda.graphql.schemas.account import schema


def auth_middleware(next_middleware, root, info, *args, **kwds):
    """My custom GraphQL middleware."""
    # Invoke next middleware.
    if kwds.__contains__("auth_token"):
        user = get_user_by_token(kwds['auth_token'])
        info.context.user = user
    return next_middleware(root, info, *args, **kwds)


class AccountGraphqlWsConsumer(channels_graphql_ws.GraphqlWsConsumer):
    schema = schema
    middleware = [auth_middleware]

    async def on_connect(self, payload):
        pass
