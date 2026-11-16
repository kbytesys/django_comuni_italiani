# Changelog

## 1.5.0

### Novità
 - Regioni, province, città metropolitane e comuni hanno il campo `suppressed` e tre manager: `objects` (solo attivi,
   manager di default), `all_objects` (tutti) e `suppressed_objects` (solo soppressi).
 - Nuovo comando `aggiorna_comuni`: aggiorna attivi e soppressi dalle API SITUAS dell'Istat, senza input interattivi
   (adatto a cron), con le opzioni `--verbose`, `--dry-run`, `--data-da` e `--data-a`.
 - La fixture `comuni_italiani.json` contiene i dati Istat aggiornati, compresi i soppressi dal 1861.
 - Popolazione legale (censimento 2021), superficie e altitudine sono di nuovo disponibili.
 - Autocomplete per tutti gli oggetti (`*-all-autocomplete`) e per i soli soppressi (`*-suppressed-autocomplete`).
 - Campi per i form (`ComuneAutocompleteField`, ecc.) che usano lo stesso manager per widget e validazione, con
   supporto agli url inclusi con un namespace (`COMUNI_ITALIANI_AUTOCOMPLETE_NAMESPACE`).
 - L'admin mostra anche gli oggetti soppressi, filtrabili per stato.

### Correzioni
 - L'admin registra `CittaMetropolitana` con il suo `CittaMetropolitanaAdmin`.
 - Il forward `regione` di `cittametropolitana-autocomplete` non genera più un errore.
 - Gli autocomplete di comuni e province non eseguono più una query per ogni risultato.

### Compatibilità
Dopo l'aggiornamento del pacchetto e `./manage.py migrate` non cambia nulla: tutti i dati esistenti risultano attivi.
I cambiamenti seguenti si vedono solo dopo aver eseguito `aggiorna_comuni` (o caricato la nuova fixture su
un'installazione nuova):

 - I comuni soppressi non compaiono più in `objects`, nelle relazioni inverse (`provincia.comune_set`), nei form,
   negli autocomplete e nelle chiamate json. Un vostro record che punta ad un comune soppresso resta valido e
   l'accesso diretto (`anagrafica.citta`) funziona, ma il form di modifica lo considera una scelta non valida: usate
   `queryset=Comune.all_objects.all()` sul campo o `ComuneAutocompleteField(manager='all_objects')`.
 - I comuni sardi hanno un nuovo codice Istat (riforma delle province del 2025). Il loro id non cambia, quindi le
   vostre foreign key restano valide, ma se avete salvato altrove il vecchio codice Istat dovete aggiornarlo.
 - La popolazione è quella del censimento 2021 invece del 2011.
 - `dumpdata` esporta solo gli oggetti attivi: per un backup completo usate `dumpdata --all`.
 - I comandi `import_regioni_prov` e `import_comuni` sono deprecati e si rifiutano di partire se il database contiene
   oggetti soppressi.
 - È richiesto Django 3.2 o successivo.
