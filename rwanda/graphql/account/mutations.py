import graphene
from asgiref.sync import async_to_sync
from channels.auth import login
from django.contrib.auth import authenticate
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from graphene_django.types import ErrorType
from graphql_jwt.refresh_token.shortcuts import create_refresh_token
from graphql_jwt.settings import jwt_settings

from rwanda.accounting.models import Operation
from rwanda.graphql.auth_base_mutations.account import AccountDjangoModelMutation
from rwanda.graphql.decorators import anonymous_account_required, account_required
from rwanda.graphql.inputs import UserInput, UserUpdateInput, LoginInput, ChangePasswordInput
from rwanda.graphql.purchase.operations import credit_account, debit_account
from rwanda.graphql.types import AccountType, DepositType, RefundType, LitigationType, AuthType
from rwanda.purchase.models import ServicePurchase
from rwanda.user.models import User, Account


class LoginAccount(graphene.Mutation):
    class Arguments:
        input = LoginInput(required=True)

    account = graphene.Field(AccountType)
    errors = graphene.List(ErrorType)
    auth = graphene.Field(AuthType)

    @anonymous_account_required
    def mutate(self, info, input):
        user: User = User.objects.filter(Q(username=input.login) & Q(account__isnull=False) |
                                         Q(email=input.login) & Q(account__isnull=False)).first()
        if user is None:
            return LoginAccount(errors=[ErrorType(field="login", messages=[_("Incorrect username or email.")])])

        user = authenticate(username=user.username, password=input.password)
        if user is None:
            return LoginAccount(errors=[ErrorType(field="password", messages=[_("Incorrect password.")])])

        if not user.is_active:
            return LoginAccount(
                errors=[ErrorType(field="login", messages=[_("Your account has been disabled.")])])

        async_to_sync(login)(info.context.__dict__, user)
        info.context.session.save()

        payload = jwt_settings.JWT_PAYLOAD_HANDLER(user, info.context)
        token = jwt_settings.JWT_ENCODE_HANDLER(payload, info.context)
        refresh_token = create_refresh_token(user).get_token()

        auth = AuthType(token=token, refresh_token=refresh_token, token_expires_in=payload['exp'])

        return LoginAccount(account=user.account, auth=auth, errors=[])


class ChangeAccountPasswordInput(ChangePasswordInput):
    pass


class ChangeAccountPassword(graphene.Mutation):
    class Arguments:
        input = ChangeAccountPasswordInput(required=True)

    account = graphene.Field(AccountType)
    errors = graphene.List(ErrorType)

    @account_required
    def mutate(self, info, input):
        user: User = info.context.user

        if not user.check_password(input.current_password):
            return ChangeAccountPassword(
                errors=[ErrorType(field="currentPassword", messages=[_("Bad current password.")])])

        if input.current_password == input.password:
            return ChangeAccountPassword(
                errors=[
                    ErrorType(field='password',
                              messages=[_("The new password must different from the current password.")])]
            )

        if input.password != input.password_confirmation:
            return ChangeAccountPassword(
                errors=[
                    ErrorType(field='password', messages=[_("Password does not match password confirmation.")])]
            )

        user.set_password(input.password)
        user.save()

        return ChangeAccountPassword(account=user.account, errors=[])


# MUTATION DEPOSIT
class CreateDeposit(AccountDjangoModelMutation):
    class Meta:
        model_type = DepositType
        only_fields = ('amount',)

    @classmethod
    @transaction.atomic
    def pre_save(cls, info, old_obj, form, input):
        instance = form.instance
        account = info.context.user.account
        instance.account = account

        credit_account(account, instance.amount, Operation.DESC_CREDIT_FOR_DEPOSIT)

        form.save()
        instance.refresh_from_db()

        return cls(deposit=instance, errors=[])


# MUTATION REFUND
class CreateRefund(AccountDjangoModelMutation):
    class Meta:
        model_type = RefundType
        only_fields = ('amount', "phone_number")
        custom_input_fields = {'phone_number': graphene.String(required=True)}

    @classmethod
    @transaction.atomic
    def pre_save(cls, info, old_obj, form, input):
        account = Account.objects.select_for_update().get(pk=info.context.user.account.id)
        instance = form.instance
        instance.account = account

        if input.amount > account.balance:
            return cls(
                errors=[ErrorType(field='amount', messages=[_("Insufficient amount to process the refund.")])])

        debit_account(account, instance.amount, Operation.DESC_DEBIT_FOR_REFUND)

        form.save()
        instance.refresh_from_db()

        return cls(refund=instance, errors=[])


# ACCOUNT MUTATIONS
class AccountInput(UserInput):
    pass


class CreateAccount(graphene.Mutation):
    class Arguments:
        input = AccountInput(required=True)

    account = graphene.Field(AccountType)
    errors = graphene.List(ErrorType)

    @anonymous_account_required
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


class UpdateAccountInput(UserUpdateInput):
    pass


class UpdateAccount(graphene.Mutation):
    class Arguments:
        input = UpdateAccountInput(required=True)

    account = graphene.Field(AccountType)
    errors = graphene.List(ErrorType)

    @account_required
    def mutate(self, info, input):
        user = info.context.user

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


# MUTATION LITIGATION
class CreateLitigation(AccountDjangoModelMutation):
    class Meta:
        model_type = LitigationType
        only_fields = ('service_purchase', 'title', 'description')

    @classmethod
    @transaction.atomic
    def pre_save(cls, info, old_obj, form, input):
        account: Account = info.context.user.account

        if form.cleaned_data["service_purchase"].account_id != info.context.user.account.id:
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        service_purchase: ServicePurchase = form.cleaned_data["service_purchase"]
        if service_purchase.cannot_be_in_dispute:
            return cls(
                errors=[ErrorType(field="service_purchase", messages=[_("You cannot perform this action.")])])

        service_purchase.set_in_dispute()
        service_purchase.save()

        form.instance.account = account
        form.save()

        return cls(litigation=form.instance, errors=[])


class AccountMutations(graphene.ObjectType):
    login = LoginAccount.Field()

    create_deposit = CreateDeposit.Field()
    create_refund = CreateRefund.Field()

    create_account = CreateAccount.Field()
    update_account = UpdateAccount.Field()
    change_account_password = ChangeAccountPassword.Field()

    create_litigation = CreateLitigation.Field()
