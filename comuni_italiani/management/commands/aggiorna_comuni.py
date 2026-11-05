# -*- coding: utf-8 -*-
"""
Aggiorna regioni, province, città metropolitane e comuni (attivi e soppressi) dalle API SITUAS dell'Istat.

Regole principali:
 - una riga per codice: lo stato attivo/soppresso è deciso dall'elenco dei comuni attivi;
 - una provincia resta attiva finché almeno un comune attivo usa il suo codice (es. Torino 001 resta attiva anche se
   per l'Istat è stata sostituita dalla Città metropolitana 201);
 - un comune attivo viene riconosciuto prima dal codice catastale, che non cambia quando il comune cambia provincia o
   nome, e solo dopo dal codice Istat: se il codice è cambiato viene ricodificato sulla stessa riga, così le foreign
   key esistenti continuano a puntare al comune corretto;
 - se il codice di un comune attivo è occupato da una riga che non corrisponde a nessun comune attivo (es. una
   vecchia incarnazione soppressa), la riga viene eliminata solo se nessun altro dato vi fa riferimento, altrimenti
   viene segnalato un errore e il comune non viene modificato.

Il comando non richiede input ed è pensato per essere eseguito anche da cron: senza --verbose scrive solo gli errori.
"""
import json
import urllib.request
from collections import Counter, defaultdict
from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from comuni_italiani.models import CittaMetropolitana, Comune, Provincia, Regione

SITUAS_URL = 'https://situas-servizi.istat.it/publish/reportspooljson?pfun=%d&%s'
TIMEOUT = 120
DATA_INIZIO = '17/03/1861'

PFUN_COMUNI_ATTIVI = 61
PFUN_ALTITUDINE = 73
PFUN_POPOLAZIONE_SUPERFICIE = 74
PFUN_COMUNI_SOPPRESSI = 98
PFUN_REGIONI_SOPPRESSE = 106
PFUN_PROVINCE_SOPPRESSE = 112

TIPO_UTS_CITTA_METROPOLITANA = 3

# Province cedute a stato estero nel 1947 (Fiume, Istria/Pola, Zara): l'Istat non indica una provincia che le
# sostituisce, le colleghiamo quindi al compartimento storico "Venezia Giulia".
REGIONE_PROVINCE_CEDUTE = {701: 83, 702: 83, 703: 83}


def data_valida(valore):
    datetime.strptime(valore, '%d/%m/%Y')
    return valore


def piu_recenti(rows, campo_codice):
    """Per ogni codice restituisce la riga con la data di variazione più recente."""
    result = {}
    for row in rows:
        codice = int(row[campo_codice])
        if codice not in result or row['DATA_INIZIO_AMMINISTRATIVA'] > result[codice]['DATA_INIZIO_AMMINISTRATIVA']:
            result[codice] = row
    return result


class Command(BaseCommand):
    help = 'Aggiorna regioni, province, città metropolitane e comuni (attivi e soppressi) dalle API Istat'

    def add_arguments(self, parser):
        parser.add_argument('--data-da', type=data_valida, default=DATA_INIZIO,
                            help='Data iniziale per le soppressioni, GG/MM/AAAA (default %s)' % DATA_INIZIO)
        parser.add_argument('--data-a', type=data_valida, default=None,
                            help='Data finale per le soppressioni, GG/MM/AAAA (default oggi). '
                                 "L'elenco dei comuni attivi è sempre quello di oggi")
        parser.add_argument('--verbose', action='store_true',
                            help="Scrive il dettaglio dell'importazione; senza, scrive solo gli errori")
        parser.add_argument('--dry-run', action='store_true',
                            help='Esegue tutto senza salvare le modifiche')

    def handle(self, *args, **options):
        self.verbose = options['verbose']
        self.errori = 0
        self.stats = defaultdict(Counter)

        # Gli attivi sono sempre quelli di oggi: una data passata riporterebbe indietro il database
        oggi = date.today().strftime('%d/%m/%Y')
        data_da = options['data_da']
        data_a = options['data_a'] or oggi

        # Tutti i dati vengono scaricati e controllati prima di toccare il database
        attivi = self.scarica(PFUN_COMUNI_ATTIVI, pdata=oggi)
        self.controlla(attivi, PFUN_COMUNI_ATTIVI, ['PRO_COM', 'COMUNE_IT', 'COD_CATASTO', 'COD_REG', 'DEN_REG',
                                                   'COD_PROV_STORICO', 'COD_UTS', 'DEN_UTS', 'TIPO_UTS',
                                                   'SIGLA_AUTOMOBILISTICA', 'CC_UTS'], obbligatorio=True)
        altitudini = self.scarica(PFUN_ALTITUDINE, pdata=oggi)
        self.controlla(altitudini, PFUN_ALTITUDINE, ['PRO_COM', 'ALT'])
        popolazioni = self.scarica(PFUN_POPOLAZIONE_SUPERFICIE, pdata=oggi)
        self.controlla(popolazioni, PFUN_POPOLAZIONE_SUPERFICIE, ['PRO_COM', 'POP_LEG', 'AREA_KMQ'])
        comuni_soppressi = self.scarica(PFUN_COMUNI_SOPPRESSI, pdatada=data_da, pdataa=data_a)
        self.controlla(comuni_soppressi, PFUN_COMUNI_SOPPRESSI, ['PRO_COM_T', 'COMUNE', 'COD_CATASTO', 'COD_UTS',
                                                                 'DATA_INIZIO_AMMINISTRATIVA'])
        regioni_soppresse = self.scarica(PFUN_REGIONI_SOPPRESSE, pdatada=data_da, pdataa=data_a)
        self.controlla(regioni_soppresse, PFUN_REGIONI_SOPPRESSE, ['COD_COMP_REG', 'DEN_COMP_REG',
                                                                   'DATA_INIZIO_AMMINISTRATIVA'])
        province_soppresse = self.scarica(PFUN_PROVINCE_SOPPRESSE, pdatada=data_da, pdataa=data_a)
        self.controlla(province_soppresse, PFUN_PROVINCE_SOPPRESSE, ['COD_UTS', 'DEN_UTS', 'SIGLA_UTS', 'TIPO_UTS',
                                                                     'DATA_INIZIO_AMMINISTRATIVA'])

        try:
            with transaction.atomic():
                self.aggiorna_regioni(attivi, regioni_soppresse)
                self.aggiorna_province(attivi, province_soppresse)
                self.aggiorna_citta_metropolitane(attivi, province_soppresse)
                self.aggiorna_comuni_attivi(attivi, altitudini, popolazioni)
                self.aggiorna_comuni_soppressi(comuni_soppressi)

                if options['dry_run']:
                    transaction.set_rollback(True)
        except IntegrityError as e:
            raise CommandError('Conflitto non risolvibile automaticamente, nessuna modifica salvata: %s' % e)

        self.riepilogo(options['dry_run'])

        if self.errori:
            raise CommandError("Aggiornamento completato con %d errori" % self.errori)

    # Download e controlli

    def scarica(self, pfun, **params):
        url = SITUAS_URL % (pfun, '&'.join('%s=%s' % item for item in params.items()))
        request = urllib.request.Request(url, headers={'User-Agent': 'django-comuni-italiani'})
        self.log('Scarico %s' % url)
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                return json.loads(response.read().decode('utf-8'))['resultset'] or []
        except (OSError, ValueError, KeyError, TypeError) as e:
            raise CommandError('Impossibile scaricare i dati Istat da %s: %s' % (url, e))

    def controlla(self, rows, pfun, campi, obbligatorio=False):
        if not rows:
            if obbligatorio:
                raise CommandError('Il report Istat pfun=%d non contiene dati' % pfun)
            return
        mancanti = set(campi) - set(rows[0])
        if mancanti:
            raise CommandError('Il report Istat pfun=%d non contiene i campi: %s' % (pfun, ', '.join(sorted(mancanti))))

    # Output

    def log(self, messaggio):
        if self.verbose:
            self.stdout.write(messaggio)

    def errore(self, messaggio):
        self.errori += 1
        self.stderr.write(messaggio)

    def salva(self, istanza, valori, descrizione):
        """Applica i valori all'istanza e la salva solo se qualcosa è cambiato."""
        nuova = istanza._state.adding
        modifiche = []
        for campo, valore in valori.items():
            vecchio = getattr(istanza, campo)
            if vecchio != valore:
                modifiche.append((campo, vecchio, valore))
                setattr(istanza, campo, valore)

        if not nuova and not modifiche:
            return

        istanza.save()

        modello = istanza._meta.verbose_name
        if nuova:
            self.stats[modello]['creati'] += 1
            self.log('Creato %s %s' % (modello, descrizione))
            return

        campi = [m[0] for m in modifiche]
        if 'suppressed' in campi:
            self.stats[modello]['soppressi' if istanza.suppressed else 'riattivati'] += 1
        else:
            self.stats[modello]['aggiornati'] += 1
        self.log('Aggiornato %s %s: %s' % (modello, descrizione,
                                           ', '.join('%s %r -> %r' % m for m in modifiche)))

    def riepilogo(self, dry_run):
        if not self.verbose:
            return
        self.stdout.write('Riepilogo%s:' % (' (dry-run, nessuna modifica salvata)' if dry_run else ''))
        for modello in ('regione', 'provincia', 'città metropolitana', 'comune'):
            valori = self.stats.get(modello)
            dettaglio = ', '.join('%s %d' % item for item in sorted(valori.items())) if valori else 'nessuna modifica'
            self.stdout.write('  %s: %s' % (modello, dettaglio))
        for chiave, valore in sorted(self.stats['altro'].items()):
            self.stdout.write('  %s: %d' % (chiave, valore))

    # Regioni

    def aggiorna_regioni(self, attivi, regioni_soppresse):
        esistenti = {r.pk: r for r in Regione.all_objects.all()}
        nomi_attivi = {int(r['COD_REG']): r['DEN_REG'] for r in attivi}

        for codice, nome in nomi_attivi.items():
            regione = esistenti.get(codice) or Regione(codice_regione=codice)
            self.salva(regione, {'name': nome, 'suppressed': False}, '%02d %s' % (codice, nome))

        soppresse = piu_recenti(regioni_soppresse, 'COD_COMP_REG')
        for codice, row in soppresse.items():
            if codice in nomi_attivi:
                continue
            regione = esistenti.get(codice) or Regione(codice_regione=codice)
            self.salva(regione, {'name': row['DEN_COMP_REG'], 'suppressed': True},
                       '%02d %s' % (codice, row['DEN_COMP_REG']))

        for codice, regione in esistenti.items():
            if codice not in nomi_attivi and codice not in soppresse:
                self.salva(regione, {'suppressed': True}, '%02d %s' % (codice, regione.name))

    # Province

    def aggiorna_province(self, attivi, province_soppresse):
        esistenti = {p.pk: p for p in Provincia.all_objects.all()}
        regioni = set(Regione.all_objects.values_list('pk', flat=True))

        province_attive = {}
        regione_uts = {}
        for row in attivi:
            codice = int(row['COD_PROV_STORICO'])
            province_attive[codice] = (row['DEN_UTS'], row['SIGLA_AUTOMOBILISTICA'], int(row['COD_REG']))
            regione_uts[codice] = int(row['COD_REG'])
            regione_uts[int(row['COD_UTS'])] = int(row['COD_REG'])

        for codice, (nome, sigla, regione) in province_attive.items():
            provincia = esistenti.get(codice) or Provincia(codice_provincia=codice)
            self.salva(provincia, {'name': nome, 'codice_targa': sigla, 'regione_id': regione, 'suppressed': False},
                       '%03d %s' % (codice, nome))

        successori = defaultdict(set)
        for row in province_soppresse:
            if row.get('COD_UTS_REL'):
                successori[int(row['COD_UTS'])].add(int(row['COD_UTS_REL']))

        soppresse = piu_recenti([r for r in province_soppresse if int(r['TIPO_UTS']) != TIPO_UTS_CITTA_METROPOLITANA],
                                'COD_UTS')
        for codice, row in soppresse.items():
            if codice in province_attive:
                continue
            provincia = esistenti.get(codice) or Provincia(codice_provincia=codice)
            regione = provincia.regione_id if not provincia._state.adding else \
                self.regione_provincia_soppressa(codice, successori, regione_uts)
            if regione not in regioni:
                self.errore('Provincia soppressa %03d %s: regione non trovata, ignorata' % (codice, row['DEN_UTS']))
                continue
            # Per alcune province storiche l'Istat riporta come sigla il nome per esteso (es. "Venezia Giulia")
            sigla = row['SIGLA_UTS'] if len(row['SIGLA_UTS'] or '') <= 2 else ''
            self.salva(provincia, {'name': row['DEN_UTS'], 'codice_targa': sigla, 'regione_id': regione,
                                   'suppressed': True}, '%03d %s' % (codice, row['DEN_UTS']))

        for codice, provincia in esistenti.items():
            if codice not in province_attive and codice not in soppresse:
                self.salva(provincia, {'suppressed': True}, '%03d %s' % (codice, provincia.name))

    def regione_provincia_soppressa(self, codice, successori, regione_uts):
        """Risale le province che hanno sostituito quella soppressa fino ad una con regione nota."""
        da_visitare, visitati = [codice], set()
        while da_visitare:
            corrente = da_visitare.pop(0)
            if corrente in regione_uts:
                return regione_uts[corrente]
            if corrente in REGIONE_PROVINCE_CEDUTE:
                return REGIONE_PROVINCE_CEDUTE[corrente]
            visitati.add(corrente)
            da_visitare.extend(s for s in successori[corrente] if s not in visitati)
        return None

    # Città metropolitane

    def aggiorna_citta_metropolitane(self, attivi, province_soppresse):
        esistenti = {c.pk: c for c in CittaMetropolitana.all_objects.all()}

        attive = {int(r['COD_UTS']): r['DEN_UTS'] for r in attivi if int(r['TIPO_UTS']) == TIPO_UTS_CITTA_METROPOLITANA}
        for codice, nome in attive.items():
            citta = esistenti.get(codice) or CittaMetropolitana(codice_cittametropolitana=codice)
            self.salva(citta, {'name': nome, 'suppressed': False}, '%03d %s' % (codice, nome))

        # Le città metropolitane soppresse compaiono come provincia soppressa o come sostituta di una provincia
        soppresse = {}
        for row in province_soppresse:
            if int(row['TIPO_UTS']) == TIPO_UTS_CITTA_METROPOLITANA:
                soppresse[int(row['COD_UTS'])] = row['DEN_UTS']
            if row.get('COD_UTS_REL') and int(row.get('TIPO_UTS_REL') or 0) == TIPO_UTS_CITTA_METROPOLITANA:
                soppresse.setdefault(int(row['COD_UTS_REL']), row['DEN_UTS_REL'])

        for codice, nome in soppresse.items():
            if codice in attive:
                continue
            citta = esistenti.get(codice) or CittaMetropolitana(codice_cittametropolitana=codice)
            self.salva(citta, {'name': nome, 'suppressed': True}, '%03d %s' % (codice, nome))

        for codice, citta in esistenti.items():
            if codice not in attive and codice not in soppresse:
                self.salva(citta, {'suppressed': True}, '%03d %s' % (codice, citta.name))

    # Comuni

    def aggiorna_comuni_attivi(self, attivi, altitudini, popolazioni):
        esistenti = list(Comune.all_objects.all())
        per_codice = {c.codice_istat: c for c in esistenti}
        catastali_attivi = Counter(c.codice_catastale for c in esistenti if not c.suppressed and c.codice_catastale)
        per_catastale = {c.codice_catastale: c for c in esistenti
                         if not c.suppressed and c.codice_catastale and catastali_attivi[c.codice_catastale] == 1}
        altitudine = {int(r['PRO_COM']): r['ALT'] for r in altitudini}
        popolazione = {int(r['PRO_COM']): (r['POP_LEG'], r['AREA_KMQ']) for r in popolazioni}

        abbinati = set()   # pk delle righe che corrispondono ad un comune attivo Istat
        protetti = set()   # pk da non sopprimere perché coinvolti in un errore

        # 1. Riga del database corrispondente ad ogni comune attivo: prima per codice catastale (stabile anche se il
        # comune cambia provincia), poi per codice Istat se la riga ha lo stesso catastale (comune ricostituito)
        abbinamenti = []
        for row in attivi:
            codice, catastale = int(row['PRO_COM']), row['COD_CATASTO']
            comune = per_catastale.get(catastale)
            stesso_codice = per_codice.get(codice)
            if comune is None and catastali_attivi[catastale] > 1:
                # Più comuni attivi con lo stesso catastale: si può scegliere solo quello che ha già il codice giusto
                if stesso_codice is not None and not stesso_codice.suppressed and \
                        stesso_codice.codice_catastale == catastale:
                    comune = stesso_codice
                else:
                    duplicati = [c for c in esistenti if not c.suppressed and c.codice_catastale == catastale]
                    self.errore('Comune %06d %s: nel database ci sono più comuni attivi con catastale %s (%s), '
                                'ignorato' % (codice, row['COMUNE_IT'], catastale,
                                              ', '.join('%06d %s' % (c.codice_istat, c.name) for c in duplicati)))
                    protetti.update(c.pk for c in duplicati)
                    continue
            elif comune is None and stesso_codice is not None and \
                    stesso_codice.codice_catastale in (catastale, None, ''):
                comune = stesso_codice
            if comune is not None:
                abbinati.add(comune.pk)
            abbinamenti.append((row, comune))

        # 2. Il codice può essere occupato da una riga che non corrisponde a nessun comune attivo: una vecchia
        # incarnazione soppressa oppure un comune a cui l'Istat ha tolto il codice. Vale il comune attivo: la riga
        # viene eliminata se nessun dato vi fa riferimento, altrimenti serve un intervento manuale.
        validi = []
        for row, comune in abbinamenti:
            codice = int(row['PRO_COM'])
            occupante = per_codice.get(codice)
            if occupante is None or occupante is comune or occupante.pk in abbinati:
                validi.append((row, comune))
                continue
            descrizione = '%06d %s (catastale %s)' % (occupante.codice_istat, occupante.name, occupante.codice_catastale)
            if self.referenziato(occupante):
                self.errore('Comune %06d %s: il codice è usato da %s, a cui fanno riferimento altri dati; '
                            'comune ignorato, serve un intervento manuale' % (codice, row['COMUNE_IT'], descrizione))
                if comune is not None:
                    protetti.add(comune.pk)
                continue
            occupante.delete()
            del per_codice[codice]
            self.stats['comune']['eliminati'] += 1
            self.log('Eliminato comune %s: il codice ora è di %s' % (descrizione, row['COMUNE_IT']))
            validi.append((row, comune))

        # 3. Ricodifiche in due passaggi con codici temporanei negativi, così anche uno scambio di codici tra due
        # comuni non viola il vincolo unique
        ricodifiche = [(comune, int(row['PRO_COM'])) for row, comune in validi
                       if comune is not None and comune.codice_istat != int(row['PRO_COM'])]
        for comune, codice in ricodifiche:
            Comune.all_objects.filter(pk=comune.pk).update(codice_istat=-codice)
        for comune, codice in ricodifiche:
            Comune.all_objects.filter(pk=comune.pk).update(codice_istat=codice)
            self.stats['altro']['comuni ricodificati'] += 1
            self.log('Ricodificato comune %s: %06d -> %06d' % (comune.name, comune.codice_istat, codice))
            comune.codice_istat = codice

        # 4. Aggiornamento dei dati
        for row, comune in validi:
            codice = int(row['PRO_COM'])
            if comune is None:
                comune = Comune(codice_istat=codice)

            tipo_uts = int(row['TIPO_UTS'])
            valori = {
                'name': row['COMUNE_IT'],
                'codice_catastale': row['COD_CATASTO'],
                'provincia_id': int(row['COD_PROV_STORICO']),
                'citta_metropolitana_id': int(row['COD_UTS']) if tipo_uts == TIPO_UTS_CITTA_METROPOLITANA else None,
                'is_capoluogo': int(row['CC_UTS']) == 1,
                'suppressed': False,
            }
            if codice in altitudine:
                valori['altitudine'] = altitudine[codice]
            if codice in popolazione:
                valori['popolazione'], valori['superficie'] = popolazione[codice]
            self.salva(comune, valori, '%06d %s' % (codice, row['COMUNE_IT']))

        # 5. I comuni attivi nel database che non corrispondono più a nessun comune attivo Istat sono soppressi
        for comune in esistenti:
            if comune.pk is None or comune.suppressed or comune.pk in abbinati or comune.pk in protetti:
                continue
            self.salva(comune, {'suppressed': True}, '%06d %s' % (comune.codice_istat, comune.name))

    def referenziato(self, istanza):
        """Indica se altri dati, anche dei progetti che usano l'app, fanno riferimento a questa riga."""
        for relazione in istanza._meta.get_fields(include_hidden=True):
            if not relazione.auto_created or relazione.concrete:
                continue
            if relazione.one_to_many or relazione.one_to_one or relazione.many_to_many:
                if relazione.related_model._base_manager.filter(**{relazione.field.name: istanza}).exists():
                    return True
        return False

    def aggiorna_comuni_soppressi(self, comuni_soppressi):
        esistenti = {c.codice_istat: c for c in Comune.all_objects.all()}
        province = set(Provincia.all_objects.values_list('pk', flat=True))
        citta_metropolitane = set(CittaMetropolitana.all_objects.values_list('pk', flat=True))

        for codice, row in piu_recenti(comuni_soppressi, 'PRO_COM_T').items():
            comune = esistenti.get(codice)
            if comune is not None and not comune.suppressed:
                # Codice riutilizzato da un comune oggi attivo: vale lo stato più recente
                self.stats['altro']['soppressi ignorati (codice oggi attivo)'] += 1
                continue
            if comune is not None and comune.codice_catastale and comune.codice_catastale != row['COD_CATASTO']:
                # Soppressione di un altro comune che in passato ha avuto lo stesso codice (es. con --data-a nel
                # passato): la riga esistente non viene trasformata in un comune diverso
                self.stats['altro']['soppressi ignorati (codice di un altro comune)'] += 1
                continue

            # Il codice Istat di una città metropolitana è il codice della provincia storica + 200
            uts = int(row['COD_UTS'])
            citta = uts if uts in citta_metropolitane else None
            provincia = uts - 200 if citta else uts
            if provincia not in province:
                self.errore('Comune soppresso %06d %s: provincia %03d non trovata, ignorato' %
                            (codice, row['COMUNE'], uts))
                continue

            if comune is None:
                comune = Comune(codice_istat=codice)
            valori = {
                'name': row['COMUNE'],
                'codice_catastale': row['COD_CATASTO'],
                'provincia_id': provincia,
                'citta_metropolitana_id': citta,
                'suppressed': True,
            }
            self.salva(comune, valori, '%06d %s' % (codice, row['COMUNE']))
