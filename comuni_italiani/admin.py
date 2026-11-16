# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import *


class SuppressibleAdminMixin(object):
    """
    Il default manager (objects) esclude gli oggetti soppressi: nell'admin vogliamo invece vederli tutti,
    filtrabili tramite il campo suppressed, e poterli selezionare nelle foreign key (es. la provincia di un comune).
    """

    def get_queryset(self, request):
        qs = self.model.all_objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if 'queryset' not in kwargs and hasattr(db_field.related_model, 'all_objects'):
            kwargs['queryset'] = db_field.related_model.all_objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ComuneAdmin(SuppressibleAdminMixin, admin.ModelAdmin):
    list_display = ('codice_istat', 'name', 'codice_catastale', 'get_provincia_name', 'citta_metropolitana', 'suppressed')
    search_fields = ('name', 'codice_istat')
    list_filter = ('suppressed', 'provincia')

    def get_provincia_name(self, obj):
        return obj.provincia.name
    get_provincia_name.short_description = 'Provincia'
    get_provincia_name.admin_order_field = 'provincia__name'

class ProvinciaAdmin(SuppressibleAdminMixin, admin.ModelAdmin):
    list_display = ('codice_provincia', 'name', 'codice_targa', 'get_regione_name', 'suppressed')
    search_fields = ('codice_provincia', 'name')
    list_filter = ('suppressed', 'regione')

    def get_regione_name(self, obj):
        return obj.regione.name
    get_regione_name.short_description = 'Regione'
    get_regione_name.admin_order_field = 'regione__name'

class RegioneAdmin(SuppressibleAdminMixin, admin.ModelAdmin):
    list_display = ('codice_regione', 'name', 'suppressed')
    search_fields = ('codice_regione', 'name')
    list_filter = ('suppressed',)

class CittaMetropolitanaAdmin(SuppressibleAdminMixin, admin.ModelAdmin):
    list_display = ('codice_cittametropolitana', 'name', 'suppressed')
    search_fields = ('codice_cittametropolitana', 'name')
    list_filter = ('suppressed',)

admin.site.register(Regione, RegioneAdmin)
admin.site.register(Provincia, ProvinciaAdmin)
admin.site.register(Comune, ComuneAdmin)
admin.site.register(CittaMetropolitana, CittaMetropolitanaAdmin)
