# Django Comuni Italiani
### Applicazione Django per gestire comuni, province e regioni

----

Questa applicazione django contiene lo stretto necessario per gestire le entità topografiche italiane (regioni, province, città metropolitane, comuni) importate dai dati pubblici dell'istat reperibili al link <a href="http://www.istat.it/it/archivio/6789" target="_blank">http://www.istat.it/it/archivio/6789</a>

----

### Requisiti e installazione

I requiti sono i seguenti:

 - Python 3.6+
 - Django 3.2+

Le novità e le note di compatibilità tra le versioni sono nel [CHANGELOG](CHANGELOG.md).

Per l'installazione potete utilizzare pip:

```bash

pip install django-comuni-italiani

```

Oppure prendere l'ultima versione da github <a href="https://github.com/kbytesys/django_comuni_italiani" target="_blank">https://github.com/kbytesys/django_comuni_italiani</a>
ed eseguire il classico:

```bash

./setup.py install

```

Nella configurazione di django aggiungi l'applicazione dove ti è più conveniente:

```python

INSTALLED_APPS = (
    ...
    'comuni_italiani',
    ...
)

```

L'app dispone di alcune viste per chiamate ajax e alto, dovrete dunque aggiungere gli url a quelli del vostro
progetto:

```python

urlpatterns = [
    ...
    url(r'^comuni_italiani/', include('comuni_italiani.urls', namespace='comuni_italiani')),
    ...
]

```

In Django 2:
```python

from django.urls import path, include

urlpatterns = [
    ...
    path('comuni_italiani/', include('comuni_italiani.urls', namespace='comuni_italiani')),
    ...
]

```

Un dump dei dati più aggiornati al momento del rilascio (attivi e soppressi) è distribuito sotto forma di fixture.
Esso può essere caricato con il seguente comando:

```bash

./manage.py loaddata --app comuni_italiani comuni_italiani.json

```

**Attenzione:** caricate la fixture solo su un'installazione nuova. Se avete già i dati nel database usate il comando
`aggiorna_comuni` (vedi sotto): gli id dei comuni sono autogenerati e caricare la fixture sopra dati esistenti
potrebbe sovrascrivere i comuni sbagliati.

### Chiamate ajax/json
L'app vi fornisce alcune chiamate per l'elenco e la ricerca delle diverse entità attraverso json/ajax.

Troverete la documentazione completa nel <a href="https://github.com/kbytesys/django_comuni_italiani/wiki/ChiamateJsonAjax" target="_blank">wiki</a>.

### Supporto django-autocomplete-light
Se utilizzate django-autocomplete-light potete facilmente aggiungere le definizioni per il completamento automatico aggiungendo
la seguente app tra quelle installate:

```python
INSTALLED_APPS = (
    ...
    'comuni_italiani',
    'comuni_italiani.autocomplete',
    ...
)
```

Ovviamente dovete aver aggiunto autocomplete light seguendo la documentazione che troverete  <a href="https://github.com/yourlabs/django-autocomplete-light">qui</a>.

Gli URL a disposizione per l'autocompletamento sono i seguenti:

*  `regione-autocomplete`
*  `provincia-autocomplete`
*  `cittametropolitana-autocomplete`
*  `comune-autocomplete`

Supportano il _forward_ (filtro selezionando oggetto padre, es. regione => provincia) tutti tranne regione-autocomplete.

Questi URL mostrano solo gli oggetti attivi. Per ognuno esistono anche le varianti con tutti gli oggetti (attivi e
soppressi) e con i soli soppressi, che supportano lo stesso _forward_. Nei risultati gli oggetti soppressi sono
indicati con "(soppresso)".

| Solo attivi | Tutti | Solo soppressi |
|---|---|---|
| `regione-autocomplete` | `regione-all-autocomplete` | `regione-suppressed-autocomplete` |
| `provincia-autocomplete` | `provincia-all-autocomplete` | `provincia-suppressed-autocomplete` |
| `cittametropolitana-autocomplete` | `cittametropolitana-all-autocomplete` | `cittametropolitana-suppressed-autocomplete` |
| `comune-autocomplete` | `comune-all-autocomplete` | `comune-suppressed-autocomplete` |

#### Campi per i form
L'autocompletamento decide solo cosa mostrare: la validazione la fa il campo del form, che di default accetta solo
gli oggetti attivi. Se usate il widget di `comune-all-autocomplete` con un campo normale, un comune soppresso verrà
mostrato ma rifiutato come "scelta non valida".

Per questo l'app mette a disposizione dei campi che usano lo stesso manager sia per il widget sia per la validazione:
`RegioneAutocompleteField`, `ProvinciaAutocompleteField`, `CittaMetropolitanaAutocompleteField` e
`ComuneAutocompleteField`. Il parametro `manager` può valere `'objects'` (solo attivi, default), `'all_objects'`
(tutti) o `'suppressed_objects'` (solo soppressi); `forward` viene passato al widget. Se avete incluso gli url
dell'autocompletamento con un namespace, indicatelo con il parametro `namespace` oppure, per tutti i campi, con
l'impostazione `COMUNI_ITALIANI_AUTOCOMPLETE_NAMESPACE`.

```python
from comuni_italiani.autocomplete.fields import ComuneAutocompleteField

class AnagraficaForm(forms.ModelForm):
    # accetta anche i comuni soppressi, es. per un luogo di nascita
    citta = ComuneAutocompleteField(manager='all_objects')
```

### Un esempio

Model con _ForeignKey_ ad un comune e un form con `django-autocomplete-light`:

```python
# models.py

class Anagrafica(models.Model):
    nome = models.CharField(max_length=32)
    email = models.EmailField()
    citta = models.ForeignKey(
        'comuni_italiani.Comune', on_delete=models.PROTECT
    )

```

```python
# urls.py

from django.urls import path, include

urlpatterns = [
	# i tuoi url, es. admin
	path('admin/', admin.site.urls),
	# includi gli URLs per l'autocompletamento
	path('ac/comuni/', include('comuni_italiani.autocomplete.urls')),
]
```

```python
# forms.py

from django import forms
from comuni_italiani.autocomplete.fields import ComuneAutocompleteField
from . import models


class AnagraficaForm(forms.ModelForm):
    citta = ComuneAutocompleteField()

    class Meta:
        model = models.Anagrafica
        fields = ('__all__')
```

In alternativa potete usare direttamente il widget di `django-autocomplete-light`
(`widgets = {'citta': autocomplete.ModelSelect2(url='comune-autocomplete')}`), ricordando che con le varianti
"tutti" o "soppressi" dovete impostare anche il `queryset` del campo (es. `Comune.all_objects.all()`).

Potete verificarne il funzionamento nell'admin:

```python
# admin.py

from django.contrib import admin
from . import models
from . import forms


@admin.register(models.Anagrafica)
class AnagraficaAdmin(admin.ModelAdmin):
    form = forms.AnagraficaForm
```


### Entità soppresse
Tutti i modelli (`Regione`, `CittaMetropolitana`, `Provincia`, `Comune`) hanno il campo booleano `suppressed`
(default `False`) che indica se l'entità è stata soppressa/cessata. Ogni modello mette a disposizione tre manager:

```python
Comune.objects.all()             # solo i comuni attivi (manager di default)
Comune.all_objects.all()         # tutti i comuni, attivi e soppressi
Comune.suppressed_objects.all()  # solo i comuni soppressi
```

Poiché `objects` è il manager di default, i soppressi sono esclusi anche da relazioni inverse
(`provincia.comune_set`), form, autocompletamento e chiamate json. L'admin invece mostra tutti i record, filtrabili
per `suppressed`. L'accesso diretto ad una foreign key (es. `anagrafica.citta`) funziona anche se il comune è soppresso.

Alcune accortezze:

 - Per un backup completo usate `./manage.py dumpdata --all comuni_italiani`: senza `--all` i soppressi non vengono esportati.
 - Se un vostro modello punta ad un comune poi soppresso, il form di modifica lo considererà una scelta non valida.
 Se volete permetterlo, allargate il queryset del campo:

```python
class AnagraficaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['citta'].queryset = Comune.all_objects.all()
```

### Aggiornamento dei dati
Regioni, province, città metropolitane e comuni, sia attivi che soppressi, si aggiornano con un unico comando che
scarica i dati dalle API [SITUAS](https://situas.istat.it) dell'Istat:

```bash

./manage.py aggiorna_comuni

```

Opzioni:

 - `--verbose`: scrive il dettaglio dell'importazione (creazioni, modifiche con valore vecchio e nuovo, ricodifiche,
 soppressioni) e un riepilogo finale. Senza questa opzione vengono scritti solo gli errori.
 - `--dry-run`: esegue tutto senza salvare nulla, utile insieme a `--verbose` per vedere cosa cambierebbe.
 - `--data-da GG/MM/AAAA` e `--data-a GG/MM/AAAA`: intervallo delle soppressioni da importare (default dal 17/03/1861
 ad oggi). L'elenco dei comuni attivi è sempre quello di oggi: non è possibile riportare il database ad una data passata.

Il comando non richiede alcun input, può quindi essere eseguito da cron. In caso di errori termina con un exit code
diverso da zero; se non riesce a scaricare i dati non modifica il database.

```
# ogni lunedì alle 3:00
0 3 * * 1 /percorso/venv/bin/python /percorso/progetto/manage.py aggiorna_comuni
```

#### Come vengono gestiti i codici
 - **Codice Istat del comune**: è formato dal codice della provincia e da un progressivo, quindi cambia quando un
 comune cambia provincia (es. tutti i comuni sardi con la riforma del 2025) e può essere riassegnato dopo una
 soppressione. **Codice catastale**: è quello del codice fiscale, resta uguale anche se il comune cambia provincia.
 - Nessuno dei due identifica un comune per sempre: per questo i comuni hanno un id autogenerato, che è ciò a cui
 puntano le vostre foreign key, e il comando fa in modo che resti lo stesso.
 - Un comune attivo viene riconosciuto **prima dal codice catastale** e solo dopo dal codice Istat. Se il codice è
 cambiato, il comune viene **ricodificato sulla stessa riga**.
 - Nel database c'è **una riga per codice Istat**, con l'ultimo stato noto. Se un codice soppresso è oggi usato da un
 comune attivo, vale il comune attivo.
 - Se il codice di un comune attivo è occupato da una riga che non corrisponde più a nessun comune attivo (per esempio
 la vecchia incarnazione soppressa di un comune che riprende un codice avuto in passato), quella riga viene eliminata
 solo se nessun dato vi fa riferimento. Altrimenti il comando segnala un errore e non modifica quel comune: serve un
 intervento manuale. Lo stesso vale se nel database ci sono più comuni attivi con lo stesso codice catastale.
 - Il database è allineato all'Istat ad ogni esecuzione: le modifiche fatte a mano (per esempio dall'admin) vengono
 sovrascritte. In particolare non modificate il codice catastale dei comuni, perché è ciò che permette di
 riconoscerli quando cambiano codice.
 - Una provincia resta attiva finché almeno un comune attivo usa il suo codice. Per esempio Torino (001) resta attiva
 anche se dal 2015 per l'Istat è stata sostituita dalla città metropolitana (201), che è presente tra le città
 metropolitane. Lo stesso vale per le ex province del Friuli-Venezia Giulia e per i liberi consorzi siciliani.
 - Le regioni soppresse sono i compartimenti storici precedenti al 1948 (es. "Venezia Giulia"). Le province cedute
 a stato estero nel 1947 (Fiume, Pola, Zara) sono collegate al compartimento "Venezia Giulia".
 - Popolazione legale (ultimo censimento), superficie e altitudine vengono aggiornate per i comuni attivi.

#### Comandi deprecati
I comandi `import_regioni_prov` e `import_comuni` sono ancora presenti per compatibilità, ma sono deprecati: leggono
il vecchio formato csv dell'Istat e non gestiscono i soppressi. Usate `aggiorna_comuni`. Per non rovinare i dati,
si rifiutano di partire se il database contiene oggetti soppressi, cioè dopo aver usato `aggiorna_comuni` o caricato
la nuova fixture.

```bash

./manage.py import_regioni_prov
./manage.py import_comuni

```

L'aggiornamento dei comuni con questi comandi funziona così:

 - Durante l'aggiornamento se viene rilevato un comune con lo stesso codice istat, ma con diverso nome, verrà richiesto
 di confermare l'aggiornamento o saltare il record. Ciò evita probabili inconvenienti durante le (rare)
 rinumerazioni dei comuni in una provincia.

 - Al termine dell'aggiornamento vengono elencati i comuni presenti del db, ma assenti nel csv. Ciò vi aiuterà a rilevare
 i comuni eliminati/abrogati/accorpati

 - Al termine dell'aggiornamento verranno elencati i comuni *omonimi*. Attualmente sono presenti 8 nomi di comune uguali
 per un totale di 16 comuni

In ogni caso sarà vostro compito fare i dovuti aggiustamenti.

### FAQ
**A quando risale l'ultimo aggiornamento dei dati?**<br>
La fixture inclusa contiene i dati Istat aggiornati al 4 novembre 2026. Per aggiornarli usate `aggiorna_comuni`.

**Perchè documentazione e codice sorgente sono in Italiano?**<br>
Questa appliazione ha uno scopo intimamente riservato al "mercato" italiano. In genere se si ha la necessità
di utilizzare luoghi e lingue diverse consiglio l'uso di <a href="https://github.com/yourlabs/django-cities-light" target="_blank">django-cities-light</a> oppure di <a href="https://github.com/coderholic/django-cities" target="_blank">django-cities</a>

**Posso aggiornare i comuni eliminandoli e reimportando i dati da zero?**<br>
Assumento che tu possa farlo sbloccando temporaneamente le foreign keys, non è una buona idea. Mentre province e regioni hanno sempre lo stesso codice istat,
il codice istat di un comune può cambiare. Per questo motivo i comuni hanno una chiave numerica autogenerata che potrebbe non essere coerente tra un'importazione
e l'altra.

**Nei nuovi dati non trovo più la superfice e l'altitudine dei comuni!**<br>
Nei csv del 2016 l'Istat aveva tolto quelle informazioni; il comando `aggiorna_comuni` le recupera dalle API SITUAS.
I comuni soppressi non hanno popolazione, superficie e altitudine.

### TODO
 - Form temizzabili per selezionare una provincia da regione e un comune da provincia
(se si usa [django-autocomplete-light](https://github.com/yourlabs/django-autocomplete-light) non c'è bisogno).
