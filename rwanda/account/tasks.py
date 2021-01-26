from celery import shared_task

from rwanda.account.mails import send_verification_mail, on_service_purchase_initiated, \
    on_service_purchase_accepted_or_refused, on_service_purchase_delivered, on_service_purchase_approved, \
    on_service_purchase_canceled, on_service_purchase_update_request_initiated, \
    on_service_purchase_update_request_accepted_or_refused, on_service_purchase_update_request_delivered, \
    on_litigation_opened, on_litigation_handled, on_service_accepted_or_rejected
from rwanda.purchase.models import ServicePurchase, ServicePurchaseUpdateRequest, Litigation
from rwanda.service.models import Service
from rwanda.user.models import User


@shared_task
def send_verification_mail_task(user_uuid):
    send_verification_mail(User.objects.get(pk=user_uuid))
    return True


@shared_task
def on_service_accepted_or_rejected_task(service_uuid):
    on_service_accepted_or_rejected(Service.objects.get(pk=service_uuid))
    return True


@shared_task
def on_service_purchase_initiated_task(service_purchase_uuid):
    on_service_purchase_initiated(ServicePurchase.objects.get(pk=service_purchase_uuid))
    return True


@shared_task
def on_service_purchase_accepted_or_refused_task(service_purchase_uuid):
    on_service_purchase_accepted_or_refused(ServicePurchase.objects.get(pk=service_purchase_uuid))
    return True


@shared_task
def on_service_purchase_delivered_task(service_purchase_uuid):
    on_service_purchase_delivered(ServicePurchase.objects.get(pk=service_purchase_uuid))
    return True


@shared_task
def on_service_purchase_approved_task(service_purchase_uuid):
    on_service_purchase_approved(ServicePurchase.objects.get(pk=service_purchase_uuid))
    return True


@shared_task
def on_service_purchase_canceled_task(service_purchase_uuid):
    on_service_purchase_canceled(ServicePurchase.objects.get(pk=service_purchase_uuid))
    return True


@shared_task
def on_service_purchase_update_request_initiated_task(update_request_uuid):
    on_service_purchase_update_request_initiated(ServicePurchaseUpdateRequest.objects.get(pk=update_request_uuid))
    return True


@shared_task
def on_service_purchase_update_request_accepted_or_refused_task(update_request_uuid):
    on_service_purchase_update_request_accepted_or_refused(
        ServicePurchaseUpdateRequest.objects.get(pk=update_request_uuid))
    return True


@shared_task
def on_service_purchase_update_request_delivered_task(update_request_uuid):
    on_service_purchase_update_request_delivered(ServicePurchaseUpdateRequest.objects.get(pk=update_request_uuid))
    return True


@shared_task
def on_litigation_opened_task(litigation_uuid):
    on_litigation_opened(Litigation.objects.get(pk=litigation_uuid))
    return True


@shared_task
def on_litigation_handled_task(litigation_uuid):
    on_litigation_handled(Litigation.objects.get(pk=litigation_uuid))
    return True
