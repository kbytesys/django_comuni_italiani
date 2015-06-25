from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^elenco/comuni/provincia/(?P<codice>[0-9]+)/$',
        views.elenco_comuni_provincia, name="elenco_comuni_provincia"),
    url(r'^elenco/comuni/provincia/$',
        views.elenco_comuni_provincia, name="elenco_comuni_provincia_post"),

    url(r'^elenco/comuni/regione/(?P<codice>[0-9]+)/$',
        views.elenco_comuni_regione, name="elenco_comuni_regione"),
    url(r'^elenco/comuni/regione/$',
        views.elenco_comuni_regione, name="elenco_comuni_regione_post"),

    url(r'^elenco/comuni/citta_metro/(?P<codice>[0-9]+)/$',
        views.elenco_comuni_cittmetro, name="elenco_comuni_cittmetro"),
    url(r'^elenco/comuni/citta_metro/$',
        views.elenco_comuni_cittmetro, name="elenco_comuni_cittmetro_post"),

    url(r'^elenco/province/regione/(?P<codice>[0-9]+)/$',
        views.elenco_province_regione, name="elenco_province_regione"),
    url(r'^elenco/province/regione/$',
        views.elenco_province_regione, name="elenco_province_regione_post"),

    url(r'^elenco/province/$', views.elenco_province, name="elenco_province"),
    url(r'^elenco/regioni/$', views.elenco_regioni, name="elenco_regioni"),
    url(r'^elenco/citta_metro/$', views.elenco_citta_metro, name="elenco_citta_metro"),

    url(r'^ricerca/comune/$', views.ricerca_comune, name="ricerca_comune"),
    url(r'^ricerca/provincia/$', views.ricerca_provincia, name="ricerca_provincia"),
    url(r'^ricerca/regione/$', views.ricerca_regione, name="ricerca_regione"),
]