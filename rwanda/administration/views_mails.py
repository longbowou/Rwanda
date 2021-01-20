from django.conf import settings
from django.views.generic import TemplateView

from rwanda.administration.utils import param_currency
from rwanda.purchase.models import ServicePurchase, ServicePurchaseUpdateRequest, Litigation
from rwanda.user.models import User


class VerifyAccountMailPreviewView(TemplateView):
    template_name = "mails/very_account.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        user = User.objects.get(email='blandedaniel@gmail.com')
        activate_url = settings.FRONTEND_ACCOUNT_BASE_URL + '/#/activate/' + str(user.id)

        data["activate_url"] = activate_url
        data["user"] = user

        # send_verification_mail(user)

        return data


class PurchaseInitiatedMailPreviewView(TemplateView):
    template_name = "mails/services/purchases/initiated.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data["currency"] = param_currency()
        data["purchase"] = ServicePurchase.objects.last()
        data["url"] = settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/purchases/' + str(data["purchase"].id)

        return data


class PurchaseAcceptedOrRejectedMailPreviewView(TemplateView):
    template_name = "mails/services/purchases/accepted_or_refused.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data["currency"] = param_currency()
        data["purchase"] = ServicePurchase.objects.last()
        data["url"] = settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/purchases/' + str(data["purchase"].id)

        return data


class OrderInitiatedMailPreviewView(TemplateView):
    template_name = "mails/services/orders/initiated.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data["currency"] = param_currency()
        data["purchase"] = ServicePurchase.objects.last()
        data["url"] = settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(data["purchase"].id)

        return data


class OrderCanceledMailPreviewView(TemplateView):
    template_name = "mails/services/orders/canceled.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data["currency"] = param_currency()
        data["purchase"] = ServicePurchase.objects.last()
        data["url"] = settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(data["purchase"].id)

        return data


class OrderApprovedMailPreviewView(TemplateView):
    template_name = "mails/services/orders/approved.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data["currency"] = param_currency()
        data["purchase"] = ServicePurchase.objects.last()
        data["url"] = settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(data["purchase"].id)

        return data


class UpdateInitiatedMailPreviewView(TemplateView):
    template_name = "mails/services/update_requests/initiated.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data["currency"] = param_currency()
        data["update"] = ServicePurchaseUpdateRequest.objects.first()
        data["url"] = settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(
            data["update"].service_purchase.id)

        return data


class LitigationInitiatedMailPreviewView(TemplateView):
    template_name = "mails/services/disputes/opened.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data["currency"] = param_currency()
        data["litigation"] = Litigation.objects.first()
        data["url"] = settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(
            data["litigation"].service_purchase.id)

        return data


class LitigationHandledMailPreviewView(TemplateView):
    template_name = "mails/services/disputes/handled.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data["currency"] = param_currency()
        data["litigation"] = Litigation.objects.first()
        data["url"] = settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(
            data["litigation"].service_purchase.id)

        return data
