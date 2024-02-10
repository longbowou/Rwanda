from django.core.management.base import BaseCommand

from rwanda.account.models import RefundWay, Deposit
from rwanda.accounting.models import Fund, Operation
from rwanda.administration.models import Parameter
from rwanda.administration.utils import param_deposit_fee
from rwanda.graphql.purchase.operations import credit_account
from rwanda.payments.models import Payment
from rwanda.services.models import ServiceCategory
from rwanda.users.models import User, Account


class Command(BaseCommand):
    help = 'Seed data'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for item in [
            {"label": Parameter.BASE_PRICE, "value": 2000},
            {"label": Parameter.DEPOSIT_FEE, "value": 0.04},
            {"label": Parameter.COMMISSION, "value": 0.04},
            {"label": Parameter.HOME_PAGE_MAX_SIZE, "value": 30},
            {"label": Parameter.REMINDER_SERVICE_PURCHASE_DEADLINE_LTE, "value": 1},
            {"label": Parameter.CURRENCY, "value": "XOF"},
            {"label": Parameter.CINETPAY_PASSWORD, "value": 'M@dchanger@2020'},
        ]:
            if not Parameter.objects.filter(label=item['label']).exists():
                Parameter(**item).save()

        for item in [
            {"name": "ORANGE MONEY CÔTE D’IVOIRE", "country_code": 225},
            {"name": "ORANGE MONEY SÉNÉGAL", "country_code": 221},
            {"name": "ORANGE MONEY CAMEROUN", "country_code": 237},
            {"name": "ORANGE MONEY BURKINA", "country_code": 226},
            {"name": "FLOOZ TOGO", "country_code": 228},
        ]:
            if not RefundWay.objects.filter(name=item['name']).exists():
                RefundWay(**item).save()

        for item in [Fund.MAIN, Fund.COMMISSIONS, Fund.ACCOUNTS]:
            if not Fund.objects.filter(label=item).exists():
                Fund(label=item).save()

        for item in ["Technology", "Art", "Business"]:
            if not ServiceCategory.objects.filter(label=item).exists():
                ServiceCategory(label=item).save()

        for item in [
            {
                "username": 'seller',
                "email": 'seller@rwanda.app',
                "first_name": 'Seller',
                "last_name": 'Rwanda',
                "password": 'sellerpassword',
            },
            {
                "username": 'john',
                "email": 'john@rwanda.app',
                "first_name": 'John',
                "last_name": 'Doe',
                "password": 'johnpassword',
            },
            {
                "username": 'Jane',
                "email": 'jane@rwanda.app',
                "first_name": 'Jane',
                "last_name": 'Doe',
                "password": 'janepassword',
            }
        ]:
            if not User.objects.filter(username=item['username']).exists():
                user = User(
                    username=item['username'],
                    email=item['email'],
                    first_name=item['first_name'],
                    last_name=item['last_name'],
                    email_verified=True,
                )
                user.set_password(item['password'])
                user.save()

                account = Account(
                    user=user
                )
                account.save()

                amount = 200000
                payment = Payment(amount=amount,
                                  fee=param_deposit_fee() * amount,
                                  account=account)
                payment.set_as_confirmed()
                payment.save()

                deposit = Deposit(account=payment.account, amount=payment.amount, payment=payment)
                deposit.save()

                credit_account(payment.account, payment.amount, Operation.DESC_CREDIT_FOR_DEPOSIT)

        self.stdout.write(self.style.SUCCESS('Seed complete'))
