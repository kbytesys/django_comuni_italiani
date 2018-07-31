from django.urls import path
from . import views


urlpatterns = [
    path(
        'regione/',
        views.RegioneAutocomplete.as_view(),
        name='regione-autocomplete',
    ),
    path(
        'provincia/',
        views.ProvinciaAutocomplete.as_view(),
        name='provincia-autocomplete',
    ),
    path(
        'cittametropolitana/',
        views.CittaMetropolitanaAutocomplete.as_view(),
        name='cittametropolitana-autocomplete',
    ),
    path(
        'comune/',
        views.ComuneAutocomplete.as_view(),
        name='comune-autocomplete',
    ),
]
