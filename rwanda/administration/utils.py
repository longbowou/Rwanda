from asgiref.sync import sync_to_async

from rwanda.administration.models import Parameter


def param_base_price():
    return int(Parameter.objects.filter(label=Parameter.BASE_PRICE).first().value)


def param_deposit_fee():
    return float(Parameter.objects.filter(label=Parameter.DEPOSIT_FEE).first().value)


def param_currency(from_async=False):
    queryset = Parameter.objects.filter(label=Parameter.CURRENCY).first()

    if from_async:
        @sync_to_async
        def get_param():
            return queryset.value

        return get_param()

    return queryset.value


def param_commission():
    return float(Parameter.objects.filter(label=Parameter.COMMISSION).first().value)


def param_home_max_page_size():
    return int(Parameter.objects.filter(label=Parameter.HOME_PAGE_MAX_SIZE).first().value)


def param_cinetpay_password():
    return Parameter.objects.filter(label=Parameter.CINETPAY_PASSWORD).first().value
