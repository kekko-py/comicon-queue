import datetime
from copy import deepcopy
import pytz
from typing import List, Dict, TypedDict, Tuple, Optional, Union

class Player(TypedDict):
    id: str
    name: str

class Queue(TypedDict, total=False):
    id: str
    arrival: datetime.datetime
    name: str   # aggiunto come chiave opzionale

class GameBackend:
    def __init__(self) -> None:
        # Code: ogni elemento è un dizionario con "id" e "arrival" (orario d'arrivo)
        self.queue_couples: List[Queue] = []  # Es. [{'id': 'GIALLO-01', 'arrival': datetime}, ...]
        self.queue_singles: List[Queue] = []  # Es. [{'id': 'BLU-01', 'arrival': datetime}, ...]
        self.queue_charlie: List[Queue] = []  # Es. [{'id': 'VERDE-01', 'arrival': datetime}, ...]

        self.couples= []
        # Storico dei tempi (in minuti) registrati per aggiornamento dinamico
        self.couple_history_mid: List[float] = []    # Tempo dal Pulsante 1 al Pulsante 3 (liberazione di ALFA)
        self.couple_history_total: List[float] = []  # Tempo totale per il game coppia (fino alla liberazione di BRAVO)
        self.single_history: List[float] = []        # Tempo totale per il game singolo (durata in cui ALFA è occupata)
        self.charlie_history: List[float] = []       # Tempo totale per il game charlie

        # Valori indicativi (default) iniziali (in minuti)
        self.default_T_mid = 2.0
        self.default_T_total = 5.0
        self.default_T_single = 2.0
        self.default_T_charlie = 3.0

        # Tempi attuali: partono dai valori indicativi e verranno aggiornati
        self.T_mid = self.default_T_mid
        self.T_total = self.default_T_total
        self.T_single = self.default_T_single
        self.T_charlie = self.default_T_charlie

        # Giocatori attuali in pista
        self.current_player_alfa: Optional[Queue] = None
        self.current_player_bravo: Optional[Queue] = None
        self.current_player_charlie: Optional[Queue] = None

        # Stato iniziale delle piste: disponibilità immediata
        self.rome_tz = pytz.timezone('Europe/Rome')
        now = self.get_current_time()
        self.ALFA_next_available = now
        self.BRAVO_next_available = now
        self.CHARLIE_next_available = now

        # Variabili per la gestione dei giocatori
        self.next_player_alfa_bravo_id: Optional[str] = None
        self.next_player_alfa_bravo_locked: bool = False
        self.next_player_alfa_bravo_name: Optional[str] = None
        self.next_player_charlie_id: Optional[str] = None
        self.next_player_charlie_locked: bool = False
        self.next_player_charlie_name: Optional[str] = None
        self.current_player_couple: Optional[Queue] = None
        self.player_in_charlie: bool = False

        # Flag per tracciare lo stato delle piste
        self.couple_in_bravo = False
        self.couple_in_alfa = False
        self.single_in_alfa = False
        self.third_button_pressed = False

        # Liste per i giocatori skippati
        self.skipped_couples: List[Queue] = []
        self.skipped_singles: List[Queue] = []
        self.skipped_charlie: List[Queue] = []

        # Dizionario per memorizzare i nomi dei giocatori
        self.player_names: Dict[str, str] = {}

        # Inizializza le code con i nuovi formati ID
        # for i in range(1, 11):
        #     couple_id = f"GIALLO-{i:02d}"
        #     single_id = f"BLU-{i:02d}"
        #     charlie_id = f"VERDE-{i:02d}"
            
        #     self.add_couple(couple_id)
        #     self.add_single(single_id)
        #     self.add_charlie_player(charlie_id)

        self.player_start_times: Dict[str, datetime.datetime] = {}
        self.player_durations: Dict[str, float] = {}

    def add_couple(self, couple_id, name) -> None:
        self.queue_couples.append({'id': couple_id, 'arrival': self.get_current_time()})
        self.player_names[couple_id] = name

    def add_single(self, single_id, name) -> None:
        self.queue_singles.append({'id': single_id, 'arrival': self.get_current_time()})
        self.player_names[single_id] = name

    def add_charlie_player(self, player_id, name) -> None:
        """Aggiunge un giocatore alla coda Charlie"""
        if not any(p['id'] == player_id for p in self.queue_charlie):
            self.queue_charlie.append({
                'id': player_id,
                'arrival': self.get_current_time(),
                'name': name
            })
            self.player_names[player_id] = name
            if not self.next_player_charlie_id and not self.next_player_charlie_locked:
                self.next_player_charlie_id = player_id
                self.next_player_charlie_name = name
                self.next_player_charlie_locked = True

    def record_couple_game(self, mid_time: float, total_time: float) -> None:
        """
        Registra i tempi (in minuti) relativi a un game coppia:
          - mid_time: tempo dal Pulsante 1 all'attivazione del Pulsante 3
          - total_time: tempo totale dal Pulsante 1 (avvio) allo stop (liberazione di BRAVO)
        Dopo la registrazione, aggiorna i tempi medi.
        """
        self.couple_history_mid.append(mid_time)
        self.couple_history_total.append(total_time)
        # Mantiene la pista BRAVO occupata fino alla fine del game di coppia
        self.current_player_bravo = None  
        self.couple_in_alfa = False
        self.couple_in_bravo = False
        self.update_averages()
        self.update_next_player()
        # Record the duration
        player_id = self.current_player_couple['id']
        start_time = self.player_start_times.pop(player_id, None)
        if start_time:
            duration = (self.get_current_time() - start_time).total_seconds() / 60
            self.player_durations[player_id] = duration

    def record_single_game(self, game_time: float) -> None:
        """
        Registra il tempo (in minuti) relativo a un game singolo (durata in cui ALFA è occupata).
        Dopo la registrazione, aggiorna i tempi medi.
        """
        if self.current_player_alfa:
            player_id = self.current_player_alfa['id']
            self.single_history.append(game_time)
            self.update_averages()
            self.current_player_alfa = None
            if self.couple_in_bravo and self.queue_singles:
                self.next_player_alfa_bravo_id = self.queue_singles[0]['id']
                self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                self.next_player_alfa_bravo_locked = True
            else:
                self.update_next_player()
            # Record the duration
            start_time = self.player_start_times.pop(player_id, None)
            if start_time:
                duration = (self.get_current_time() - start_time).total_seconds() / 60
                self.player_durations[player_id] = duration

    def record_charlie_game(self, game_time: float) -> None:
        """Registra il tempo (in minuti) relativo a un game charlie"""
        if self.current_player_charlie:
            player_id = self.current_player_charlie['id']
            self.charlie_history.append(game_time)
            self.update_averages()
            self.current_player_charlie = None
            self.player_in_charlie = False
            # Record the duration
            start_time = self.player_start_times.pop(player_id, None)
            if start_time:
                duration = (self.get_current_time() - start_time).total_seconds() / 60
                self.player_durations[player_id] = duration

    def format_time(self, time_in_minutes: float) -> str:
        """Formatta il tempo in minuti e secondi"""
        minutes = int(time_in_minutes)
        seconds = int((time_in_minutes - minutes) * 60)
        return f"{minutes}m {seconds}s"
    
    def get_leaderboard(self) -> Dict[str, List[Tuple[str, str]]]:
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

    def get_current_time(self) -> datetime.datetime:
        """Ottiene l'ora corrente nel fuso orario di Roma"""
        return datetime.datetime.now(self.rome_tz)

    def localize_time(self, dt):
        """Assicura che un datetime abbia il fuso orario di Roma"""
        if dt.tzinfo is None:
            return self.rome_tz.localize(dt)
        return dt
    
    

    def update_averages(self) -> None:
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


    

    def get_player_name(self, player_id: Optional[str]) -> str:
        if player_id is None:
            return "N/D"
        return self.player_names.get(player_id, player_id)

    def update_next_player(self) -> None:
        """
        Aggiorna next_player_alfa_bravo_id e next_player_alfa_bravo_name in base alla disponibilità in coda,
        considerando l'orario di entrata (campo 'arrival') oppure la priorità,
        in modo che il prossimo giocatore da entrare venga mostrato nella finestra "Prossimo ingresso".
        """
        if self.current_player_alfa is None and self.current_player_bravo is None:
            if self.queue_couples:
                self.next_player_alfa_bravo_id = self.queue_couples[0]['id']
                assert self.next_player_alfa_bravo_id is not None
                self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                self.next_player_alfa_bravo_locked = True
            elif self.queue_singles:
                self.next_player_alfa_bravo_id = self.queue_singles[0]['id']
                assert self.next_player_alfa_bravo_id is not None
                self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                self.next_player_alfa_bravo_locked = True
            else:
                self.next_player_alfa_bravo_id = None
                self.next_player_alfa_bravo_name = None
                self.next_player_alfa_bravo_locked = False
        elif self.current_player_alfa is None and self.current_player_bravo is not None:
            if self.queue_couples:
                self.next_player_alfa_bravo_id = self.queue_couples[0]['id']
                assert self.next_player_alfa_bravo_id is not None
                self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                self.next_player_alfa_bravo_locked = True
            elif self.queue_singles:
                self.next_player_alfa_bravo_id = self.queue_singles[0]['id']
                assert self.next_player_alfa_bravo_id is not None
                self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                self.next_player_alfa_bravo_locked = True
            else:
                self.next_player_alfa_bravo_id = None
                self.next_player_alfa_bravo_name = None
                self.next_player_alfa_bravo_locked = False
        else:
            if self.queue_couples and self.current_player_alfa and self.current_player_alfa["id"].startswith("BLU") and self.current_player_bravo is None:
                self.next_player_alfa_bravo_id = self.queue_couples[0]['id']
                assert self.next_player_alfa_bravo_id is not None
                self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                self.next_player_alfa_bravo_locked = True
            elif self.queue_couples:
                self.next_player_alfa_bravo_id = self.queue_couples[0]['id']
                assert self.next_player_alfa_bravo_id is not None
                self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                self.next_player_alfa_bravo_locked = True
            elif self.queue_singles:
                self.next_player_alfa_bravo_id = self.queue_singles[0]['id']
                assert self.next_player_alfa_bravo_id is not None
                self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                self.next_player_alfa_bravo_locked = True
            else:
                self.next_player_alfa_bravo_id = None
                self.next_player_alfa_bravo_name = None
                self.next_player_alfa_bravo_locked = False

    def start_game(self, is_couple: bool) -> None:
        now = self.get_current_time()
        if is_couple:
            if self.queue_couples:
                self.current_player_couple = self.queue_couples.pop(0)
                self.ALFA_next_available = now + datetime.timedelta(minutes=self.T_mid)
                self.BRAVO_next_available = now + datetime.timedelta(minutes=self.T_total)
                self.current_player_alfa = self.current_player_couple
                self.current_player_bravo = self.current_player_couple
                self.couple_in_alfa = True
                self.couple_in_bravo = True
                self.player_start_times[self.current_player_couple['id']] = now
                if self.queue_singles:
                    self.next_player_alfa_bravo_id = self.queue_singles[0]['id']
                    self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                    self.next_player_alfa_bravo_locked = True
                else:
                    self.next_player_alfa_bravo_id = self.queue_couples[0]['id'] if self.queue_couples else None
                    self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id) if self.next_player_alfa_bravo_id else None
                    self.next_player_alfa_bravo_locked = True if self.next_player_alfa_bravo_id else False
            else:
                raise ValueError("No couples in queue to start the game.")
        else:
            if self.queue_singles:
                self.current_player_alfa = self.queue_singles.pop(0)
                self.single_in_alfa = True
                self.ALFA_next_available = now + datetime.timedelta(minutes=self.T_single)
                self.player_start_times[self.current_player_alfa['id']] = now
                if self.queue_couples:
                    self.next_player_alfa_bravo_id = self.queue_couples[0]['id']
                    self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                    self.next_player_alfa_bravo_locked = True
                else:
                    self.next_player_alfa_bravo_id = self.queue_singles[0]['id'] if self.queue_singles else None
                    self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id) if self.next_player_alfa_bravo_id else None
                    self.next_player_alfa_bravo_locked = True if self.next_player_alfa_bravo_id else False
            else:
                raise ValueError("No singles in queue to start the game.")

    def simulate_schedule(self) -> Dict[str, datetime.datetime]:
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
            # Se non ci sono coppie in coda, ma ci sono singoli, serviamo un singolo
            if not couples and singles:
                item = singles.pop(0)
                start_time = sim_time
                estimated_times[item['id']] = start_time
                sim_time = start_time + dt_single
                continue

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

    def get_waiting_board(self) -> Tuple[
        List[Tuple[int, str, Union[datetime.datetime, str]]],
        List[Tuple[int, str, Union[datetime.datetime, str]]],
        List[Tuple[int, str, Union[datetime.datetime, str]]]
    ]:
        now = self.get_current_time()
        # Calcola i tempi stimati di ingresso
        est = self.simulate_schedule()
        # Se non è già fissato un prossimo giocatore...
        if not self.next_player_alfa_bravo_locked:
            # Caso speciale: se c'è una coppia in BRAVO e un singolo in ALFA, prioritizza le coppie
            if self.couple_in_bravo and self.single_in_alfa and self.queue_couples:
                self.next_player_alfa_bravo_id = self.queue_couples[0]['id']
                self.next_player_alfa_bravo_locked = True
            else:
                # Altrimenti, controlla il tempo stimato per ogni giocatore in coda
                for queue_item in self.queue_couples + self.queue_singles:
                    estimated_time = est.get(queue_item['id'])
                    if estimated_time:
                        minutes_to_entry = (estimated_time - now).total_seconds() / 60
                        if minutes_to_entry <= 2:
                            self.next_player_alfa_bravo_id = queue_item['id']
                            self.next_player_alfa_bravo_locked = True
                            break

        # Costruzione della board: se l'elemento corrisponde a next_player_alfa_bravo_id, mostra "PROSSIMO INGRESSO"
        couples_board: List[Tuple[int, str, Union[datetime.datetime, str]]] = []
        for idx, item in enumerate(self.queue_couples):
            estimated = est.get(item['id'], None)
            if item['id'] == self.next_player_alfa_bravo_id:
                couples_board.append((idx + 1, item['id'], "PROSSIMO INGRESSO"))
            else:
                # Convertiamo eventuale None in "N/D"
                value = estimated if estimated is not None else "N/D"
                couples_board.append((idx + 1, item['id'], value))

        singles_board: List[Tuple[int, str, Union[datetime.datetime, str]]] = []
        for idx, item in enumerate(self.queue_singles):
            estimated = est.get(item['id'], None)
            if item['id'] == self.next_player_alfa_bravo_id:
                singles_board.append((idx + 1, item['id'], "PROSSIMO INGRESSO"))
            else:
                value = estimated if estimated is not None else "N/D"
                singles_board.append((idx + 1, item['id'], value))

        charlie_board: List[Tuple[int, str, Union[datetime.datetime, str]]] = []
        for idx, item in enumerate(self.queue_charlie):
            if item['id'] == self.next_player_charlie_id:
                charlie_board.append((idx + 1, item['id'], "PROSSIMO INGRESSO"))
            else:
                players_ahead = idx
                estimated_time = now + datetime.timedelta(minutes=self.T_charlie * players_ahead)
                charlie_board.append((idx + 1, item['id'], estimated_time))

        return couples_board, singles_board, charlie_board

    def button_third_pressed(self) -> None:
        """Gestisce la pressione del pulsante metà percorso e libera la Pista ALPHA solo se c'era una coppia"""
        if self.current_player_alfa and self.current_player_alfa["id"].startswith("GIALLO"):
            self.third_button_pressed = True
            self.couple_in_alfa = False
            self.current_player_alfa = None    # Libera la pista ALPHA
            self.next_player_alfa_bravo_id = None         # Correzione: resettiamo next_player_alfa_bravo_id
        else:
            raise ValueError("Non c'è una coppia in ALFA.")

    def can_stop_couple(self) -> bool:
        "Verifica se una coppia può fermarsi"
        return self.third_button_pressed

    def skip_player(self, player_id: str) -> None:
        """Sposta un giocatore nella lista degli skippati (Alfa/Bravo)"""
        player = next((c for c in self.queue_couples if c['id'] == player_id), None)
        if player:
            self.queue_couples.remove(player)
            self.skipped_couples.append(player)
            # Set the next player to the next couple in the queue
            if self.queue_couples:
                self.next_player_alfa_bravo_id = self.queue_couples[0]['id']
                self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                self.next_player_alfa_bravo_locked = True
            else:
                self.next_player_alfa_bravo_id = None
                self.next_player_alfa_bravo_name = None
                self.next_player_alfa_bravo_locked = False
        else:
            player = next((s for s in self.queue_singles if s['id'] == player_id), None)
            if player:
                self.queue_singles.remove(player)
                self.skipped_singles.append(player)
                # Set the next player to the next single in the queue
                if self.queue_singles:
                    self.next_player_alfa_bravo_id = self.queue_singles[0]['id']
                    self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                    self.next_player_alfa_bravo_locked = True
                elif self.queue_couples:
                    self.next_player_alfa_bravo_id = self.queue_couples[0]['id']
                    self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                    self.next_player_alfa_bravo_locked = True
                else:
                    self.next_player_alfa_bravo_id = None
                    self.next_player_alfa_bravo_name = None
                    self.next_player_alfa_bravo_locked = False

    def skip_charlie_player(self, player_id: str) -> None:
        """Sposta un giocatore nella lista degli skippati (Charlie)"""
        player = next((p for p in self.queue_charlie if p['id'] == player_id), None)
        if player:
            self.queue_charlie.remove(player)
            self.skipped_charlie.append(player)
            # Set the next player to the next Charlie in the queue
            if self.queue_charlie:
                self.next_player_charlie_id = self.queue_charlie[0]['id']
                self.next_player_charlie_name = self.get_player_name(self.next_player_charlie_id)
                self.next_player_charlie_locked = True
            else:
                self.next_player_charlie_id = None
                self.next_player_charlie_name = None
                self.next_player_charlie_locked = False

    def restore_skipped(self, player_id: str) -> None:
        """Ripristina un giocatore skippato in coda come priorità"""
        player = next((c for c in self.skipped_couples if c['id'] == player_id), None)
        if player:
            self.skipped_couples.remove(player)
            self.queue_couples.insert(0, player)
        else:
            player = next((s for s in self.skipped_singles if s['id'] == player_id), None)
            if player:
                self.skipped_singles.remove(player)
                self.queue_singles.insert(0, player)
            else:
                player = next((p for p in self.skipped_charlie if p['id'] == player_id), None)
                if player:
                    self.skipped_charlie.remove(player)
                    self.queue_charlie.insert(0, player)

    def restore_skipped_as_next(self, player_id: str) -> None:
        """Ripristina un giocatore skippato come prossimo nella coda"""
        player = next((c for c in self.skipped_couples if c['id'] == player_id), None)
        if player:
            self.skipped_couples.remove(player)
            self.queue_couples.insert(0, player)
            self.next_player_alfa_bravo_id = player_id
            self.next_player_alfa_bravo_locked = True
        else:
            player = next((s for s in self.skipped_singles if s['id'] == player_id), None)
            if player:
                self.skipped_singles.remove(player)
                self.queue_singles.insert(0, player)
                self.next_player_alfa_bravo_id = player_id
                self.next_player_alfa_bravo_locked = True
            else:
                player = next((p for p in self.skipped_charlie if p['id'] == player_id), None)
                if player:
                    self.skipped_charlie.remove(player)
                    self.queue_charlie.insert(0, player)
                    self.next_player_charlie_id = player_id
                    self.next_player_charlie_name = self.get_player_name(player_id)
                    self.next_player_charlie_locked = True

    def start_charlie_game(self) -> None:
        """Avvia un gioco sulla pista Charlie"""
        if self.next_player_charlie_id:
            self.current_player_charlie = {'id': self.next_player_charlie_id, 'arrival': self.get_current_time()}
            self.CHARLIE_next_available = self.get_current_time() + datetime.timedelta(minutes=self.T_charlie)
            self.player_start_times[self.current_player_charlie['id']] = self.get_current_time()
            self.player_in_charlie = True
            # Rimuovi il giocatore dalla coda
            self.queue_charlie = [p for p in self.queue_charlie if p['id'] != self.next_player_charlie_id]
            # Imposta il prossimo giocatore
            if self.queue_charlie:
                self.next_player_charlie_id = self.queue_charlie[0]['id']
                self.next_player_charlie_name = self.get_player_name(self.next_player_charlie_id)
                self.next_player_charlie_locked = True
            else:
                self.next_player_charlie_id = None
                self.next_player_charlie_name = None
                self.next_player_charlie_locked = False

    def get_durations(self) -> Dict[str, str]:
        """Restituisce le durate dei giocatori attuali in pista formattate in minuti:secondi"""
        durations = {}
        now = self.get_current_time()
        if self.current_player_alfa:
            player_id = self.current_player_alfa['id']
            start_time = self.player_start_times.get(player_id)
            if start_time:
                duration_seconds = (now - start_time).total_seconds()
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                durations['alfa'] = f"{minutes:02}:{seconds:02}"
        if self.current_player_bravo:
            player_id = self.current_player_bravo['id']
            start_time = self.player_start_times.get(player_id)
            if start_time:
                duration_seconds = (now - start_time).total_seconds()
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                durations['bravo'] = f"{minutes:02}:{seconds:02}"
        if self.current_player_charlie:
            player_id = self.current_player_charlie['id']
            start_time = self.player_start_times.get(player_id)
            if start_time:
                duration_seconds = (now - start_time).total_seconds()
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                durations['charlie'] = f"{minutes:02}:{seconds:02}"
        return durations

    def delete_player(self, player_id: str) -> None:
        """Elimina un giocatore dalla coda"""
        self.queue_couples = [p for p in self.queue_couples if p['id'] != player_id]
        self.queue_singles = [p for p in self.queue_singles if p['id'] != player_id]
        self.queue_charlie = [p for p in self.queue_charlie if p['id'] != player_id]
        self.skipped_couples = [p for p in self.skipped_couples if p['id'] != player_id]
        self.skipped_singles = [p for p in self.skipped_singles if p['id'] != player_id]
        self.skipped_charlie = [p for p in self.skipped_charlie if p['id'] != player_id]

        # Check if the deleted player was the next player in the queue
        if self.next_player_alfa_bravo_id == player_id:
            self.next_player_alfa_bravo_id = None
            self.next_player_alfa_bravo_name = None
            self.next_player_alfa_bravo_locked = False
            self.update_next_player()

        if self.next_player_charlie_id == player_id:
            self.next_player_charlie_id = None
            self.next_player_charlie_name = None
            self.next_player_charlie_locked = False
            self.update_next_player()
        
        

if __name__ == '__main__':
    backend = GameBackend()
    
    # Assicuriamoci che, al momento, non ci sia un game in corso
    # Aggiungiamo alcune coppie e alcuni singoli in coda
    # backend.add_couple("GIALLO-01")
    # backend.add_single("BLU-01")
    # backend.add_couple("GIALLO-02")
    # backend.add_single("BLU-02")
    # backend.add_couple("GIALLO-03")
    # backend.add_single("BLU-03")
    print("Tabellone Coppie (Gialli):")
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
    print(f"{pos}. {sid} - Ingresso stimato: {time_str}")
    print("\nTabellone Charlie (Verde):")
    for pos, cid, time_est in charlie_board:
      time_str = time_est.strftime('%H:%M:%S') if isinstance(time_est, datetime.datetime) else time_est if time_est else 'N/D'
    print(f"{pos}. {cid} - Ingresso stimato: {time_str}")

