from rwanda.administration.models import Parameter


def param_base_price():
    return Parameter.objects.filter(label=Parameter.BASE_PRICE).first().value


def param_currency():
    return Parameter.objects.filter(label=Parameter.CURRENCY).first().value


def param_commission():
    return Parameter.objects.filter(label=Parameter.COMMISSION).first().value


def param_home_max_page_size():
    return int(Parameter.objects.filter(label=Parameter.HOME_PAGE_MAX_SIZE).first().value)


def param_cinetpay_password():
    return Parameter.objects.filter(label=Parameter.CINETPAY_PASSWORD).first().value
