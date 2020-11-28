import json

import requests
from django.conf import settings
from django.urls import reverse

from rwanda.account.models import Refund
from rwanda.administration.utils import param_cinetpay_password
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


def get_auth_token():
    data = {
        "password": param_cinetpay_password(),
        "apikey": settings.CINETPAY_API_KEY,
    }

    result = requests.post(settings.CINETPAY_AUTH_URL, data).json()
    if "code" in result and result['code'] == 0:
        return result['data']['token']

    return None


def get_available_balance(token):
    params = {
        "token": token,
    }

    result = requests.get(settings.CINETPAY_CHECK_BALANCE_URL, params).json()

    if 'code' in result and result['code'] == 0:
        return int(result['data']['available'])

    return None


def add_contact(token, refund: Refund):
    params = {
        "token": token,
    }

    data = {
        'data': json.dumps(
            [
                {
                    "prefix": refund.refund_way.country_code,
                    "phone": refund.phone_number,
                    "name": refund.account.user.first_name,
                    "surname": refund.account.user.last_name,
                    "email": refund.account.user.email,
                }
            ]
        )
    }

    result = requests.post(settings.CINETPAY_ADD_CONTACT_URL, data, params=params).json()

    if 'code' in result and result['code'] == 0:
        return True

    return False


def transfer_money(token, refund: Refund, payment: Payment):
    params = {
        "token": token,
    }

    data = {
        'data': json.dumps(
            [
                {
                    "prefix": refund.refund_way.country_code,
                    "phone": refund.phone_number,
                    "amount": refund.amount,
                    # "notify_url": "https://backend.mdtaf.com/payments/confirmation",
                    "notify_url": settings.BASE_URL + reverse('payments-confirmation'),
                    "client_transaction_id": str(payment.id),
                }
            ]
        )
    }

    result = requests.post(settings.CINETPAY_TRANSFER_MONEY_URL, data, params=params).json()

    if 'code' in result and result['code'] == 0:
        return True, None

    if 'data' in result and len(result['data']):
        return False, result['data'][0]['message'] + ' ' + result['data'][0]['description']

    return False, result['message'] + ' ' + result['description']
