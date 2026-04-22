"""
Data migration that repairs the guest user's auth token.

Migration 0003 created the token via the historical Token model returned by
`apps.get_model`, which lacks DRF's custom `save()` that auto-generates the
`key`. As a result the token row was persisted with an empty key, causing
401 responses for all authenticated requests after a guest login.

Forward : regenerates the key for any guest token with an empty key.
Backward: no-op (restoring an empty key would re-introduce the bug).
"""

import binascii
import os

from django.db import migrations


GUEST_EMAIL = 'kevin@kovacsi.de'


def fix_guest_token(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Token = apps.get_model('authtoken', 'Token')

    try:
        user = User.objects.get(email=GUEST_EMAIL)
    except User.DoesNotExist:
        return

    Token.objects.filter(user=user, key='').delete()
    Token.objects.get_or_create(
        user=user,
        defaults={'key': binascii.hexlify(os.urandom(20)).decode()},
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0003_seed_guest_user'),
        ('authtoken', '0003_tokenproxy'),
    ]

    operations = [
        migrations.RunPython(fix_guest_token, reverse_code=noop),
    ]
