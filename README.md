# Progetto Game Backend e Dashboard

Questo progetto è un sistema di gestione di giochi che utilizza code per gestire le partite e una dashboard per monitorare lo stato.  
Il progetto comprende due file principali:

- `main.py`: Contiene la logica del backend, la gestione delle code di giocatori, la simulazione degli ingressi e la registrazione dei giochi.
- `app.py`: Implementa un server web basato su Flask che espone diverse rotte per interagire con il backend e visualizzare la dashboard.

## Prerequisiti

Assicurati di avere installato:

- Python 3.7 o versione successiva
- pip

## Installazione delle Dipendenze

È consigliato usare un virtual environment per isolare le dipendenze. Ad esempio:

## Creazione del virtual environment

python -m venv venv

## Attivazione del virtual environment (Windows)

venv\Scripts\activate

## Attivazione del virtual environment (Linux/macOS)

source venv/bin/activate

## Installa le dipendenze richieste con il seguente comando:

```bash
pip install flask pytz mysql-connector
```

## Avvio del Progetto in Locale

1. **Clona o Scarica il Progetto**  
   Assicurati di avere i file `main.py` e `app.py` nella stessa directory.

2. **Configura le Code (facoltativo)**  
   Nel file `app.py` è presente la funzione `initialize_queues()` per svuotare e, eventualmente, popolare le code.  
   Puoi modificare questa funzione se desideri pre-caricare delle code di giocatori.

3. **Avvia l'Applicazione Flask**  
   Esegui il comando seguente dalla directory del progetto:

   ```bash
   python app.py
   ```

4. **Accedi all'Applicazione nel Browser**  
   Dopo aver avviato il server, apri il browser e naviga all'URL:

   ```
   http://localhost:2000/
   ```

   Da qui potrai accedere alla dashboard e alle altre pagine di controllo (es. `/controls/cassa`, `/controls/couple`, `/controls/single`, `/controls/charlie`).



## Rotte Principali

- `/`  
  Reindirizza automaticamente alla dashboard.

- `/dashboard`  
  Visualizza la dashboard principale.

- `/controls/cassa`  
  Pagina per i controlli relativi alla cassa.

- `/controls/couple`  
  Pagina per la gestione dei controlli delle coppie.

- `/controls/single`  
  Pagina per la gestione dei controlli dei singoli.

- `/controls/charlie`  
  Pagina per i controlli della pista Charlie.

- `/queue`  
  Pagina per controllare tutte le piste (ideata per i giocatori).

- `/qrqueue`  
  Pagina di visualizzazione del qrcode per accedere alla queue.

- Altre rotte (es. `/add_couple`, `/add_single`, `/skip_charlie_player`, `/restore_skipped`, ecc.)  
  Permettono di gestire l'aggiunta di giocatori, saltare un giocatore in coda, ripristinare giocatori "skippati", ottenere il tabellone d'attesa, e altro.

## Debug e Sviluppo

- L'applicazione Flask è avviata in modalità debug (`debug=True` in `app.py`); ciò permette il live reload e la visualizzazione dei log in console per agevolare lo sviluppo.
- Ogni modifica apportata al codice verrà automaticamente rilevata (se si è in modalità debug). In caso di problemi, controlla i log della console per ulteriori dettagli.

## Note Tecniche

- Il progetto utilizza la libreria `pytz` per la gestione del fuso orario di Roma.
- La logica di aggiornamento del tabellone d'attesa e la gestione delle code sono implementate nella classe `GameBackend` definita in `main.py`.
- Il dizionario `player_names` in `GameBackend` viene utilizzato per memorizzare e recuperare i nomi dei giocatori associati ai loro ID.

## Conclusioni

Seguendo questi passaggi potrai far partire il progetto in locale e testare tutte le funzionalità fornite dall'interfaccia web e dal backend.  
Se dovessi riscontrare problemi, controlla attentamente la configurazione dell'ambiente e i log generati dal server.

Buon lavoro!
