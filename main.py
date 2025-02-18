import datetime
from copy import deepcopy
import pytz

class GameBackend:
    def __init__(self):

        # Code: ogni elemento è un dizionario con "id" e "arrival" (orario d'arrivo)
        self.queue_couples = []  # Es. [{'id': 'GIALLO-01', 'arrival': datetime}, ...]
        self.queue_singles = []  # Es. [{'id': 'BLU-01', 'arrival': datetime}, ...]
        self.queue_charlie = []  # Es. [{'id': 'VERDE-01', 'arrival': datetime}, ...]
        
        # Storico dei tempi (in minuti) registrati per aggiornamento dinamico
        self.couple_history_mid = []    # Tempo dal Pulsante 1 al Pulsante 3 (liberazione di ALFA)
        self.couple_history_total = []  # Tempo totale per il game coppia (fino alla liberazione di BRAVO)
        self.single_history = []        # Tempo totale per il game singolo (durata in cui ALFA è occupata)
        
        # Aggiungi storico tempi per Charlie
        self.charlie_history = []        # Tempo totale per il game charlie
        
        # Valori indicativi (default) iniziali (in minuti)
        self.default_T_mid = 2.0
        self.default_T_total = 5.0
        self.default_T_single = 2.0
        self.default_T_charlie = 3.0    # Tempo default per Charlie: 3 minuti
        
        # Tempi attuali: partono dai valori indicativi e verranno aggiornati
        self.T_mid = self.default_T_mid
        self.T_total = self.default_T_total
        self.T_single = self.default_T_single
        self.T_charlie = self.default_T_charlie  # Tempo attuale per Charlie
        
        # Stato iniziale delle piste: disponibilità immediata
        self.rome_tz = pytz.timezone('Europe/Rome')
        
        # Inizializza i datetime con il fuso orario
        now = self.get_current_time()
        self.ALFA_next_available = now
        self.BRAVO_next_available = now

        # Aggiungi variabile per il prossimo giocatore
        self.next_player = None
        self.next_player_locked = False

        self.couple_in_bravo = False  # Flag per tracciare se c'è una coppia in BRAVO
        self.couple_in_alfa = False   # Flag per tracciare se c'è una coppia in ALFA
        self.single_in_alfa = False   # Flag per tracciare se c'è un singolo in ALFA
        self.third_button_pressed = False  # Nuovo flag per tracciare se è stato premuto il pulsante metà percorso

        self.skipped_couples = []  # Lista per le coppie skippate
        self.skipped_singles = []  # Lista per i singoli skippati

        # Aggiunta variabili per la pista Charlie
        self.skipped_charlie = []
        self.CHARLIE_next_available = self.get_current_time()
        self.player_in_charlie = False
        self.next_charlie_player = None
        self.next_charlie_player_locked = False

        # Inizializza le code con i nuovi formati ID
        for i in range(1, 11):
            couple_id = f"GIALLO-{i:02d}"
            single_id = f"BLU-{i:02d}"
            charlie_id = f"VERDE-{i:02d}"
            
            self.add_couple(couple_id)
            self.add_single(single_id)
            self.add_charlie_player(charlie_id)

    def add_charlie_player(self, player_id):
        """Aggiunge un giocatore alla coda Charlie"""
        if not any(p['id'] == player_id for p in self.queue_charlie):
            self.queue_charlie.append({
                'id': player_id,
                'timestamp': self.get_current_time()
            })
            if not self.next_charlie_player and not self.next_charlie_player_locked:
                self.next_charlie_player = player_id
                self.next_charlie_player_locked = True

    def record_couple_game(self, mid_time, total_time):
        """
        Registra i tempi (in minuti) relativi a un game coppia:
          - mid_time: tempo dal Pulsante 1 all'attivazione del Pulsante 3
          - total_time: tempo totale dal Pulsante 1 (avvio) allo stop (liberazione di BRAVO)
        Dopo la registrazione, aggiorna i tempi medi.
        """
        self.couple_history_mid.append(mid_time)
        self.couple_history_total.append(total_time)
        self.update_averages()

    def record_single_game(self, game_time):
        """
        Registra il tempo (in minuti) relativo a un game singolo (durata in cui ALFA è occupata).
        Dopo la registrazione, aggiorna i tempi medi.
        """
        self.single_history.append(game_time)
        self.update_averages()
        self.single_in_alfa = False 

    def record_charlie_game(self, game_time):
        """
        Registra il tempo (in minuti) relativo a un game charlie.
        Dopo la registrazione, aggiorna i tempi medi.
        """
        self.charlie_history.append(game_time)
        self.update_averages()
        
    def format_time(self, time_in_minutes):
        """Formatta il tempo in minuti e secondi"""
        minutes = int(time_in_minutes)
        seconds = int((time_in_minutes - minutes) * 60)
        return f"{minutes}m {seconds}s"
    def get_leaderboard(self):
        """
        Restituisce la classifica dei giocatori in base ai tempi medi di gioco.
        """
        couple_avg_times = [(f"COMPLETATO-{i+1}", self.format_time(time)) for i, time in enumerate(self.couple_history_total)]
        single_avg_times = [(f"COMPLETATO-{i+1}", self.format_time(time)) for i, time in enumerate(self.single_history)]
        charlie_avg_times = [(f"COMPLETATO-{i+1}", self.format_time(time)) for i, time in enumerate(self.charlie_history)]

        return {
            'couples': couple_avg_times,
            'singles': single_avg_times,
            'charlie': charlie_avg_times
        }

    def get_current_time(self):
        """Ottiene l'ora corrente nel fuso orario di Roma"""
        return datetime.datetime.now(self.rome_tz)

    def localize_time(self, dt):
        """Assicura che un datetime abbia il fuso orario di Roma"""
        if dt.tzinfo is None:
            return self.rome_tz.localize(dt)
        return dt
    
    

    def update_averages(self):
        """
        Aggiorna i tempi medi in base allo storico.
        Se sono stati registrati almeno 5 game, si calcola la media;
        altrimenti si usano i valori indicativi.
        """
        if len(self.couple_history_mid) >= 5:
            self.T_mid = sum(self.couple_history_mid) / len(self.couple_history_mid)
        else:
            self.T_mid = self.default_T_mid

        if len(self.couple_history_total) >= 5:
            self.T_total = sum(self.couple_history_total) / len(self.couple_history_total)
        else:
            self.T_total = self.default_T_total

        if len(self.single_history) >= 5:
            self.T_single = sum(self.single_history) / len(self.single_history)
        else:
            self.T_single = self.default_T_single

        # Aggiungi calcolo media per Charlie
        if len(self.charlie_history) >= 5:
            self.T_charlie = sum(self.charlie_history) / len(self.charlie_history)
        else:
            self.T_charlie = self.default_T_charlie

    def add_couple(self, couple_id):
        """Aggiunge una coppia alla coda con timestamp di Roma"""
        self.queue_couples.append({
            'id': couple_id,
            'arrival': self.get_current_time()
        })

    def add_single(self, single_id):
        """Aggiunge un singolo alla coda con timestamp di Roma"""
        self.queue_singles.append({
            'id': single_id,
            'arrival': self.get_current_time()
        })

    def record_couple_game(self, mid_time, total_time):
        """
        Registra i tempi (in minuti) relativi a un game coppia:
          - mid_time: tempo dal Pulsante 1 all'attivazione del Pulsante 3
          - total_time: tempo totale dal Pulsante 1 (avvio) allo stop (liberazione di BRAVO)
        Dopo la registrazione, aggiorna i tempi medi.
        """
        self.couple_history_mid.append(mid_time)
        self.couple_history_total.append(total_time)
        self.update_averages()

    def record_single_game(self, game_time):
        """
        Registra il tempo (in minuti) relativo a un game singolo (durata in cui ALFA è occupata).
        Dopo la registrazione, aggiorna i tempi medi.
        """
        self.single_history.append(game_time)
        self.update_averages()

    def simulate_schedule(self):
        """
        Simula la pianificazione degli ingressi a partire dallo stato attuale, considerando:
          - Un game (coppia o singolo) parte sempre da ALFA.
          - Se ALFA e BRAVO sono libere (ossia, BRAVO è libera al momento in cui ALFA diventa disponibile),
            il prossimo ingresso deve essere una coppia (se in coda).
          - Se ALFA è libera ma BRAVO non lo è, solo i singoli possono iniziare.
          - Notare che il tempo di un game singolo (T_single) potrebbe essere maggiore della finestra
            di tempo compresa tra il liberamento di ALFA (da un game coppia) e la fine dello stesso game coppia.
            Questo verrà preso in considerazione aggiornando l'orario in cui ALFA diventa disponibile.
          
        La funzione restituisce un dizionario in cui, per ogni elemento in coda (id),
        viene associato l'orario stimato d'ingresso.
        """
        now = self.get_current_time()
        # Il tempo di partenza della simulazione è il momento in cui ALFA è (o diventerà) disponibile
        self.ALFA_next_available = self.localize_time(self.ALFA_next_available)
        sim_time = max(now, self.ALFA_next_available)
        
        # Assicurati che BRAVO_next_available abbia il fuso orario
        self.BRAVO_next_available = self.localize_time(self.BRAVO_next_available)
        BRAVO_avail = self.BRAVO_next_available if self.BRAVO_next_available > sim_time else sim_time

        # Creiamo dei timedelta dai tempi medi (in minuti)
        dt_mid = datetime.timedelta(minutes=self.T_mid)
        dt_total = datetime.timedelta(minutes=self.T_total)
        dt_single = datetime.timedelta(minutes=self.T_single)

        # Facciamo una copia delle code in modo da non modificare lo stato reale
        couples = deepcopy(self.queue_couples)
        singles = deepcopy(self.queue_singles)

        estimated_times = {}  # key: id, value: orario stimato (datetime)

        # Simulazione: continuiamo finché rimane almeno un elemento in una delle code
        while couples or singles:
            # Se, al momento in cui ALFA è libera, anche BRAVO lo è (o è già stata liberata),
            # allora possiamo avviare un game coppia se in coda.
            if BRAVO_avail <= sim_time:
                if couples:
                    item = couples.pop(0)
                    start_time = sim_time
                    estimated_times[item['id']] = start_time
                    # Quando parte un game coppia:
                    # - ALFA è occupata fino a T_mid (dopo di che si libera)
                    # - BRAVO resta occupata fino a T_total
                    sim_time = start_time + dt_mid
                    BRAVO_avail = start_time + dt_total
                    continue
                else:
                    # Se non ci sono coppie in coda, ma ci sono singoli, serviamo un singolo
                    if singles:
                        item = singles.pop(0)
                        start_time = sim_time
                        estimated_times[item['id']] = start_time
                        # Nota: il game singolo occupa ALFA per T_single, 
                        # che potrebbe essere maggiore della finestra tra liberazione di ALFA e fine di un game coppia.
                        sim_time = start_time + dt_single
                        # BRAVO non viene modificata in questo caso
                        continue
                    else:
                        break  # Non ci sono altri elementi in coda
            else:
                # Se ALFA è libera ma BRAVO è ancora occupata, solo i singoli possono iniziare
                if singles:
                    item = singles.pop(0)
                    start_time = sim_time
                    estimated_times[item['id']] = start_time
                    sim_time = start_time + dt_single
                    continue
                else:
                    # Se non ci sono singoli, dobbiamo attendere che BRAVO diventi libera
                    sim_time = BRAVO_avail
                    continue

        return estimated_times

    def get_waiting_board(self):
        now = self.get_current_time()
        
        # Calcola i tempi stimati di ingresso
        est = self.simulate_schedule()
        
        # Se non abbiamo un prossimo giocatore bloccato, controlliamo se dobbiamo assegnarne uno
        if not self.next_player_locked:
            # Se c'è una coppia in BRAVO e un singolo in ALFA, diamo priorità alle coppie
            if self.couple_in_bravo and self.single_in_alfa and self.queue_couples:
                # Assegna la prima coppia in coda come prossimo
                self.next_player = self.queue_couples[0]['id']
                self.next_player_locked = True
            else:
                # Logica normale per l'assegnazione del prossimo
                for queue_item in self.queue_couples + self.queue_singles:
                    estimated_time = est.get(queue_item['id'])
                    if estimated_time:
                        minutes_to_entry = (estimated_time - now).total_seconds() / 60
                        if minutes_to_entry <= 2:
                            self.next_player = queue_item['id']
                            self.next_player_locked = True
                            break

        couples_board = []
        for idx, item in enumerate(self.queue_couples):
            estimated = est.get(item['id'], None)
            # Non mostrare il tempo stimato se è il prossimo giocatore
            if item['id'] == self.next_player:
                couples_board.append((idx + 1, item['id'], "PROSSIMO INGRESSO"))
            else:
                couples_board.append((idx + 1, item['id'], estimated))

        singles_board = []
        for idx, item in enumerate(self.queue_singles):
            estimated = est.get(item['id'], None)
            # Non mostrare il tempo stimato se è il prossimo giocatore
            if item['id'] == self.next_player:
                singles_board.append((idx + 1, item['id'], "PROSSIMO INGRESSO"))
            else:
                singles_board.append((idx + 1, item['id'], estimated))

        # Formatta la board di Charlie con i tempi stimati
        charlie_board = []
        for idx, item in enumerate(self.queue_charlie):
            if item['id'] == self.next_charlie_player:
                charlie_board.append((idx + 1, item['id'], "PROSSIMO INGRESSO"))
            else:
                # Calcola il tempo stimato in base al numero di giocatori davanti
                # e al tempo medio di gioco
                players_ahead = idx
                estimated_time = now + datetime.timedelta(minutes=self.T_charlie * players_ahead)
                charlie_board.append((idx + 1, item['id'], estimated_time))

        return couples_board, singles_board, charlie_board


    def start_game(self, is_couple=True):
        """Avvia un nuovo game e rimuove il giocatore dalla coda"""
        if is_couple:
            if self.queue_couples:
                player = self.queue_couples.pop(0)
                self.couple_in_bravo = True
                self.couple_in_alfa = True
                self.single_in_alfa = False
                self.third_button_pressed = False  # Reset del flag all'inizio di un nuovo game coppia
                if player['id'] == self.next_player:
                    self.next_player = None
                    self.next_player_locked = False
        else:  # Singolo
            if self.queue_singles:
                player = self.queue_singles.pop(0)
                self.single_in_alfa = True    # Imposta il flag
                self.couple_in_alfa = False
            if player['id'] == self.next_player:
                self.next_player = None
                self.next_player_locked = False

    def button_third_pressed(self):
        """Gestisce la pressione del pulsante metà percorso"""
        self.couple_in_bravo = True
        self.couple_in_alfa = False
        self.third_button_pressed = True
        self.ALFA_next_available = self.get_current_time()

    def can_stop_couple(self):
        """Verifica se una coppia può fermarsi"""
        return self.third_button_pressed

    def skip_player(self, player_id):
        """Sposta un giocatore nella lista degli skippati"""
        if player_id.startswith('G'):
            player = next((c for c in self.queue_couples if c['id'] == player_id), None)
            if player:
                self.queue_couples = [c for c in self.queue_couples if c['id'] != player_id]
                self.skipped_couples.append(player)
        elif player_id.startswith('B'):
            player = next((s for s in self.queue_singles if s['id'] == player_id), None)
            if player:
                self.queue_singles = [s for s in self.queue_singles if s['id'] != player_id]
                self.skipped_singles.append(player)

    def restore_skipped(self, player_id):
        """Ripristina un giocatore skippato dopo il prossimo ingresso se presente"""
        if player_id.startswith('G'):
            player = next((c for c in self.skipped_couples if c['id'] == player_id), None)
            if player:
                self.skipped_couples = [c for c in self.skipped_couples if c['id'] != player_id]
                # Se c'è un prossimo ingresso che è una coppia, inserisci dopo di esso
                if self.next_player and self.next_player.startswith('G'):
                    next_index = next((i for i, c in enumerate(self.queue_couples) 
                                     if c['id'] == self.next_player), 0)
                    self.queue_couples.insert(next_index + 1, player)
                else:
                    self.queue_couples.insert(0, player)
        elif player_id.startswith('B'):
            player = next((s for s in self.skipped_singles if s['id'] == player_id), None)
            if player:
                self.skipped_singles = [s for s in self.skipped_singles if s['id'] != player_id]
                # Se c'è un prossimo ingresso che è un singolo, inserisci dopo di esso
                if self.next_player and self.next_player.startswith('B'):
                    next_index = next((i for i, s in enumerate(self.queue_singles) 
                                     if s['id'] == self.next_player), 0)
                    self.queue_singles.insert(next_index + 1, player)
                else:
                    self.queue_singles.insert(0, player)

        # Gestione giocatori Charlie
        player = next((p for p in self.skipped_charlie if p['id'] == player_id), None)
        if player:
            self.skipped_charlie.remove(player)
            self.add_charlie_player(player_id)

    def add_charlie_player(self, player_id):
        """Aggiunge un giocatore alla coda Charlie"""
        if not any(p['id'] == player_id for p in self.queue_charlie):
            self.queue_charlie.append({
                'id': player_id,
                'timestamp': self.get_current_time()
            })
            if not self.next_charlie_player and not self.next_charlie_player_locked:
                self.next_charlie_player = player_id
                self.next_charlie_player_locked = True

    def start_charlie_game(self):
        """Avvia un gioco sulla pista Charlie"""
        if self.next_charlie_player:
            self.player_in_charlie = True
            # Rimuovi il giocatore dalla coda
            self.queue_charlie = [p for p in self.queue_charlie if p['id'] != self.next_charlie_player]
            
            # Imposta il prossimo giocatore
            if self.queue_charlie:
                self.next_charlie_player = self.queue_charlie[0]['id']
                self.next_charlie_player_locked = True
            else:
                self.next_charlie_player = None
                self.next_charlie_player_locked = False

    def record_charlie_game(self, game_time):
        """Registra il tempo (in minuti) relativo a un game charlie"""
        self.charlie_history.append(game_time)
        self.update_averages()

    def skip_charlie_player(self, player_id):
        """Sposta un giocatore dalla coda Charlie alla lista degli skippati"""
        player = next((p for p in self.queue_charlie if p['id'] == player_id), None)
        if player:
            self.skipped_charlie.append(player)
            self.queue_charlie = [p for p in self.queue_charlie if p['id'] != player_id]

# ---------------------------
# Esempio d'uso

if __name__ == '__main__':
    backend = GameBackend()
    

    # Aggiungiamo alcune coppie e alcuni singoli in coda
    backend.add_couple("GIALLO-01")
    backend.add_single("BLU-01")
    backend.add_couple("GIALLO-02")
    backend.add_single("BLU-02")
    backend.add_couple("GIALLO-03")
    backend.add_single("BLU-03")

    # Assicuriamoci che, al momento, non ci sia un game in corso
    now = datetime.datetime.now()
    backend.ALFA_next_available = now
    backend.BRAVO_next_available = now

    # Otteniamo il tabellone d'attesa
    couples_board, singles_board, charlie_board = backend.get_waiting_board()

    print("Tabellone Coppie (Gialli):")
    for pos, cid, time_est in couples_board:
      time_str = time_est.strftime('%H:%M:%S') if isinstance(time_est, datetime.datetime) else time_est if time_est else 'N/D'
    print(f"{pos}. {cid} - Ingresso stimato: {time_str}")

    print("\nTabellone Singoli (Blu):")
    for pos, sid, time_est in singles_board:
      time_str = time_est.strftime('%H:%M:%S') if isinstance(time_est, datetime.datetime) else time_est if time_est else 'N/D'
    print(f"{pos}. {cid} - Ingresso stimato: {time_str}")

    print("\nTabellone Charlie (Verde):")
    for pos, cid, time_est in charlie_board:
       time_str = time_est.strftime('%H:%M:%S') if isinstance(time_est, datetime.datetime) else time_est if time_est else 'N/D'
    print(f"{pos}. {cid} - Ingresso stimato: {time_str}")
