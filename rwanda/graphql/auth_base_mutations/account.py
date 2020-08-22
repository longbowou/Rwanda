from rwanda.graphql.decorators import account_required
from rwanda.graphql.mutations import DjangoModelMutation, DjangoModelDeleteMutation


class AccountDjangoModelMutation(DjangoModelMutation):
    class Meta:
        abstract = True

    @classmethod
    @account_required
    def mutate(cls, root, info, input):
        return super().mutate(root, info, input)


class AccountDjangoModelDeleteMutation(DjangoModelDeleteMutation):
    class Meta:
        abstract = True

    @classmethod
    @account_required
    def mutate(cls, root, info, input):
        return super().mutate(root, info, input)
