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
