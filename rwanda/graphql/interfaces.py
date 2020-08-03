import graphene


class UserInterface(graphene.Interface):
    username = graphene.String(required=True)
    email = graphene.String(required=True)
    first_name = graphene.String()
    last_name = graphene.String()
    full_name = graphene.String()

    @staticmethod
    def resolve_username(cls, info):
        return cls.user.username

    @staticmethod
    def resolve_email(cls, info):
        return cls.user.email

    @staticmethod
    def resolve_first_name(cls, info):
        return cls.user.first_name

    @staticmethod
    def resolve_last_name(cls, info):
        return cls.user.last_name

    @staticmethod
    def resolve_full_name(cls, info):
        return cls.user.get_full_name()
