# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from django.core.management import call_command

fixture = 'comuni_italiani'

def load_fixture(apps, schema_editor):
    call_command('loaddata', fixture, app_label='comuni_italiani')

class Migration(migrations.Migration):

    dependencies = [
        ('comuni_italiani', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixture),
    ]
