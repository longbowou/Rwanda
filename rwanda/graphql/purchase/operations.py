from django.db.models import F

from rwanda.accounting.models import Operation, Fund
from rwanda.user.models import Account


def credit_account(account: Account, amount, desc):
    Operation(type=Operation.TYPE_CREDIT, account=account, amount=amount,
              description=desc,
              fund=Fund.objects.get(label=Fund.ACCOUNTS)).save()
    Fund.objects.filter(label=Fund.ACCOUNTS).update(balance=F('balance') + amount)
    Account.objects.filter(pk=account.pk).update(balance=F('balance') + amount)


def debit_account(account, amount, desc):
    Operation(type=Operation.TYPE_DEBIT, account=account, amount=amount,
              description=desc,
              fund=Fund.objects.get(label=Fund.ACCOUNTS)).save()
    Fund.objects.filter(label=Fund.ACCOUNTS).update(balance=F('balance') - amount)
    Account.objects.filter(pk=account.pk).update(balance=F('balance') - amount)


def credit_main(service_purchase, amount, desc):
    Operation(type=Operation.TYPE_CREDIT, service_purchase=service_purchase, amount=amount,
              description=desc,
              fund=Fund.objects.get(label=Fund.MAIN)).save()
    Fund.objects.filter(label=Fund.MAIN).update(balance=F('balance') + amount)


def debit_main(service_purchase, amount, desc):
    Operation(type=Operation.TYPE_DEBIT, service_purchase=service_purchase, amount=amount,
              description=desc,
              fund=Fund.objects.get(label=Fund.MAIN)).save()
    Fund.objects.filter(label=Fund.MAIN).update(balance=F('balance') - amount)


def credit_commission(service_purchase, amount, desc):
    Operation(type=Operation.TYPE_CREDIT, service_purchase=service_purchase, amount=amount,
              description=desc,
              fund=Fund.objects.get(label=Fund.COMMISSIONS)).save()
    Fund.objects.filter(label=Fund.COMMISSIONS).update(balance=F('balance') + amount)


def debit_commission(service_purchase, amount, desc):
    Operation(type=Operation.TYPE_DEBIT, service_purchase=service_purchase, amount=amount,
              description=desc,
              fund=Fund.objects.get(label=Fund.COMMISSIONS)).save()
    Fund.objects.filter(label=Fund.COMMISSIONS).update(balance=F('balance') - amount)
