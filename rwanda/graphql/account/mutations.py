import graphene
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from graphene_django.types import ErrorType

from rwanda.accounting.models import Operation, Fund
from rwanda.graphql.inputs import UserInput
from rwanda.graphql.mutations import DjangoModelMutation, DjangoModelDeleteMutation
from rwanda.graphql.types import AccountType, DepositType, RefundType
from rwanda.user.models import User, Account


class CreateDeposit(DjangoModelMutation):
    class Meta:
        model_type = DepositType

    @classmethod
    def post_mutate(cls, old_obj, form, obj, input):
        Operation(type=Operation.CREDIT, account=obj.account, amount=obj.amount,
                  fund=Fund.objects.get(label=Fund.ACCOUNTS)).save()
        Fund.objects.filter(label=Fund.ACCOUNTS).update(balance=F('balance') + obj.amount)
        Account.objects.filter(pk=input.account).update(balance=F('balance') + obj.amount)
        obj.refresh_from_db()


class CreateRefund(DjangoModelMutation):
    class Meta:
        model_type = RefundType

    @classmethod
    def pre_validations(cls, root, info, input, form):
        if input.amount > Account.objects.get(pk=input.account).balance:
            form.add_error("seller_service", ValidationError(_("Insufficient amount to process the refund.")))

    @classmethod
    def post_mutate(cls, old_obj, form, obj, input):
        Operation(type=Operation.DEBIT, account=obj.account, amount=obj.amount,
                  fund=Fund.objects.get(label=Fund.ACCOUNTS)).save()
        Fund.objects.filter(label=Fund.ACCOUNTS).update(balance=F('balance') - obj.amount)
        Account.objects.filter(pk=input.account).update(balance=F('balance') - obj.amount)
        obj.refresh_from_db()


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
            email=input.email,
        )

        for field, value in input.items():
            if field in ('first_name', 'last_name') and value is not None:
                setattr(user, field, value)

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
    create_deposit = CreateDeposit.Field()
    create_refund = CreateRefund.Field()

    create_account = CreateAccount.Field()
    update_account = UpdateAccount.Field()
    delete_account = DeleteAccount.Field()
