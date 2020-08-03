import graphene
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _
from graphene_django.types import ErrorType

from rwanda.graphql.inputs import UserInput
from rwanda.graphql.mutations import DjangoModelMutation, DjangoModelDeleteMutation
from rwanda.graphql.types import ServiceType, AccountType
from rwanda.user.models import User, Account


# SERVICE MUTATIONS
class CreateService(DjangoModelMutation):
    class Meta:
        model_type = ServiceType


class UpdateService(DjangoModelMutation):
    class Meta:
        model_type = ServiceType
        for_update = True
        exclude_fields = ("activated",)


class DeleteService(DjangoModelDeleteMutation):
    class Meta:
        model_type = AccountType


# ACCOUNT MUTATIONS
class AccountInput(UserInput):
    pass


class CreateAccount(graphene.Mutation):
    class Arguments:
        input = AccountInput(required=True)

    account = graphene.Field(AccountType)
    errors = graphene.List(ErrorType)

    def mutate(self, info, input):
        username_validator = UnicodeUsernameValidator()
        email_validator = EmailValidator()
        try:
            username_validator(input.username)
            if User.objects.filter(username=input.username).exists():
                return CreateAccount(
                    errors=[ErrorType(field='username', messages=[_("An account with that username already exists.")])]
                )
        except ValidationError as e:
            return CreateAccount(
                errors=[ErrorType(field='username', messages=[_(e.message)])])

        try:
            email_validator(input.email)
            if User.objects.filter(email=input.email).exists():
                return CreateAccount(
                    errors=[ErrorType(field='email', messages=[_("An account with that email already exists.")])]
                )

        except ValidationError as e:
            return CreateAccount(
                errors=[ErrorType(field='email', messages=[_(e.message)])])

        if input.password != input.password_confirmation:
            return CreateAccount(
                errors=[
                    ErrorType(field='password', messages=[_("Password does not match password confirmation.")])]
            ),

        user = User(
            username=input.username,
            first_name=input.first_name,
            last_name=input.last_name,
            email=input.email,
        )
        user.set_password(input.password)
        user.save()
        account = Account(
            user=user
        )
        account.save()
        return CreateAccount(account=account, errors=[])


class UpdateAccount(graphene.Mutation):
    class Arguments:
        input = AccountInput(required=True)

    account = graphene.Field(AccountType)
    errors = graphene.List(ErrorType)

    def mutate(self, info, input):
        pass


class DeleteAccount(DjangoModelDeleteMutation):
    class Meta:
        model_type = AccountType


class AccountMutations(graphene.ObjectType):
    create_service = CreateService.Field()
    update_service = UpdateService.Field()
    delete_service = DeleteService.Field()

    create_account = CreateAccount.Field()
    update_account = UpdateAccount.Field()
    delete_account = DeleteAccount.Field()
