from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from rwanda.administration.utils import param_currency, param_base_price, send_mail
from rwanda.purchases.models import ServicePurchase, ServicePurchaseUpdateRequest, Litigation
from rwanda.services.models import Service
from rwanda.users.models import User


def process_mail(subject, template, data, email):
    data['base_url'] = settings.BASE_URL
    html_content = render_to_string(template, data)
    return send_mail(email, str(subject), html_content)


def send_verification_mail(user: User):
    return process_mail(_('Activate your account'),
                        "mails/very_account.html",
                        {
                            "activate_url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/activate/' + str(user.id),
                            "user": user
                        },
                        user.email)


def on_service_accepted_or_rejected(service: Service):
    data = {"currency": param_currency(),
            "base_price": param_base_price(),
            "service": service,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/services/' + str(service.id)}

    return process_mail(_("Service accepted") if service.accepted else _("Service rejected"),
                        "mails/services/accepted.html" if service.accepted else "mails/services/rejected.html",
                        data,
                        service.account.user.email)


def on_service_purchase_initiated(service_purchase: ServicePurchase):
    data = {"currency": param_currency(),
            "purchase": service_purchase,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/purchases/' + str(service_purchase.id)}

    process_mail(_("Purchase"),
                 "mails/services/purchases/initiated.html",
                 data,
                 service_purchase.buyer.user.email)

    data["url"] = settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(service_purchase.id)
    return process_mail(_("New order"),
                        "mails/services/orders/initiated.html",
                        data,
                        service_purchase.seller.user.email)


def on_service_purchase_accepted_or_refused(service_purchase: ServicePurchase):
    data = {"currency": param_currency(),
            "purchase": service_purchase,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/purchases/' + str(service_purchase.id)}

    return process_mail(_("Purchase accepted") if service_purchase.accepted else _("Purchase refused"),
                        "mails/services/purchases/accepted_or_refused.html",
                        data,
                        service_purchase.buyer.user.email)


def on_service_purchase_delivered(service_purchase: ServicePurchase):
    data = {"currency": param_currency(),
            "purchase": service_purchase,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/purchases/' + str(service_purchase.id)}

    return process_mail(_("Purchase delivered"),
                        "mails/services/purchases/delivered.html",
                        data,
                        service_purchase.buyer.user.email)


def on_service_purchase_approved(service_purchase: ServicePurchase):
    data = {"currency": param_currency(),
            "purchase": service_purchase,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(service_purchase.id)}

    return process_mail(_("Order approved"),
                        "mails/services/orders/approved.html",
                        data,
                        service_purchase.seller.user.email)


def on_service_purchase_canceled(service_purchase: ServicePurchase):
    data = {"currency": param_currency(),
            "purchase": service_purchase,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(service_purchase.id)}

    return process_mail(_("Order canceled"),
                        "mails/services/purchases/canceled.html",
                        data,
                        service_purchase.seller.user.email)


def send_service_purchase_deadline_reminder(service_purchase: ServicePurchase):
    data = {"currency": param_currency(),
            "purchase": service_purchase,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(service_purchase.id)}

    return process_mail(_("Deadline reminder"),
                        "mails/services/purchases/deadline_reminder.html",
                        data,
                        service_purchase.seller.user.email)


def on_service_purchase_update_request_initiated(service_purchase_update_request: ServicePurchaseUpdateRequest):
    data = {"currency": param_currency(),
            "update_request": service_purchase_update_request,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(
                service_purchase_update_request.service_purchase.id)}

    return process_mail(_("Update requested"),
                        "mails/services/update_requests/initiated.html",
                        data,
                        service_purchase_update_request.service_purchase.seller.user.email)


def on_service_purchase_update_request_accepted_or_refused(
        service_purchase_update_request: ServicePurchaseUpdateRequest):
    data = {"currency": param_currency(),
            "update_request": service_purchase_update_request,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(
                service_purchase_update_request.service_purchase.id)}

    return process_mail(
        _("Update request accepted") if service_purchase_update_request.accepted else _("Update request refused"),
        "mails/services/update_requests/accepted_or_refused.html",
        data,
        service_purchase_update_request.service_purchase.buyer.user.email)


def on_service_purchase_update_request_delivered(service_purchase_update_request: ServicePurchaseUpdateRequest):
    data = {"currency": param_currency(),
            "update_request": service_purchase_update_request,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(
                service_purchase_update_request.service_purchase.id)}

    return process_mail(_("Update delivered"),
                        "mails/services/update_requests/delivered.html",
                        data,
                        service_purchase_update_request.service_purchase.buyer.user.email)


def on_litigation_opened(litigation: Litigation):
    data = {"currency": param_currency(),
            "litigation": litigation,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/purchases/' + str(litigation.service_purchase.id)}

    process_mail(_("Litigation opened"),
                 "mails/services/disputes/opened.html",
                 data,
                 litigation.service_purchase.buyer.user.email)

    data["url"] = settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(litigation.service_purchase.id)
    return process_mail(_("Litigation opened"),
                        "mails/services/disputes/opened.html",
                        data,
                        litigation.service_purchase.seller.user.email)


def on_litigation_handled(litigation: Litigation):
    data = {"currency": param_currency(),
            "litigation": litigation,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/purchases/' + str(litigation.service_purchase.id)}

    process_mail(litigation.decision_display,
                 "mails/services/disputes/handled.html",
                 data,
                 litigation.service_purchase.buyer.user.email)

    data["url"] = settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(litigation.service_purchase.id)
    return process_mail(litigation.decision_display,
                        "mails/services/disputes/handled.html",
                        data,
                        litigation.service_purchase.seller.user.email)
