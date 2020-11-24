from django.core.management.base import BaseCommand

from rwanda.account.models import RefundWay
from rwanda.accounting.models import Fund
from rwanda.administration.models import Parameter
from rwanda.service.models import ServiceCategory


class Command(BaseCommand):
    help = 'Seed data'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for item in [
            {"label": Parameter.BASE_PRICE, "value": 1000},
            {"label": Parameter.CURRENCY, "value": "XOF"},
            {"label": Parameter.COMMISSION, "value": 500},
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

        self.stdout.write(self.style.SUCCESS('Seed complete'))
