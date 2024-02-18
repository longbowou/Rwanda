from django.core.management.base import BaseCommand

from rwanda.users.models import User


class Command(BaseCommand):
    help = 'Longbowou'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)

    def handle(self, *args, **options):
        created = False
        user = User.objects.filter(username=options['username']).first()
        if not user:
            created = True
            user = User(username=options['username'], is_superuser=True)
        user.email("superuser@rwanda.app")
        user.set_password(options['password'])
        user.longbowou = True
        user.save()

        self.stdout.write(self.style.SUCCESS(f'Longbowou {"created" if created else "updated"} !'))
