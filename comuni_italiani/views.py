# -*- coding: utf-8 -*-
import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render

from .models import *

def jsonize_comuni(comuni):
    result = list()

    for comune in comuni:
        result.append(
            {
                'codice_istat': comune.codice_istat,
                'codice_catastale': comune.codice_catastale,
                'name': comune.name,
                'codice_provincia': comune.provincia.codice_provincia,
                'targa_provincia': comune.provincia.codice_targa,
                'codice_cittametropolitana': comune.citta_metropolitana.codice_cittametropolitana if comune.citta_metropolitana is not None else None,
                'is_capoluogo': comune.is_capoluogo,
                'altitudine': comune.altitudine,
                'superficie': comune.superficie,
                'popolazione': comune.popolazione
            }
        )

    return result

def jsonize_cittametro(citta_metro):
    result = list()

    for cm in citta_metro:
        result.append(
            {
                'name': cm.name,
                'codice_cittametropolitana': cm.codice_cittametropolitana,
            }
        )

    return result

def jsonize_province(province):
    result = list()

    for provincia in province:
        result.append(
            {
                'codice_provincia': provincia.codice_provincia,
                'codice_targa': provincia.codice_targa,
                'name': provincia.name,
                'codice_regione': provincia.regione.codice_regione,
                'name_regione': provincia.regione.name,
            }
        )

    return result


def jsonize_regioni(regioni):
    result = list()

    for regione in regioni:
        result.append(
            {
                'codice_regione': regione.codice_regione,
                'name': regione.name,
            }
        )

    return result


def check_elenco_parameters(request, codice):
    if request.method == 'POST':
        if codice is not None or 'codice' not in request.POST:
            return (None, JsonResponse({
                'result_code': 401,
            }))

        try:
            return (int(request.POST['codice']), None)
        except ValueError:
            return (None, JsonResponse({
                'result_code': 401,
            }))
    else:
        return (int(codice), None)

def elenco_comuni_provincia(request, codice=None):
    (codice_provincia, error) = check_elenco_parameters(request, codice)

    if error is not None:
        return error

    try:
        provincia = Provincia.objects.get(codice_provincia=codice_provincia)
    except ObjectDoesNotExist:
        return JsonResponse({'result_code': 404})

    qs = Comune.objects.filter(provincia=codice_provincia).all()

    comuni = jsonize_comuni(qs)

    return JsonResponse({
        'result_code': 200,
        'codice_provincia': codice_provincia,
        'name': provincia.name,
        'codice_targa': provincia.codice_targa,
        'comuni': comuni
    })

def elenco_comuni_regione(request, codice=None):
    (codice_regione, error) = check_elenco_parameters(request, codice)

    if error is not None:
        return error

    try:
        regione = Regione.objects.get(codice_regione=codice_regione)
    except ObjectDoesNotExist:
        return JsonResponse({'result_code': 404})

    qs = Comune.objects.filter(provincia__regione=codice_regione)

    comuni = jsonize_comuni(qs)

    return JsonResponse({
        'result_code': 200,
        'codice_regione': codice_regione,
        'name': regione.name,
        'comuni': comuni
    })


def elenco_comuni_cittmetro(request, codice=None):
    (codice_citta_metro, error) = check_elenco_parameters(request, codice)

    if error is not None:
        return error

    try:
        cittm = CittaMetropolitana.objects.get(codice_cittametropolitana=codice_citta_metro)
    except ObjectDoesNotExist:
        return JsonResponse({'result_code': 404})

    qs = Comune.objects.filter(citta_metropolitana=codice_citta_metro)

    comuni = jsonize_comuni(qs)

    return JsonResponse({
        'result_code': 200,
        'codice_citta_metro': codice_citta_metro,
        'name': cittm.name,
        'comuni': comuni
    })

def elenco_citta_metro(request):
    qs = CittaMetropolitana.objects.all()

    citta_metro = jsonize_cittametro(qs)

    return JsonResponse({
        'result_code': 200,
        'citta_metro': citta_metro
    })


def elenco_province_regione(request, codice=None):
    (codice_regione, error) = check_elenco_parameters(request, codice)

    if error is not None:
        return error

    try:
        regione = Regione.objects.get(codice_regione=codice_regione)
    except ObjectDoesNotExist:
        return JsonResponse({'result_code': 404})

    qs = Provincia.objects.filter(regione=codice_regione)

    province = jsonize_province(qs)

    return JsonResponse({
        'result_code': 200,
        'codice_regione': codice_regione,
        'name': regione.name,
        'province': province
    })

def elenco_province(request):
    qs = Provincia.objects.all()
    province = jsonize_province(qs)

    return JsonResponse({
        'result_code': 200,
        'province': province
    })

def elenco_regioni(request):
    qs = Regione.objects.all()
    regioni = jsonize_regioni(qs)

    return JsonResponse({
        'result_code': 200,
        'regioni': regioni
    })

def check_ricerca_params(request):
    take = 20
    skip = 0

    if request.method != 'POST' or 'nome' not in request.POST:
        return (take, skip, JsonResponse({
            'result_code': 401,
        }))

    try:
        if 'take' in request.POST:
            take = int(request.POST['take'])

        if 'skip' in request.POST:
            skip = int(request.POST['skip'])

        if take <= 0 or skip < 0:
            raise ValueError()
    except ValueError:
        return (take, skip, JsonResponse({
            'result_code': 401,
        }))

    return (take, skip, None)

def ricerca_comune(request):
    (take, skip, error) = check_ricerca_params(request)

    if error is not None:
        return error

    qs = Comune.objects.filter(name__icontains=request.POST['nome'])[skip:skip+take]

    comuni = jsonize_comuni(qs)

    return JsonResponse({
        'result_code': 200,
        'comuni': comuni,
        'take': take,
        'skip': skip
    })

def ricerca_provincia(request):
    (take, skip, error) = check_ricerca_params(request)

    if error is not None:
        return error

    qs = Provincia.objects.filter(name__icontains=request.POST['nome'])[skip:skip+take]

    province = jsonize_province(qs)

    return JsonResponse({
        'result_code': 200,
        'province': province,
        'take': take,
        'skip': skip
    })

def ricerca_regione(request):
    (take, skip, error) = check_ricerca_params(request)

    if error is not None:
        return error

    qs = Regione.objects.filter(name__icontains=request.POST['nome'])[skip:skip+take]

    regioni = jsonize_regioni(qs)

    return JsonResponse({
        'result_code': 200,
        'regioni': regioni,
        'take': take,
        'skip': skip
    })