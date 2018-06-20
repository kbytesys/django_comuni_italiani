from django.conf import settings
from dal.autocomplete import Select2QuerySetView
from .. import models

RESULTS_PER_PAGE = getattr(settings, "COMUNI_ITALIANI_AUTOCOMPLETE_RESULTS", 10)


class BaseAutocomplete(Select2QuerySetView):
    model_clazz = None
    limit_results = None
    forwarded_field = None
    paginate_by = RESULTS_PER_PAGE

    def get_queryset(self):
        qs = self.model_clazz.objects.all()

        if self.forwarded_field:
            fw_value = self.forwarded.get(self.forwarded_field, None)

            if fw_value:
                qs = qs.filter(**{self.forwarded_field: fw_value})

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class RegioneAutocomplete(BaseAutocomplete):
    model_clazz = models.Regione


class ProvinciaAutocomplete(BaseAutocomplete):
    model_clazz = models.Provincia
    forwarded_field = 'regione'


class CittaMetropolitanaAutocomplete(BaseAutocomplete):
    model_clazz = models.CittaMetropolitana
    forwarded_field = 'regione'


class ComuneAutocomplete(BaseAutocomplete):
    model_clazz = models.Comune
    forwarded_field = 'provincia'
