from dal import autocomplete
from django import forms

from .. import models


class SuppressibleAutocompleteField(forms.ModelChoiceField):
    """
    Campo con autocompletamento in cui widget e queryset usano sempre lo stesso manager: un oggetto mostrato
    dall'autocompletamento è quindi anche una scelta valida per il form.

    manager: 'objects' (solo attivi, default), 'all_objects' (tutti) o 'suppressed_objects' (solo soppressi).
    """
    model = None
    url_name = None
    URL = {
        'objects': '%s-autocomplete',
        'all_objects': '%s-all-autocomplete',
        'suppressed_objects': '%s-suppressed-autocomplete',
    }

    def __init__(self, manager='objects', forward=None, **kwargs):
        url = self.URL[manager] % self.url_name
        kwargs.setdefault('queryset', getattr(self.model, manager).all())
        kwargs.setdefault('widget', autocomplete.ModelSelect2(url=url, forward=forward))
        super().__init__(**kwargs)


class RegioneAutocompleteField(SuppressibleAutocompleteField):
    model = models.Regione
    url_name = 'regione'


class ProvinciaAutocompleteField(SuppressibleAutocompleteField):
    model = models.Provincia
    url_name = 'provincia'


class CittaMetropolitanaAutocompleteField(SuppressibleAutocompleteField):
    model = models.CittaMetropolitana
    url_name = 'cittametropolitana'


class ComuneAutocompleteField(SuppressibleAutocompleteField):
    model = models.Comune
    url_name = 'comune'
