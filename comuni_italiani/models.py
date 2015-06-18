# -*- coding: utf-8 -*-
from django.db import models

class Regione(models.Model):
    codice_regione = models.IntegerField(primary_key=True, verbose_name="codice Istat")
    name = models.CharField(max_length=300, db_index=True, verbose_name='nome')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'regione'
        verbose_name_plural = 'regioni'


class CittaMetropolitana(models.Model):
    codice_cittametropolitana = models.IntegerField(primary_key=True, verbose_name="codice Istat")
    name = models.CharField(max_length=300, db_index=True, verbose_name="nome")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'città metropolitana'
        verbose_name_plural = 'città metropolitane'


class Provincia(models.Model):
    codice_provincia = models.IntegerField(primary_key=True, verbose_name="codice Istat")
    name = models.CharField(max_length=300, db_index=True, verbose_name="Nome")
    codice_targa = models.CharField(max_length=2, db_index=True)
    regione = models.ForeignKey(Regione, db_index=True)

    def __str__(self):
        return '%s - %s' % (self.name, self.regione.name)

    class Meta:
        ordering = ['name']
        verbose_name = 'provincia'
        verbose_name_plural = 'province'


class Comune(models.Model):
    codice_istat = models.IntegerField(db_index=True, unique=True, verbose_name="codice Istat")
    codice_catastale = models.CharField(blank=True, null=True, max_length=50, db_index=True)
    name = models.CharField(max_length=300, db_index=True, verbose_name="nome")
    provincia = models.ForeignKey(Provincia, db_index=True)
    citta_metropolitana = models.ForeignKey(CittaMetropolitana, null=True, blank=True, db_index=True)
    is_capoluogo = models.BooleanField(default=False, verbose_name="capoluogo")
    altitudine = models.IntegerField(blank=True, null=True)
    superficie = models.FloatField(blank=True, null=True, verbose_name="superficie (kmq)")
    popolazione = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'comune'
        verbose_name_plural = 'comuni'

    def __str__(self):
        return '%s - %s' % (self.name, self.provincia.name)
