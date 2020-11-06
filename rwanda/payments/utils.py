import requests
from django.conf import settings

from rwanda.payments.models import Payment


def get_signature(payment: Payment):
    data = {
        "cpm_amount": payment.amount,
        "cpm_currency": settings.CINETPAY_CURRENCY,
        "cpm_site_id": settings.CINETPAY_SITE_ID,
        "cpm_trans_id": str(payment.id),
        "cpm_trans_date": payment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "cpm_payment_config": "SINGLE",
        "cpm_page_action": "PAYMENT",
        "cpm_version": "V1",
        "cpm_language": "fr",
        "apikey": settings.CINETPAY_API_KEY,
    }
    return requests.post(settings.CINETPAY_SIGNATURE_URL, data).json()


def check_status(payment: Payment):
    data = {
        "cpm_site_id": settings.CINETPAY_SITE_ID,
        "cpm_trans_id": str(payment.id),
        "apikey": settings.CINETPAY_API_KEY,
    }
    return requests.post(settings.CINETPAY_CHECK_STATUS_URL, data).json()
