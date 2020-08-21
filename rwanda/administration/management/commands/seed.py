from django.core.management.base import BaseCommand

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
            {"label": Parameter.COMMISSION, "value": 200},
            {"label": Parameter.SERVICE_PURCHASE_CANCELLATION_DELAY, "value": 5},
        ]:
            if not Parameter.objects.filter(label=item['label']).exists():
                Parameter(**item).save()

        for item in [Fund.MAIN, Fund.COMMISSIONS, Fund.ACCOUNTS]:
            if not Fund.objects.filter(label=item).exists():
                Fund(label=item).save()

        for item in ["TECH", ]:
            if not ServiceCategory.objects.filter(label=item).exists():
                ServiceCategory(label=item).save()

        self.stdout.write(self.style.SUCCESS('Seed complete'))
