# -*- coding: utf-8 -*-
import argparse
import csv
import os

from django.core.management.base import BaseCommand, CommandError

from comuni_italiani.models import *

default_regioni_file = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../../fixtures')), 'ripartizioni-reg-prov-cm.csv'
)

class Command(BaseCommand):
    help = 'Importa regioni e province italiane'

    def add_arguments(self, parser):
        parser.add_argument('-csvfile', type=argparse.FileType('r', encoding='iso-8859-15'),
                            default=default_regioni_file)

    def handle(self, *args, **options):

        csvfile = options['csvfile']

        reader = csv.DictReader(csvfile, delimiter=';')

        '''
        Importazione delle regioni, province e città metropolitane
        '''

        regioni_keys = set()

        for row in reader:
            codice_regione = row['Codice regione']

            if codice_regione is None or len(codice_regione) == 0:
                continue

            codice_regione = int(codice_regione)

            if codice_regione not in regioni_keys:
                r = Regione()
                r.codice_regione = codice_regione
                r.name = row['Denominazione regione']
                regioni_keys.add(codice_regione)
                r.save()

            codice_provincia = int(row['Codice provincia'])
            codice_citta_metropolitana = None

            try:
                codice_citta_metropolitana = int(row['Codice Città Metropolitana'])
            except ValueError:
                pass

            if codice_citta_metropolitana is not None:
                c = CittaMetropolitana()
                c.codice_cittametropolitana = codice_citta_metropolitana
                name = row['Denominazione                  Città metropolitana']
                c.name = name
                c.save()
            else:
                name = row['Denominazione provincia']

            p = Provincia()
            p.name = name
            p.codice_provincia = codice_provincia
            p.codice_targa = row['Sigla automobilistica']
            p.regione_id = codice_regione
            p.save()

        self.stdout.write("Importazione completata")
