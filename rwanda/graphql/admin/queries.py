import graphene

from rwanda.graphql.decorators import admin_required
from rwanda.graphql.types import AdminType


class AdminQueries(graphene.ObjectType):
    admin = graphene.Field(AdminType, required=True)

    @admin_required
    def resolve_admin(root, info, **kwargs):
        return info.context.user.admin
