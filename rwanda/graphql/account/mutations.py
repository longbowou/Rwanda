import json

import graphene
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.signing import Signer
from django.core.validators import EmailValidator
from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from graphene_django.types import ErrorType
from graphql_jwt.refresh_token.shortcuts import create_refresh_token
from graphql_jwt.settings import jwt_settings

from rwanda.account.tasks import on_litigation_opened_task
from rwanda.account.tasks import send_verification_mail_task
from rwanda.administration.utils import param_deposit_fee
from rwanda.graphql.auth_base_mutations.account import AccountDjangoModelMutation
from rwanda.graphql.decorators import anonymous_account_required, account_required
from rwanda.graphql.inputs import UserInput, UserUpdateInput, LoginInput, ChangePasswordInput
from rwanda.graphql.purchase.subscriptions import ServicePurchaseSubscription
from rwanda.graphql.types import AccountType, RefundType, LitigationType, AuthType
from rwanda.payments.models import Payment
from rwanda.payments.utils import get_signature
from rwanda.purchases.models import ServicePurchase
from rwanda.users.models import User, Account


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

        user.set_email_verification_expiration()
        user.set_password(input.password)
        user.save()

        account = Account(
            user=user
        )
        account.save()

        send_verification_mail_task.delay(str(user.id))

        return CreateAccount(account=account, errors=[])


class LoginAccount(graphene.Mutation):
    class Arguments:
        input = LoginInput(required=True)

    account = graphene.Field(AccountType)
    errors = graphene.List(ErrorType)
    auth = graphene.Field(AuthType)
    can_resend_verification_mail = graphene.Boolean()

    @anonymous_account_required
    def mutate(self, info, input):
        user: User = User.objects.filter(Q(username=input.login) & Q(account__isnull=False) |
                                         Q(email=input.login) & Q(account__isnull=False)).first()

        if user is None:
            return LoginAccount(errors=[ErrorType(field="login", messages=[_("Incorrect username or email.")])])

        if not user.email_verified:
            return LoginAccount(can_resend_verification_mail=True,
                                errors=[ErrorType(
                                    field="login",
                                    messages=[_(
                                        "Please check your mail to activate your account. You can resend a verification mail.")])])

        if not user.is_active:
            return LoginAccount(
                errors=[ErrorType(field="login", messages=[_("Your account has been disabled.")])])

        user = authenticate(username=user.username, password=input.password)
        if user is None:
            return LoginAccount(errors=[ErrorType(field="password", messages=[_("Incorrect password.")])])

        payload = jwt_settings.JWT_PAYLOAD_HANDLER(user, info.context)
        token = jwt_settings.JWT_ENCODE_HANDLER(payload, info.context)
        refresh_token = create_refresh_token(user).get_token()

        token = Signer().sign(token)

        auth = AuthType(token=token, refresh_token=refresh_token, token_expires_in=payload['exp'])

        return LoginAccount(account=user.account, auth=auth, errors=[])


class SendVerificationMail(graphene.Mutation):
    class Arguments:
        login = graphene.String(required=True)

    sent = graphene.Boolean()

    @anonymous_account_required
    def mutate(self, info, login):
        user: User = User.objects.filter(Q(username=login) & Q(account__isnull=False) |
                                         Q(email=login) & Q(account__isnull=False)).first()

        sent = False
        if user is not None:
            user.set_email_verification_expiration()
            user.save()

            send_verification_mail_task.delay(str(user.id))
            sent = True

        return SendVerificationMail(sent=sent)


class ActivateAccount(graphene.Mutation):
    class Arguments:
        user = graphene.UUID(required=True)

    activated = graphene.Boolean()
    message = graphene.String()

    @anonymous_account_required
    def mutate(self, info, user):
        user = User.objects.get(pk=user)
        if user is not None and user.email_verification_not_expired:
            user.email_verified = True
            user.save()

            return ActivateAccount(activated=True, message=_('Your account has been activated. You can now login.'))

        return ActivateAccount(activated=False, message=_(
            'Your verification link expired. Please try login and resend a new verification mail.'))


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


class InitiateDeposit(graphene.Mutation):
    class Arguments:
        amount = graphene.Int(required=True)

    errors = graphene.List(ErrorType)
    payment_url = graphene.String()
    form_data = graphene.String()
    payment_id = graphene.UUID()

    @account_required
    def mutate(self, info, amount):
        if (amount % 5) != 0:
            return InitiateDeposit(
                errors=[ErrorType(field='amount', messages=[_("Your amount must be a multiple of 5")])])

        if amount < 200:
            return InitiateDeposit(
                errors=[ErrorType(field='amount', messages=[_("Your amount must be a greater than 200")])])

        payment = Payment(amount=amount,
                          fee=param_deposit_fee() * amount,
                          account=info.context.user.account)
        payment.save()
        payment.signature = get_signature(payment)
        payment.save()

        data = {
            "cpm_amount": payment.total_amount,
            "cpm_currency": str(settings.CINETPAY_CURRENCY),
            "cpm_site_id": str(settings.CINETPAY_SITE_ID),
            "cpm_trans_id": str(payment.id),
            "cpm_trans_date": str(payment.created_at.strftime("%Y-%m-%d %H:%M:%S")),
            "cpm_payment_config": "SINGLE",
            "cpm_page_action": "PAYMENT",
            "cpm_version": "V1",
            "cpm_language": "fr",
            "apikey": str(settings.CINETPAY_API_KEY),
            "signature": str(payment.signature),
        }

        payment_url = settings.CINETPAY_PAYMENT_URL
        form_data = json.dumps(data)

        return InitiateDeposit(
            payment_url=payment_url,
            form_data=form_data,
            payment_id=payment.id,
            errors=[]
        )


class InitiateRefund(AccountDjangoModelMutation):
    class Meta:
        model_type = RefundType
        only_fields = ('amount', "phone_number", 'refund_way')
        custom_input_fields = {
            'phone_number': graphene.String(required=True),
            'refund_way': graphene.UUID(required=True),
        }

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        account = info.context.user.account
        if (input.amount % 5) != 0:
            return cls(
                errors=[ErrorType(field='amount', messages=[_("Your amount must be a multiple of 5")])])

        if input.amount < 200:
            return cls(
                errors=[ErrorType(field='amount', messages=[_("Your amount must be a greater than 200")])])

        if input.amount > account.balance:
            return cls(
                errors=[ErrorType(field='amount', messages=[_("Insufficient amount to process the refund.")])])

        form.instance.account = account


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
                    return UpdateAccount(
                        errors=[
                            ErrorType(field='username', messages=[_("An account with that username already exists.")])]
                    )
                user.username = input.username
            except ValidationError as e:
                return UpdateAccount(
                    errors=[
                        ErrorType(field='username', messages=[_(e.message)])])

        if input.email is not None:
            email_validator = EmailValidator()
            try:
                email_validator(input.email)
                if User.objects.filter(email=input.email).exclude(pk=user.id).exists():
                    return UpdateAccount(
                        errors=[ErrorType(field='email', messages=[_("An account with that email already exists.")])]
                    )
                user.email = input.email
            except ValidationError as e:
                return UpdateAccount(
                    errors=[ErrorType(field='email', messages=[_(e.message)])])

        for field, value in input.items():
            if field in ('first_name', 'last_name', 'phone_number') and value is not None:
                setattr(user, field, value)

        user.save()

        return UpdateAccount(account=user.account, errors=[])


class CreateLitigation(AccountDjangoModelMutation):
    class Meta:
        model_type = LitigationType
        only_fields = ('service_purchase', 'title', 'content')

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

        ServicePurchaseSubscription.broadcast(group=ServicePurchaseSubscription.name.format(str(service_purchase.id)))

        on_litigation_opened_task.delay(str(form.instance.id))

        return cls(litigation=form.instance, errors=[])


class AccountMutations(graphene.ObjectType):
    login = LoginAccount.Field()
    create_account = CreateAccount.Field()
    activate_account = ActivateAccount.Field()
    send_verification_mail = SendVerificationMail.Field()
    update_account = UpdateAccount.Field()
    change_account_password = ChangeAccountPassword.Field()

    initiate_deposit = InitiateDeposit.Field()
    initiate_refund = InitiateRefund.Field()

    create_litigation = CreateLitigation.Field()
