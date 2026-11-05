# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models


class ActiveManager(models.Manager):
    """Manager di default: restituisce solo gli oggetti attivi."""

    def get_queryset(self):
        return super().get_queryset().filter(suppressed=False)


class SuppressedManager(models.Manager):
    """Restituisce solo gli oggetti soppressi."""

    def get_queryset(self):
        return super().get_queryset().filter(suppressed=True)


class SuppressibleModel(models.Model):
    suppressed = models.BooleanField(default=False, db_index=True, verbose_name='soppresso')

    objects = ActiveManager()
    all_objects = models.Manager()
    suppressed_objects = SuppressedManager()

    class Meta:
        abstract = True

    def validate_unique(self, exclude=None):
        """
        Django verifica l'unicità con il default manager (objects), che non vede i soppressi, mentre il vincolo
        del database vale per tutti i record. Ripetiamo quindi il controllo dei campi unique su all_objects.
        """
        super().validate_unique(exclude=exclude)

        errors = {}
        for field in self._meta.fields:
            if not field.unique or (exclude and field.name in exclude):
                continue
            value = getattr(self, field.attname)
            if value is None:
                continue
            qs = type(self).all_objects.filter(**{field.attname: value})
            if not self._state.adding:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                errors[field.name] = [self.unique_error_message(type(self), (field.name,))]

        if errors:
            raise ValidationError(errors)


class Regione(SuppressibleModel):
    codice_regione = models.IntegerField(primary_key=True, verbose_name="codice Istat")
    name = models.CharField(max_length=300, db_index=True, verbose_name='nome')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'regione'
        verbose_name_plural = 'regioni'


class CittaMetropolitana(SuppressibleModel):
    codice_cittametropolitana = models.IntegerField(primary_key=True, verbose_name="codice Istat")
    name = models.CharField(max_length=300, db_index=True, verbose_name="nome")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'città metropolitana'
        verbose_name_plural = 'città metropolitane'


class Provincia(SuppressibleModel):
    codice_provincia = models.IntegerField(primary_key=True, verbose_name="codice Istat")
    name = models.CharField(max_length=300, db_index=True, verbose_name="Nome")
    codice_targa = models.CharField(max_length=2, db_index=True)
    regione = models.ForeignKey(Regione, db_index=True, on_delete=models.PROTECT)

    def __str__(self):
        return '%s - %s' % (self.name, self.regione.name)

    class Meta:
        ordering = ['name']
        verbose_name = 'provincia'
        verbose_name_plural = 'province'


class Comune(SuppressibleModel):
    codice_istat = models.IntegerField(db_index=True, unique=True, verbose_name="codice Istat")
    codice_catastale = models.CharField(blank=True, null=True, max_length=50, db_index=True)
    name = models.CharField(max_length=300, db_index=True, verbose_name="nome")
    provincia = models.ForeignKey(Provincia, db_index=True, on_delete=models.PROTECT)
    citta_metropolitana = models.ForeignKey(CittaMetropolitana, null=True, blank=True, db_index=True, on_delete=models.PROTECT)
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
