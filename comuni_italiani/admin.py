# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import *

class ComuneAdmin(admin.ModelAdmin):
    list_display = ('codice_istat', 'name', 'codice_catastale', 'get_provincia_name', 'citta_metropolitana')
    search_fields = ('name', 'codice_istat')
    list_filter = ('provincia',)

    def get_provincia_name(self, obj):
        return obj.provincia.name
    get_provincia_name.short_description = 'Provincia'
    get_provincia_name.admin_order_field = 'provincia__name'

class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ('codice_provincia', 'name', 'codice_targa', 'get_regione_name')
    search_fields = ('codice_provincia', 'name')
    list_filter = ('regione',)

    def get_regione_name(self, obj):
        return obj.regione.name
    get_regione_name.short_description = 'Regione'
    get_regione_name.admin_order_field = 'regione__name'

class RegioneAdmin(admin.ModelAdmin):
    list_display = ('codice_regione', 'name')
    search_fields = ('codice_regione', 'name')

class CittaMetropolitanaAdmin(admin.ModelAdmin):
    list_display = ('codice_cittametropolitana', 'name')
    search_fields = ('codice_cittametropolitana', 'name')

admin.site.register(Regione, RegioneAdmin)
admin.site.register(Provincia, ProvinciaAdmin)
admin.site.register(Comune, ComuneAdmin)
admin.site.register(CittaMetropolitana)
