from django.conf.urls import url
from . import views


urlpatterns = [
    url(
        r'^regione/$',
        views.RegioneAutocomplete.as_view(),
        name='regione-autocomplete',
    ),
    url(
        r'^provincia/$',
        views.ProvinciaAutocomplete.as_view(),
        name='provincia-autocomplete',
    ),
    url(
        r'^cittametropolitana/$',
        views.CittaMetropolitanaAutocomplete.as_view(),
        name='cittametropolitana-autocomplete',
    ),
    url(
        r'^comune/$',
        views.ComuneAutocomplete.as_view(),
        name='comune-autocomplete',
    ),
]
