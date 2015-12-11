# -*- coding: utf-8 -*-

from django.apps import AppConfig


class ComuniItalianiAutocompleteConfig(AppConfig):
    name = 'comuni_italiani.autocomplete'
    verbose_name = "Comuni Italiani Autocomplete"

    def ready(self):
        from django.conf import settings
        import autocomplete_light.shortcuts as autocomplete_light
        from ..models import Comune, Provincia, Regione, CittaMetropolitana
        autocomplete_light.register(Comune,
                                    search_fields=['^name'],
                                    attrs={
                                        'placeholder': 'Nome della città',
                                        'data-autocomplete-minimum-characters': 2,
                                    },
                                    widget_attrs={
                                        'data-widget-maximum-values': getattr(
                                            settings, "COMUNI_ITALIANI_AUTOCOMPLETE_RESULTS", 10),
                                        'class': 'modern-style',
                                    },
                                    )

        autocomplete_light.register(Provincia,
                                    search_fields=['^name'],
                                    attrs={
                                        'placeholder': 'Nome della provincia',
                                        'data-autocomplete-minimum-characters': 2,
                                    },
                                    widget_attrs={
                                        'data-widget-maximum-values': getattr(
                                            settings, "COMUNI_ITALIANI_AUTOCOMPLETE_RESULTS", 10),
                                        'class': 'modern-style',
                                    },
                                    )

        autocomplete_light.register(Regione,
                                    search_fields=['^name'],
                                    attrs={
                                        'placeholder': 'Nome della regione',
                                        'data-autocomplete-minimum-characters': 2,
                                    },
                                    widget_attrs={
                                        'data-widget-maximum-values': getattr(
                                            settings, "COMUNI_ITALIANI_AUTOCOMPLETE_RESULTS", 10),
                                        'class': 'modern-style',
                                    },
                                    )

        autocomplete_light.register(CittaMetropolitana,
                                    search_fields=['^name'],
                                    attrs={
                                        'placeholder': 'Nome della città metropolitana',
                                        'data-autocomplete-minimum-characters': 2,
                                    },
                                    widget_attrs={
                                        'data-widget-maximum-values': getattr(
                                            settings, "COMUNI_ITALIANI_AUTOCOMPLETE_RESULTS", 10),
                                        'class': 'modern-style',
                                    },
                                    )
