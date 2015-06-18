# -*- coding: utf-8 -*-
import argparse
import csv
import sys
import os
import locale

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from comuni_italiani.models import *

default_comuni_file = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../../fixtures')), 'elenco-comuni-italiani.csv'
)


locale.setlocale( locale.LC_ALL, 'it_IT.UTF-8' )

class NotRunningInTTYException(Exception):
    pass

class Command(BaseCommand):
    help = 'Importa i comuni italiani'

    def add_arguments(self, parser):
        parser.add_argument('-csvfile', type=argparse.FileType('r', encoding='iso-8859-15'),
                            default=default_comuni_file)

    def execute(self, *args, **options):
        self.stdin = options.get('stdin', sys.stdin)  # Used for testing
        return super(Command, self).execute(*args, **options)

    def handle(self, *args, **options):

        if hasattr(self.stdin, 'isatty') and not self.stdin.isatty():
            raise NotRunningInTTYException("Not running in a TTY")

        csvfile = options['csvfile']

        reader = csv.DictReader(csvfile, delimiter=';')

        counter_totale = 0
        counter_aggiunti = 0
        counter_modificati = 0
        counter_ignorati = 0

        comuni_rilevati = set()

        for row in reader:
            codice_istat = row['Codice Istat del Comune \n(formato numerico)']

            if codice_istat is None or len(codice_istat) == 0:
                continue

            counter_totale += 1

            if counter_totale % 20 == 0:
                self.stdout.write("Righe analizzate %d" % counter_totale)

            codice_istat = int(codice_istat)

            comuni_rilevati.add(codice_istat)

            name = row['Solo denominazione in italiano']
            provincia_id = int(row['Codice Provincia *'])
            codice_catastale = row['Codice Catastale ']
            is_capoluogo = row['Comune capoluogo di provincia'] == '1'
            altitudine = locale.atoi(row['Altitudine del centro (metri)'])
            superficie = locale.atof(row['Superficie territoriale (kmq) al 09/10/2011'])
            popolazione = locale.atoi(row['Popolazione legale 2011 (09/10/2011)'])
            citta_metropolitana_id = None
            try:
                citta_metropolitana_id = int(row['Codice Città Metropolitana'])
            except ValueError:
                pass

            try:
                r = Comune.objects.get(codice_istat=codice_istat)

                if r.codice_istat == codice_istat and r.name == name and r.provincia_id == provincia_id and \
                    r.codice_catastale == codice_catastale and r.citta_metropolitana_id == citta_metropolitana_id and \
                    r.is_capoluogo == is_capoluogo and r.altitudine == altitudine and r.superficie == superficie and \
                        r.popolazione == popolazione:
                    continue
                else:
                    ignore_me = False
                    if r.codice_istat is not None and r.name != name:
                        self.stdout.write("Rilevato cambio nome per un codice istat, assicurati che non sia una rinumerazione\n")
                        self.stdout.write("DB: %s %s\n" % (r.codice_istat, r.name))
                        self.stdout.write("CSV: %s %s\n" % (codice_istat, name))
                        valid_choice = False
                        while not valid_choice:
                            choice = input("Vuoi aggiornare questo record? [y/n] ")
                            if choice in ["y", "n"]:
                                valid_choice = True
                                if choice == "n":
                                    counter_ignorati += 1

                    if ignore_me:
                        continue

                    counter_modificati += 1
            except Comune.DoesNotExist:
                r = Comune()
                counter_aggiunti += 1

            r.codice_istat = codice_istat
            r.name = name
            r.provincia_id = provincia_id
            r.codice_catastale = codice_catastale
            r.citta_metropolitana_id = citta_metropolitana_id
            r.is_capoluogo = is_capoluogo
            r.altitudine = altitudine
            r.superficie = superficie
            r.popolazione = popolazione

            r.save()

        self.stdout.write("Totale righe analizzate: %d" % counter_totale)
        self.stdout.write("Totale comuni aggiunti: %d" % counter_aggiunti)
        self.stdout.write("Totale comuni modificati: %d" % counter_modificati)
        self.stdout.write("Totale comuni ignorati: %d" % counter_ignorati)

        '''
        Controlla i comuni con lo stesso nome per evitare che nel db sia presente lo stesso comune ma con codici
        istat diversi. In futuro il comando per analizzare il file dei cambiamenti istat dovrebbe gestire queste
        situazioni da se.
        '''
        self.stdout.write("Controllo comuni con lo stesso nome\n")
        qs = Comune.objects.values('name').annotate(count=Count('id')).filter(count__gt=1).order_by('name')
        for item in qs:
            for item2 in Comune.objects.filter(name=item['name']):
                print("%s - %s - %s" % (item2.codice_istat, item2.name, item2.provincia.name))
        self.stdout.write("Numero totale comuni con lo stesso nome: %d\n" % len(qs))

        '''
        Controlla i comuni eventualmente rimossi ma presenti nel database
        '''
        self.stdout.write("Controllo comuni rimossi\n")
        qs = Comune.objects.exclude(codice_istat__in=comuni_rilevati)
        for comune in qs:
            print("%s - %s - %s" % (comune.codice_istat, comune.name, comune.provincia.name))
        self.stdout.write("Numero totale comuni presenti nel db ma rimossi da istat: %d\n" % len(qs))

        self.stdout.write("Importazione completata")