import graphene
from django.contrib.auth import authenticate
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from graphene_django.types import ErrorType
from graphql_jwt.refresh_token.shortcuts import create_refresh_token
from graphql_jwt.settings import jwt_settings

from rwanda.graphql.inputs import UserInput, UserUpdateInput, LoginInput
from rwanda.graphql.mutations import DjangoModelMutation, DjangoModelDeleteMutation
from rwanda.graphql.purchase.operations import cancel_service_purchase, \
    approve_service_purchase
from rwanda.graphql.types import ServiceCategoryType, ServiceType, AdminType, LitigationType
from rwanda.purchase.models import ServicePurchase
from rwanda.user.models import User, Admin


class LoginAdmin(graphene.Mutation):
    class Arguments:
        input = LoginInput(required=True)

    admin = graphene.Field(AdminType)
    errors = graphene.List(ErrorType)

    token = graphene.String()
    refresh_token = graphene.String()
    token_expires_in = graphene.Int()

    def mutate(self, info, input):
        user: User = User.objects.filter(Q(username=input.login) & Q(admin__isnull=False) |
                                         Q(email=input.login) & Q(admin__isnull=False)).first()
        if user is None:
            return LoginAdmin(errors=[ErrorType(field="login", messages=[_("Incorrect login")])])

        user = authenticate(username=user.username, password=input.password)
        if user is None:
            return LoginAdmin(errors=[ErrorType(field="password", messages=[_("Incorrect password")])])

        if not user.is_active:
            return LoginAdmin(
                errors=[ErrorType(field="login", messages=[_("Your account has been disabled")])])

        payload = jwt_settings.JWT_PAYLOAD_HANDLER(user, info.context)
        token = jwt_settings.JWT_ENCODE_HANDLER(payload, info.context)
        refresh_token = create_refresh_token(user).get_token()

        return LoginAdmin(admin=user.account, token=token, refresh_token=refresh_token,
                            token_expires_in=payload['exp'], errors=[])

class CreateServiceCategory(DjangoModelMutation):
    class Meta:
        model_type = ServiceCategoryType


class UpdateServiceCategory(DjangoModelMutation):
    class Meta:
        model_type = ServiceCategoryType
        for_update = True


class DeleteServiceCategory(DjangoModelDeleteMutation):
    class Meta:
        model_type = ServiceCategoryType


class UpdateService(DjangoModelMutation):
    class Meta:
        model_type = ServiceType
        only_fields = ('activated',)
        for_update = True


class AdminInput(UserInput):
    is_superuser = graphene.Boolean()
    is_active = graphene.Boolean()


class CreateAdmin(graphene.Mutation):
    class Arguments:
        input = AdminInput(required=True)

    admin = graphene.Field(AdminType)
    errors = graphene.List(ErrorType)

    def mutate(self, info, input):
        username_validator = UnicodeUsernameValidator()
        email_validator = EmailValidator()
        try:
            username_validator(input.username)
            if User.objects.filter(username=input.username).exists():
                return CreateAdmin(
                    errors=[ErrorType(field='username', messages=[_("An admin with that username already exists.")])]
                )
        except ValidationError as e:
            return CreateAdmin(
                errors=[ErrorType(field='username', messages=[_(e.message)])])

        try:
            email_validator(input.email)
            if User.objects.filter(email=input.email).exists():
                return CreateAdmin(
                    errors=[ErrorType(field='email', messages=[_("An admin with that email already exists.")])]
                )
        except ValidationError as e:
            return CreateAdmin(
                errors=[ErrorType(field='email', messages=[_(e.message)])])

        if input.password != input.password_confirmation:
            return CreateAdmin(
                errors=[
                    ErrorType(field='password', messages=[_("Password does not match password confirmation.")])]
            ),

        user = User(
            username=input.username,
            email=input.email
        )

        for field, value in input.items():
            if field in ('first_name', 'last_name', 'is_active', 'is_superuser') and value is not None:
                setattr(user, field, value)

        user.set_password(input.password)
        user.save()

        admin = Admin(user=user)
        admin.save()

        return CreateAdmin(admin=admin, errors=[])


class AdminUpdateInput(UserUpdateInput):
    id = graphene.UUID(required=True)
    is_superuser = graphene.Boolean()
    is_active = graphene.Boolean()


class UpdateAdmin(graphene.Mutation):
    class Arguments:
        input = AdminUpdateInput(required=True)

    admin = graphene.Field(AdminType)
    errors = graphene.List(ErrorType)

    def mutate(self, info, input):
        user = User.objects.filter(admin__id=input.id).first()
        if user is None:
            return CreateAdmin(
                errors=[ErrorType(field='id', messages=[_("Admin instance not found for id {}".format(input.id))])]
            )

        if input.username is not None:
            username_validator = UnicodeUsernameValidator()
            try:
                username_validator(input.username)
                if User.objects.filter(username=input.username).exclude(pk=user.id).exists():
                    return CreateAdmin(
                        errors=[
                            ErrorType(field='username', messages=[_("An admin with that username already exists.")])]
                    )
                user.username = input.username
            except ValidationError as e:
                return CreateAdmin(
                    errors=[
                        ErrorType(field='username', messages=[_(e.message)])])

        if input.email is not None:
            email_validator = EmailValidator()
            try:
                email_validator(input.email)
                if User.objects.filter(email=input.email).exclude(pk=user.id).exists():
                    return CreateAdmin(
                        errors=[ErrorType(field='email', messages=[_("An admin with that email already exists.")])]
                    )
                user.email = input.email
            except ValidationError as e:
                return CreateAdmin(
                    errors=[ErrorType(field='email', messages=[_(e.message)])])

        for field, value in input.items():
            if field in ('first_name', 'last_name', 'is_active', 'is_superuser') and value is not None:
                setattr(user, field, value)

        user.save()

        return CreateAdmin(admin=user.admin, errors=[])


class DeleteAdmin(DjangoModelDeleteMutation):
    class Meta:
        model_type = AdminType


class HandleLitigation(DjangoModelMutation):
    class Meta:
        model_type = LitigationType
        for_update = True
        only_fields = ('admin', 'decision')
        custom_input_fields = {"admin": graphene.UUID(required=True)}

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        if form.instance.handled:
            return cls(errors=[ErrorType(field="id", messages=[_("Litigation already handled.")])])

    @classmethod
    def post_save(cls, info, old_obj, form, obj, input):
        service_purchase: ServicePurchase = obj.service_purchase

        if obj.approved:
            approve_service_purchase(service_purchase)
            service_purchase.set_as_approved()

        if obj.canceled:
            cancel_service_purchase(service_purchase)
            service_purchase.set_as_canceled()

        service_purchase.save()

        obj.handled = True
        obj.save()
        obj.refresh_from_db()


class AdminMutations(graphene.ObjectType):
    login = LoginAdmin.Field()

    create_admin = CreateAdmin.Field()
    update_admin = UpdateAdmin.Field()
    delete_admin = DeleteAdmin.Field()

    create_service_category = CreateServiceCategory.Field()
    update_service_category = UpdateServiceCategory.Field()
    delete_service_category = DeleteServiceCategory.Field()

    update_service = UpdateService.Field()

    handle_litigation = HandleLitigation.Field()
