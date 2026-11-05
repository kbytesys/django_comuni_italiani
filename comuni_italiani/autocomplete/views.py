from django.conf import settings
from dal.autocomplete import Select2QuerySetView
from .. import models

RESULTS_PER_PAGE = getattr(settings, "COMUNI_ITALIANI_AUTOCOMPLETE_RESULTS", 10)


class BaseAutocomplete(Select2QuerySetView):
    model_clazz = None
    manager = 'objects'
    limit_results = None
    forwarded_field = None
    paginate_by = RESULTS_PER_PAGE

    def get_queryset(self):
        qs = getattr(self.model_clazz, self.manager).all()

        if self.forwarded_field:
            fw_value = self.forwarded.get(self.forwarded_field, None)

            if fw_value:
                qs = qs.filter(**{self.forwarded_field: fw_value})

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs

    def get_result_label(self, result):
        label = super().get_result_label(result)
        return '%s (soppresso)' % label if result.suppressed else label


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

    def get_queryset(self):
        return super().get_queryset().select_related('provincia')


class RegioneAllAutocomplete(RegioneAutocomplete):
    manager = 'all_objects'


class RegioneSuppressedAutocomplete(RegioneAutocomplete):
    manager = 'suppressed_objects'


class ProvinciaAllAutocomplete(ProvinciaAutocomplete):
    manager = 'all_objects'


class ProvinciaSuppressedAutocomplete(ProvinciaAutocomplete):
    manager = 'suppressed_objects'


class CittaMetropolitanaAllAutocomplete(CittaMetropolitanaAutocomplete):
    manager = 'all_objects'


class CittaMetropolitanaSuppressedAutocomplete(CittaMetropolitanaAutocomplete):
    manager = 'suppressed_objects'


class ComuneAllAutocomplete(ComuneAutocomplete):
    manager = 'all_objects'


class ComuneSuppressedAutocomplete(ComuneAutocomplete):
    manager = 'suppressed_objects'
