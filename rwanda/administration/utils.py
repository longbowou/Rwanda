from rwanda.administration.models import Parameter


def param_base_price():
    return Parameter.objects.filter(label=Parameter.BASE_PRICE).first().value


def param_currency():
    return Parameter.objects.filter(label=Parameter.CURRENCY).first().value


def param_commission():
    return Parameter.objects.filter(label=Parameter.COMMISSION).first().value


def param_service_purchase_cancellation_delay():
    return Parameter.objects.filter(label=Parameter.SERVICE_PURCHASE_CANCELLATION_DELAY).first().value
