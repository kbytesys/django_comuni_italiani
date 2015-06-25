# Django Comuni Italiani
### Applicazione Django per gestire comuni, province e regioni

----

Questa applicazione django contiene lo stretto necessario per gestire le entità topografiche italiane (regioni, province, città metropolitane, comuni) importate dai dati pubblici dell'istat reperibili al link <a href="http://www.istat.it/it/archivio/6789" target="_blank">http://www.istat.it/it/archivio/6789</a>

----

### Requisiti e installazione

I requiti sono i seguenti:

 - Python 3+
 - Django 1.7+

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

Un dump dei dati più aggiornati al momento del rilascio è distribuito sotto forma di fixture. Esso può essere caricato
con il seguente comando:

```bash

./manage.py loaddata --app comuni_italiani comuni_italiani.json

```

### Chiamate ajax/json
L'app vi fornisce alcune chiamate per l'elenco e la ricerca delle diverse entità attraverso json/ajax.

Troverete la documentazione completa nel <a href="https://github.com/kbytesys/django_comuni_italiani/wiki/ChiamateJsonAjax" target="_blank">wiki</a>.

### Aggiornamento dei dati
Purtroppo l'aggiornamento dei dati non è un'operazione semplice, soprattutto perché i tuoi dati contenuti nelle
applicazioni che svilupperai potrebbero essere legati a dati soggetti a cambiamenti (hanno abrogato una provincia? maledetti!)

```bash

./manage.py import_regioni_prov
./manage.py import_comuni

```

Entrambi i comandi possono accettare i file csv aggiornati presi dal sito dell'istat. Tuttavia se la loro struttura (o
anche semplicemente il nome della colonna) cambia, l'importazione potrebbe fallire.

Per l'aggiornamento delle province e regioni attualmente non viene eseguito alcun particolare controllo nel caso di rimozione,
in quanto è un'operazione delicata che deve essere gestita manualmente in base alle vostre basi dati.

L'aggiornamento dei comuni è più intelligente.

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
L'applicazione ha già inclusi i dati istat aggiornati al 30 gennaio 2015

**Perchè documentazione e codice sorgente sono in Italiano?**<br>
Questa appliazione ha uno scopo intimamente riservato al "mercato" italiano. In genere se si ha la necessità
di utilizzare luoghi e lingue diverse consiglio l'uso di <a href="https://github.com/yourlabs/django-cities-light" target="_blank">django-cities-light</a> oppure di <a href="https://github.com/coderholic/django-cities" target="_blank">django-cities</a>

**Posso aggiornare i comuni eliminandoli e reimportando i dati da zero?**<br>
Assumento che tu possa farlo sbloccando temporaneamente le foreign keys, non è una buona idea. Mentre province e regioni hanno sempre lo stesso codice istat,
il codice istat di un comune può cambiare. Per questo motivo i comuni hanno una chiave numerica autogenerata che potrebbe non essere coerente tra un'importazione
e l'altra.

### Changelog
??/??/???? 1.1.0 - Chiamate ajax/json per ricerca, aggiornamento dati istat<br>
18/06/2015 1.0.0 - Primo rilascio applicazione<br>
19/06/2015 1.0.1 - Correzioni documentazione, pulizia codice e disattivazione caricamento automatico fixtures

### TODO
 - Form temizzabili per selezionare una provincia da regione e un comune da provincia
