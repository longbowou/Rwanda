from django.conf import settings
from mailjet_rest import Client

from rwanda.administration.models import Parameter


def param_base_price():
    return int(Parameter.objects.filter(label=Parameter.BASE_PRICE).first().value)


def param_reminder_service_purchase_deadline_lte():
    return int(Parameter.objects.filter(label=Parameter.REMINDER_SERVICE_PURCHASE_DEADLINE_LTE).first().value)


def param_deposit_fee():
    return float(Parameter.objects.filter(label=Parameter.DEPOSIT_FEE).first().value)


def param_currency():
    return Parameter.objects.filter(label=Parameter.CURRENCY).first().value


def param_commission():
    return float(Parameter.objects.filter(label=Parameter.COMMISSION).first().value)


def param_home_max_page_size():
    return int(Parameter.objects.filter(label=Parameter.HOME_PAGE_MAX_SIZE).first().value)


def param_cinetpay_password():
    return Parameter.objects.filter(label=Parameter.CINETPAY_PASSWORD).first().value


def send_mail(to_email, subject, html):
    mailjet = Client(auth=(settings.MAILJET_KEY, settings.MAILJET_SECRET), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": settings.DEFAULT_FROM_EMAIL,
                    "Name": settings.BRAND
                },
                "To": [
                    {
                        "Email": to_email,
                    }
                ],
                "Subject": subject,
                "HTMLPart": html,
            }
        ]
    }
    result = mailjet.send.create(data=data)
    return result.status_code == 200
