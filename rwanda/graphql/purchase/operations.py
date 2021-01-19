from django.db import transaction
from django.db.models import F

from rwanda.accounting.models import Operation, Fund
from rwanda.purchase.models import ServicePurchase
from rwanda.user.models import Account


@transaction.atomic
def credit_account(account: Account, amount, desc):
    Operation(type=Operation.TYPE_CREDIT, account=account, amount=amount,
              description=desc,
              fund=Fund.objects.get(label=Fund.ACCOUNTS)).save()
    Fund.objects.filter(label=Fund.ACCOUNTS).update(balance=F('balance') + amount)
    Account.objects.filter(pk=account.pk).update(balance=F('balance') + amount)


@transaction.atomic
def debit_account(account, amount, desc):
    Operation(type=Operation.TYPE_DEBIT, account=account, amount=amount,
              description=desc,
              fund=Fund.objects.get(label=Fund.ACCOUNTS)).save()
    Fund.objects.filter(label=Fund.ACCOUNTS).update(balance=F('balance') - amount)
    Account.objects.filter(pk=account.pk).update(balance=F('balance') - amount)


@transaction.atomic
def credit_main(service_purchase, amount, desc):
    Operation(type=Operation.TYPE_CREDIT, service_purchase=service_purchase, amount=amount,
              description=desc,
              fund=Fund.objects.get(label=Fund.MAIN)).save()
    Fund.objects.filter(label=Fund.MAIN).update(balance=F('balance') + amount)


@transaction.atomic
def debit_main(service_purchase, amount, desc):
    Operation(type=Operation.TYPE_DEBIT, service_purchase=service_purchase, amount=amount,
              description=desc,
              fund=Fund.objects.get(label=Fund.MAIN)).save()
    Fund.objects.filter(label=Fund.MAIN).update(balance=F('balance') - amount)


@transaction.atomic
def credit_commission(service_purchase, amount, desc):
    Operation(type=Operation.TYPE_CREDIT, service_purchase=service_purchase, amount=amount,
              description=desc,
              fund=Fund.objects.get(label=Fund.COMMISSIONS)).save()
    Fund.objects.filter(label=Fund.COMMISSIONS).update(balance=F('balance') + amount)


@transaction.atomic
def debit_commission(service_purchase, amount, desc):
    Operation(type=Operation.TYPE_DEBIT, service_purchase=service_purchase, amount=amount,
              description=desc,
              fund=Fund.objects.get(label=Fund.COMMISSIONS)).save()
    Fund.objects.filter(label=Fund.COMMISSIONS).update(balance=F('balance') - amount)


@transaction.atomic
def init_service_purchase(service_purchase: ServicePurchase):
    debit_account(service_purchase.account, service_purchase.price, Operation.DESC_DEBIT_FOR_PURCHASE_INIT)

    credit_main(service_purchase, service_purchase.price_without_commission, Operation.DESC_CREDIT_FOR_PURCHASE_INIT)

    credit_commission(service_purchase, service_purchase.commission, Operation.DESC_CREDIT_FOR_PURCHASE_INIT)


@transaction.atomic
def approve_service_purchase(service_purchase: ServicePurchase):
    debit_main(service_purchase, service_purchase.price_without_commission, Operation.DESC_DEBIT_FOR_PURCHASE_APPROVED)

    credit_account(service_purchase.service.account, service_purchase.price_without_commission,
                   Operation.DESC_CREDIT_FOR_PURCHASE_APPROVED)


@transaction.atomic
def cancel_service_purchase(service_purchase: ServicePurchase):
    debit_main(service_purchase, service_purchase.price_without_commission, Operation.DESC_DEBIT_FOR_PURCHASE_CANCELED)

    debit_commission(service_purchase, service_purchase.commission, Operation.DESC_DEBIT_FOR_PURCHASE_CANCELED)

    credit_account(service_purchase.account, service_purchase.price, Operation.DESC_CREDIT_FOR_PURCHASE_CANCELED)
