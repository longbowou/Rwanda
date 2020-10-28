from rwanda.graphql.decorators import admin_required
from rwanda.graphql.mutations import DjangoModelMutation, DjangoModelDeleteMutation


class AdminDjangoModelMutation(DjangoModelMutation):
    class Meta:
        abstract = True

    @classmethod
    @admin_required
    def mutate(cls, root, info, input):
        return super().mutate(root, info, input)


class AdminDjangoModelDeleteMutation(DjangoModelDeleteMutation):
    class Meta:
        abstract = True

    @classmethod
    @admin_required
    def mutate(cls, root, info, id):
        return super().mutate(root, info, id)
