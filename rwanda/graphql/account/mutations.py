import graphene
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from graphene_django.types import ErrorType

from rwanda.accounting.models import Operation, Fund
from rwanda.graphql.inputs import UserInput, UserUpdateInput
from rwanda.graphql.mutations import DjangoModelMutation, DjangoModelDeleteMutation
from rwanda.graphql.types import AccountType, DepositType, RefundType, LitigationType
from rwanda.purchase.models import ServicePurchase, Litigation
from rwanda.user.models import User, Account


# MUTATION DEPOSIT
class CreateDeposit(DjangoModelMutation):
    class Meta:
        model_type = DepositType

    @classmethod
    def post_mutate(cls, info, old_obj, form, obj, input):
        Operation(type=Operation.TYPE_CREDIT, account=obj.account, amount=obj.amount,
                  description=Operation.DESC_CREDIT_FOR_DEPOSIT,
                  fund=Fund.objects.get(label=Fund.ACCOUNTS)).save()
        Fund.objects.filter(label=Fund.ACCOUNTS).update(balance=F('balance') + obj.amount)
        Account.objects.filter(pk=input.account).update(balance=F('balance') + obj.amount)
        obj.refresh_from_db()


#MUTATION REFUND
class CreateRefund(DjangoModelMutation):
    class Meta:
        model_type = RefundType

    @classmethod
    def pre_validations(cls, info, input, form):
        if input.amount > Account.objects.get(pk=input.account).balance:
            form.add_error("seller_service", ValidationError(_("Insufficient amount to process the refund.")))

    @classmethod
    def post_mutate(cls, info, old_obj, form, obj, input):
        Operation(type=Operation.TYPE_DEBIT, account=obj.account, amount=obj.amount,
                  description=Operation.DESC_DEBIT_FOR_REFUND,
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
            )

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


class AccountUpdateInput(UserUpdateInput):
    id = graphene.UUID(required=True)
    is_active = graphene.Boolean()


class UpdateAccount(graphene.Mutation):
    class Arguments:
        input = AccountUpdateInput(required=True)

    account = graphene.Field(AccountType)
    errors = graphene.List(ErrorType)

    def mutate(self, info, input):
        user = User.objects.filter(account__id=input.id).first()
        if user is None:
            return CreateAccount(
                errors=[ErrorType(field='id', messages=[_("Account instance not found ")])]
            )

        if input.username is not None:
            username_validator = UnicodeUsernameValidator()
            try:
                username_validator(input.username)
                if User.objects.filter(username=input.username).exclude(pk=user.id).exists():
                    return CreateAccount(
                        errors=[
                            ErrorType(field='username', messages=[_("An account with that username already exists.")])]
                    )
                user.username = input.username
            except ValidationError as e:
                return CreateAccount(
                    errors=[
                        ErrorType(field='username', messages=[_(e.message)])])

        if input.email is not None:
            email_validator = EmailValidator()
            try:
                email_validator(input.email)
                if User.objects.filter(email=input.email).exclude(pk=user.id).exists():
                    return CreateAccount(
                        errors=[ErrorType(field='email', messages=[_("An account with that email already exists.")])]
                    )
                user.email = input.email
            except ValidationError as e:
                return CreateAccount(
                    errors=[ErrorType(field='email', messages=[_(e.message)])])

        for field, value in input.items():
            if field in ('first_name', 'last_name') and value is not None:
                setattr(user, field, value)

        user.save()

        return CreateAccount(account=user.account, errors=[])


class DeleteAccount(DjangoModelDeleteMutation):
    class Meta:
        model_type = AccountType


# INPUT LITIGATION
class LitigationInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    description = graphene.String(required=True)


# MUTATION LITIGATION
class CreateLitigation(graphene.Mutation):
    class Meta:
        model_type = LitigationType
        only_fields = ("account", 'admin', 'service_purchase', 'title', 'description')


class UpdateLitigation(graphene.Mutation):
    class Meta:
        model_type = LitigationType
        for_update = True
        exclude_fields = ('service_purchase', 'account', 'title', 'description')

    @classmethod
    def post_mutate(cls, info, old_obj, form, obj, input):
        if input.is_main is not None and obj.is_main:
            Litigation.objects.exclude(pk=input.id).update(handle=True)


class DeleteLitigation(graphene.Mutation):
    class Meta:
        model_type = LitigationType


class AccountMutations(graphene.ObjectType):
    create_deposit = CreateDeposit.Field()
    create_refund = CreateRefund.Field()

    create_account = CreateAccount.Field()
    update_account = UpdateAccount.Field()
    delete_account = DeleteAccount.Field()

    create_litigation = CreateLitigation.Field()
    update_litigation = UpdateLitigation.Field()
    delete_litigation = DeleteLitigation.Field()
