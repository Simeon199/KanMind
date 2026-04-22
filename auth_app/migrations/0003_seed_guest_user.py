"""
Data migration that seeds the guest demo account on first setup.

Runs automatically as part of `python manage.py migrate` so no manual
management command is required after cloning the project.

Forward : creates the guest user and their auth token (idempotent).
Backward: removes the guest user (and cascades the token deletion).
"""

from django.db import migrations
from django.contrib.auth.hashers import make_password

GUEST_EMAIL = 'kevin@kovacsi.de'
GUEST_PASSWORD = 'asdasdasd'
GUEST_USERNAME = 'Kevin Guest'


def seed_guest_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Token = apps.get_model('authtoken', 'Token')

    user, created = User.objects.get_or_create(
        email=GUEST_EMAIL,
        defaults={
            'username': GUEST_USERNAME,
            'password': make_password(GUEST_PASSWORD),
        },
    )
    Token.objects.get_or_create(user=user)


def remove_guest_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(email=GUEST_EMAIL).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0002_rename_first_name_userprofile_fullname_and_more'),
        ('authtoken', '0003_tokenproxy'),
    ]

    operations = [
        migrations.RunPython(seed_guest_user, reverse_code=remove_guest_user),
    ]
