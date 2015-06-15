# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CittaMetropolitana',
            fields=[
                ('codice_cittametropolitana', models.IntegerField(primary_key=True, serialize=False, verbose_name='codice Istat')),
                ('name', models.CharField(db_index=True, verbose_name='nome', max_length=300)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'città metropolitane',
                'verbose_name': 'città metropolitana',
            },
        ),
        migrations.CreateModel(
            name='Comune',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('codice_istat', models.IntegerField(db_index=True, verbose_name='codice Istat', unique=True)),
                ('codice_catastale', models.CharField(blank=True, db_index=True, null=True, max_length=50)),
                ('name', models.CharField(db_index=True, verbose_name='nome', max_length=300)),
                ('is_capoluogo', models.BooleanField(default=False, verbose_name='capoluogo')),
                ('altitudine', models.IntegerField(null=True, blank=True)),
                ('superficie', models.FloatField(null=True, verbose_name='superficie (kmq)', blank=True)),
                ('popolazione', models.IntegerField(null=True, blank=True)),
                ('citta_metropolitana', models.ForeignKey(to='comuni_italiani.CittaMetropolitana', blank=True, null=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'comuni',
                'verbose_name': 'comune',
            },
        ),
        migrations.CreateModel(
            name='Provincia',
            fields=[
                ('codice_provincia', models.IntegerField(primary_key=True, serialize=False, verbose_name='codice Istat')),
                ('name', models.CharField(db_index=True, verbose_name='Nome', max_length=300)),
                ('codice_targa', models.CharField(db_index=True, max_length=2)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'province',
                'verbose_name': 'provincia',
            },
        ),
        migrations.CreateModel(
            name='Regione',
            fields=[
                ('codice_regione', models.IntegerField(primary_key=True, serialize=False, verbose_name='codice Istat')),
                ('name', models.CharField(db_index=True, verbose_name='nome', max_length=300)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'regioni',
                'verbose_name': 'regione',
            },
        ),
        migrations.AddField(
            model_name='provincia',
            name='regione',
            field=models.ForeignKey(to='comuni_italiani.Regione'),
        ),
        migrations.AddField(
            model_name='comune',
            name='provincia',
            field=models.ForeignKey(to='comuni_italiani.Provincia'),
        ),
    ]
