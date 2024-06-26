import graphene
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

from rwanda.account.models import Refund
from rwanda.account.tasks import on_litigation_handled_task
from rwanda.account.tasks import on_service_accepted_or_rejected_task
from rwanda.graphql.auth_base_mutations.admin import AdminDjangoModelDeleteMutation, AdminDjangoModelMutation
from rwanda.graphql.decorators import anonymous_admin_required, admin_required
from rwanda.graphql.inputs import UserInput, UserUpdateInput, LoginInput, ChangePasswordInput
from rwanda.graphql.purchase.operations import cancel_service_purchase, \
    approve_service_purchase
from rwanda.graphql.purchase.subscriptions import ServicePurchaseSubscription
from rwanda.graphql.types import ServiceCategoryType, ServiceType, AdminType, LitigationType, AuthType, RefundWayType, \
    ParameterType, UserType, RefundType
from rwanda.payments.models import Payment
from rwanda.payments.utils import get_auth_token, get_available_balance, transfer_money, add_contact
from rwanda.purchases.models import ServicePurchase, Litigation
from rwanda.services.models import Service, ServiceCategory
from rwanda.users.models import User, Admin


class LoginAdmin(graphene.Mutation):
    class Arguments:
        input = LoginInput(required=True)

    admin = graphene.Field(AdminType)
    errors = graphene.List(ErrorType)
    auth = graphene.Field(AuthType)

    @anonymous_admin_required
    def mutate(self, info, input):
        user: User = User.objects.filter(Q(username=input.login) & Q(admin__isnull=False) |
                                         Q(email=input.login) & Q(admin__isnull=False) |
                                         Q(username=input.login) & Q(is_superuser=True) |
                                         Q(email=input.login) & Q(is_superuser=True)).first()
        if user is None:
            return LoginAdmin(errors=[ErrorType(field="login", messages=[_("Incorrect username or email.")])])

        if not user.is_active:
            return LoginAdmin(
                errors=[ErrorType(field="login", messages=[_("Your account has been disabled.")])])

        user = authenticate(username=user.username, password=input.password)
        if user is None:
            return LoginAdmin(errors=[ErrorType(field="password", messages=[_("Incorrect password.")])])

        payload = jwt_settings.JWT_PAYLOAD_HANDLER(user, info.context)
        token = jwt_settings.JWT_ENCODE_HANDLER(payload, info.context)
        refresh_token = create_refresh_token(user).get_token()

        token = Signer().sign(token)

        auth = AuthType(token=token, refresh_token=refresh_token, token_expires_in=payload['exp'])

        if user.is_superuser and user.is_not_admin:
            admin = Admin(user=user)
            admin.save()

        return LoginAdmin(admin=user.admin, auth=auth, errors=[])


class ChangeAdminPasswordInput(ChangePasswordInput):
    pass


class ChangeAdminPassword(graphene.Mutation):
    class Arguments:
        input = ChangeAdminPasswordInput(required=True)

    admin = graphene.Field(AdminType)
    errors = graphene.List(ErrorType)

    @admin_required
    def mutate(self, info, input):
        user: User = info.context.user

        if not user.check_password(input.current_password):
            return ChangeAdminPassword(
                errors=[ErrorType(field="currentPassword", messages=[_("Bad current password.")])])

        if input.current_password == input.password:
            return ChangeAdminPassword(
                errors=[
                    ErrorType(field='password',
                              messages=[_("The new password must different from the current password.")])]
            )

        if input.password != input.password_confirmation:
            return ChangeAdminPassword(
                errors=[
                    ErrorType(field='password', messages=[_("Password does not match password confirmation.")])]
            )

        user.set_password(input.password)
        user.save()

        return ChangeAdminPassword(admin=user.admin, errors=[])


class UpdateAdminProfileInput(UserUpdateInput):
    id = graphene.UUID(required=True)
    pass


class UpdateAdminProfile(graphene.Mutation):
    class Arguments:
        input = UpdateAdminProfileInput(required=True)

    admin = graphene.Field(AdminType)
    errors = graphene.List(ErrorType)

    @admin_required
    def mutate(self, info, input):
        user = info.context.user

        if input.username is not None:
            username_validator = UnicodeUsernameValidator()
            try:
                username_validator(input.username)
                if User.objects.filter(username=input.username).exclude(pk=user.id).exists():
                    return UpdateAdminProfile(
                        errors=[
                            ErrorType(field='username', messages=[_("An account with that username already exists.")])]
                    )
                user.username = input.username
            except ValidationError as e:
                return UpdateAdminProfile(
                    errors=[
                        ErrorType(field='username', messages=[_(e.message)])])

        if input.email is not None:
            email_validator = EmailValidator()
            try:
                email_validator(input.email)
                if User.objects.filter(email=input.email).exclude(pk=user.id).exists():
                    return UpdateAdminProfile(
                        errors=[ErrorType(field='email', messages=[_("An account with that email already exists.")])]
                    )
                user.email = input.email
            except ValidationError as e:
                return UpdateAdminProfile(
                    errors=[ErrorType(field='email', messages=[_(e.message)])])

        for field, value in input.items():
            if field in ('first_name', 'last_name') and value is not None:
                setattr(user, field, value)

        user.save()

        return UpdateAdminProfile(admin=user.admin, errors=[])


class CreateServiceCategory(AdminDjangoModelMutation):
    class Meta:
        model_type = ServiceCategoryType
        exclude_fields = ('index',)

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        index = 0
        category = ServiceCategory.objects.order_by('-index').first()
        if category is not None:
            index = category.index + 1

        form.instance.index = index


class UpdateServiceCategory(AdminDjangoModelMutation):
    class Meta:
        model_type = ServiceCategoryType
        exclude_fields = ('index',)
        for_update = True


class PublishUnPublishService(AdminDjangoModelMutation):
    class Meta:
        model_type = ServiceType
        for_update = True
        only_fields = ("published_by_admin",)


class DeleteServiceCategory(AdminDjangoModelDeleteMutation):
    class Meta:
        model_type = ServiceCategoryType


class AcceptService(AdminDjangoModelMutation):
    class Meta:
        model_type = ServiceType
        for_update = True
        only_fields = ("",)

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        service: Service = form.instance
        if service.cannot_be_accepted:
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        service.set_as_accepted()

    @classmethod
    def post_save(cls, info, old_obj, form, obj, input):
        on_service_accepted_or_rejected_task.delay(str(obj.id))


class RejectService(AdminDjangoModelMutation):
    class Meta:
        model_type = ServiceType
        for_update = True
        only_fields = ("rejected_reason",)
        extra_input_fields = {"rejected_reason": graphene.String(required=True)}

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        service: Service = form.instance
        if service.cannot_be_rejected:
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        service.set_as_rejected()

    @classmethod
    def post_save(cls, info, old_obj, form, obj, input):
        on_service_accepted_or_rejected_task.delay(str(obj.id))


class DeleteService(AdminDjangoModelDeleteMutation):
    class Meta:
        model_type = ServiceType


class AdminInput(UserInput):
    is_superuser = graphene.Boolean()
    is_active = graphene.Boolean()


class CreateAdmin(graphene.Mutation):
    class Arguments:
        input = AdminInput(required=True)

    admin = graphene.Field(AdminType)
    errors = graphene.List(ErrorType)

    @admin_required
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


class UpdateAdminInput(UserUpdateInput):
    id = graphene.UUID(required=True)
    is_superuser = graphene.Boolean()
    is_active = graphene.Boolean()


class UpdateAdmin(graphene.Mutation):
    class Arguments:
        input = UpdateAdminInput(required=True)

    admin = graphene.Field(AdminType)
    errors = graphene.List(ErrorType)

    @admin_required
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
            if field in ('first_name', 'last_name', 'phone_number') and value is not None:
                setattr(user, field, value)

        user.save()

        return CreateAdmin(admin=user.admin, errors=[])


class DeleteAdmin(AdminDjangoModelDeleteMutation):
    class Meta:
        model_type = AdminType


class HandleLitigation(AdminDjangoModelMutation):
    class Meta:
        model_type = LitigationType
        for_update = True
        only_fields = ('decision', 'reason')
        custom_input_fields = {"decision": graphene.String(required=True), "reason": graphene.String(required=True)}

    @classmethod
    @transaction.atomic
    def pre_save(cls, info, old_obj, form, input):
        if form.instance.handled:
            return cls(errors=[ErrorType(field="id", messages=[_("Litigation already handled.")])])

        litigation: Litigation = form.instance
        service_purchase: ServicePurchase = litigation.service_purchase

        if litigation.approved:
            approve_service_purchase(service_purchase)
            service_purchase.set_as_approved()

        if litigation.canceled:
            cancel_service_purchase(service_purchase)
            service_purchase.set_as_canceled()

        service_purchase.save()

        litigation.set_as_handled()
        litigation.save()
        litigation.refresh_from_db()

        ServicePurchaseSubscription.broadcast(group=ServicePurchaseSubscription.name.format(str(service_purchase.id)))

        on_litigation_handled_task.delay(str(litigation.id))

        return cls(litigation=litigation, errors=[])


class CreateRefundWay(AdminDjangoModelMutation):
    class Meta:
        model_type = RefundWayType


class UpdateRefundWay(AdminDjangoModelMutation):
    class Meta:
        model_type = RefundWayType
        for_update = True


class DeleteRefundWay(AdminDjangoModelDeleteMutation):
    class Meta:
        model_type = RefundWayType


class ProcessRefund(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    result = graphene.String()
    error = graphene.String()

    @admin_required
    @transaction.atomic
    def mutate(self, info, id):
        refund = Refund.objects.get(pk=id)

        token = get_auth_token()
        if token is None:
            return ProcessRefund(error=_('Authentication error. Please check CINETPAY password parameter.'))

        balance = get_available_balance(token)
        if token is None:
            return ProcessRefund(error=_('Internal error. Please try again later.'))

        if balance < refund.amount:
            return ProcessRefund(error=_('Insufficient balance to process the refund.'))

        if not add_contact(token, refund):
            return ProcessRefund(error=_('Internal error. Please try again later.'))

        payment = Payment(amount=refund.amount, account=refund.account, type=Payment.TYPE_OUTGOING)
        payment.save()

        succeed, message = transfer_money(token, refund, payment)
        if not succeed:
            return ProcessRefund(error=message)

        refund.payment = payment
        refund.set_as_in_progress()
        refund.save()

        return ProcessRefund(
            result=_('Refund has been initiated at CINETPAY side. Please wait for the their confirmation.'))


class UpdateParameter(AdminDjangoModelMutation):
    class Meta:
        model_type = ParameterType
        for_update = True
        only_fields = ("value",)


class UpdateAccount(AdminDjangoModelMutation):
    class Meta:
        model_type = UserType
        for_update = True
        only_fields = ('is_active',)


class RefuseRefund(AdminDjangoModelMutation):
    class Meta:
        model_type = RefundType
        for_update = True
        only_fields = ('refused_reason',)
        custom_input_fields = {"refused_reason": graphene.String(required=True)}

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        if form.instance.cannot_be_refused:
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        refund: Refund = form.instance
        refund.set_as_refused()


class SortedServiceCategoryInputType(graphene.InputObjectType):
    id = graphene.UUID(required=True)
    index = graphene.Int(required=True)


class SortServiceCategories(graphene.Mutation):
    class Arguments:
        sorted = graphene.List(SortedServiceCategoryInputType, required=True)

    is_sorted = graphene.Boolean()

    @admin_required
    def mutate(self, info, sorted):
        for sorted_service_category in sorted:
            category = ServiceCategory.objects.get(pk=sorted_service_category.id)
            category.index = sorted_service_category.index
            category.save()

        return SortServiceCategories(is_sorted=True)


class AdminMutations(graphene.ObjectType):
    login = LoginAdmin.Field()
    update_admin_profile = UpdateAdminProfile.Field()
    change_admin_password = ChangeAdminPassword.Field()

    create_admin = CreateAdmin.Field()
    update_admin = UpdateAdmin.Field()
    delete_admin = DeleteAdmin.Field()

    create_service_category = CreateServiceCategory.Field()
    update_service_category = UpdateServiceCategory.Field()
    delete_service_category = DeleteServiceCategory.Field()

    accept_service = AcceptService.Field()
    reject_service = RejectService.Field()
    delete_service = DeleteService.Field()

    handle_litigation = HandleLitigation.Field()

    process_refund = ProcessRefund.Field()
    refuse_refund = RefuseRefund.Field()

    create_refund_way = CreateRefundWay.Field()
    update_refund_way = UpdateRefundWay.Field()
    delete_refund_way = DeleteRefundWay.Field()

    update_parameter = UpdateParameter.Field()

    update_account = UpdateAccount.Field()

    publish_un_publish_service = PublishUnPublishService.Field()

    sort_service_categories = SortServiceCategories.Field()
