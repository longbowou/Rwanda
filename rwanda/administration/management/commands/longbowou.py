from django.core.management.base import BaseCommand

from rwanda.users.models import User


class Command(BaseCommand):
    help = 'Longbowou'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)

    def handle(self, *args, **options):
        if User.objects.filter(username=options['username']).exists():
            return self.stdout.write(self.style.ERROR('Longbowou already exists !'))

        user = User(username=options['username'], is_superuser=True, longbowou=True)
        user.set_password(options['password'])
        user.save()

        self.stdout.write(self.style.SUCCESS('Longbowou created !'))
