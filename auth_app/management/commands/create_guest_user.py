from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

GUEST_EMAIL = 'max@mustermann.de'
GUEST_PASSWORD = 'asdasdasd'
GUEST_USERNAME = 'Max Mustermann'


class Command(BaseCommand):
    help = 'Creates the guest demo user (max@mustermann.de) if it does not exist.'

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            email=GUEST_EMAIL,
            defaults={'username': GUEST_USERNAME},
        )
        if created:
            user.set_password(GUEST_PASSWORD)
            user.save()
            Token.objects.get_or_create(user=user)
            self.stdout.write(self.style.SUCCESS(
                f'Guest user created: {GUEST_EMAIL}'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'Guest user already exists: {GUEST_EMAIL}'
            ))
