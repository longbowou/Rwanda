import graphene

from rwanda.user.models import Account


class UserInterface(graphene.Interface):
    username = graphene.String(required=True)
    email = graphene.String(required=True)
    is_online = graphene.Boolean(required=True)
    is_active = graphene.Boolean(required=True)
    is_active_display = graphene.String(required=True)
    last_login = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    full_name = graphene.String()
    phone_number = graphene.String()
    image_url = graphene.String()

    @staticmethod
    def resolve_username(cls, info):
        cls: Account
        return cls.user.username

    @staticmethod
    def resolve_email(cls, info):
        cls: Account
        return cls.user.email

    @staticmethod
    def resolve_first_name(cls, info):
        cls: Account
        return cls.user.first_name

    @staticmethod
    def resolve_last_name(cls, info):
        cls: Account
        return cls.user.last_name

    @staticmethod
    def resolve_full_name(cls, info):
        cls: Account
        return cls.user.get_full_name()

    @staticmethod
    def resolve_is_online(cls, info):
        cls: Account
        return cls.user.is_online

    @staticmethod
    def resolve_last_login(cls, info):
        cls: Account
        return cls.user.last_login_display

    @staticmethod
    def resolve_phone_number(cls, info):
        cls: Account
        return cls.user.phone_number

    @staticmethod
    def resolve_image_url(cls, info):
        cls: Account
        return cls.user.image_url

    @staticmethod
    def resolve_is_active(cls, info):
        cls: Account
        return cls.user.is_active

    @staticmethod
    def resolve_is_active_display(cls, info):
        cls: Account
        return cls.user.is_active_display
