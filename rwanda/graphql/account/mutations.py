import graphene
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _
from graphene_django.types import ErrorType

from rwanda.core.models import User, Account
from rwanda.graphql.mutations import DjangoModelMutation, DjangoModelDeleteMutation
from rwanda.graphql.types import ServiceType, AccountType


# SERVICE MUTATIONS
class CreateService(DjangoModelMutation):
    class Meta:
        model_type = ServiceType


class UpdateService(DjangoModelMutation):
    class Meta:
        model_type = ServiceType
        for_update = True


class DeleteService(DjangoModelDeleteMutation):
    class Meta:
        model_type = AccountType


# ACCOUNT MUTATIONS
class AccountInput(graphene.InputObjectType):
    username = graphene.String(required=True)
    first_name = graphene.String()
    last_name = graphene.String()
    password = graphene.String(required=True)
    password_confirmation = graphene.String(required=True)
    email = graphene.String(required=True)


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
            User.objects.filter(username=input.username).exists()
            if User.objects.filter(username=input.username).exists():
                return CreateAccount(
                    errors=[ErrorType(field='username', messages=[_("This username already exists")])]
                )

        except ValidationError:
            return CreateAccount(
                errors=[ErrorType(field='username', messages=[_("Your username does not meet the required format")])])

        try:
            email_validator(input.email)
            User.objects.filter(email=input.email).exists()
            if User.objects.filter(email=input.email).exists():
                return CreateAccount(
                    errors=[ErrorType(field='email', messages=[_("This email already exists")])]
                )

        except ValidationError:
            return CreateAccount(
                errors=[ErrorType(field='email', messages=[_("Your email does not meet the required format")])])

        if input.password != input.password_confirmation:
            return CreateAccount(
                errors=[
                    ErrorType(field='password', messages=[_("your password and its verification are not identical")])]
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
