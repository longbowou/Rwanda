from celery import shared_task

from rwanda.account.mails import send_verification_mail, on_service_purchase_initiated, \
    on_service_purchase_accepted_or_refused, on_service_purchase_delivered, on_service_purchase_approved, \
    on_service_purchase_canceled, on_service_purchase_update_request_initiated, \
    on_service_purchase_update_request_accepted_or_refused, on_service_purchase_update_request_delivered, \
    on_litigation_opened, on_litigation_handled
from rwanda.purchase.models import ServicePurchase, ServicePurchaseUpdateRequest, Litigation
from rwanda.user.models import User


@shared_task(bind=True)
def send_verification_mail_task(self, user_uuid):
    send_verification_mail(User.objects.get(pk=user_uuid))
    return True


@shared_task(bind=True)
def on_service_purchase_initiated_task(self, service_purchase_uuid):
    on_service_purchase_initiated(ServicePurchase.objects.get(pk=service_purchase_uuid))
    return True


@shared_task(bind=True)
def on_service_purchase_accepted_or_refused_task(self, service_purchase_uuid):
    on_service_purchase_accepted_or_refused(ServicePurchase.objects.get(pk=service_purchase_uuid))
    return True


@shared_task(bind=True)
def on_service_purchase_delivered_task(self, service_purchase_uuid):
    on_service_purchase_delivered(ServicePurchase.objects.get(pk=service_purchase_uuid))
    return True


@shared_task(bind=True)
def on_service_purchase_approved_task(self, service_purchase_uuid):
    on_service_purchase_approved(ServicePurchase.objects.get(pk=service_purchase_uuid))
    return True


@shared_task(bind=True)
def on_service_purchase_canceled_task(self, service_purchase_uuid):
    on_service_purchase_canceled(ServicePurchase.objects.get(pk=service_purchase_uuid))
    return True


@shared_task(bind=True)
def on_service_purchase_update_request_initiated_task(self, update_request_uuid):
    on_service_purchase_update_request_initiated(ServicePurchaseUpdateRequest.objects.get(pk=update_request_uuid))
    return True


@shared_task(bind=True)
def on_service_purchase_update_request_accepted_or_refused_task(self, update_request_uuid):
    on_service_purchase_update_request_accepted_or_refused(
        ServicePurchaseUpdateRequest.objects.get(pk=update_request_uuid))
    return True


@shared_task(bind=True)
def on_service_purchase_update_request_delivered_task(self, update_request_uuid):
    on_service_purchase_update_request_delivered(ServicePurchaseUpdateRequest.objects.get(pk=update_request_uuid))
    return True


@shared_task(bind=True)
def on_litigation_opened_task(self, litigation_uuid):
    on_litigation_opened(Litigation.objects.get(pk=litigation_uuid))
    return True


@shared_task(bind=True)
def on_litigation_handled_task(self, litigation_uuid):
    on_litigation_handled(Litigation.objects.get(pk=litigation_uuid))
    return True
