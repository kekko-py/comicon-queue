from flask import Flask, render_template, jsonify, request, redirect, url_for, send_file
from main import GameBackend
import datetime
import os
import pytz
import subprocess
import time
import atexit
import qrcode
import logging
import sqlite3
import time
import subprocess
from io import BytesIO
from threading import Thread
from threading import Lock

app = Flask(__name__)
backend = GameBackend()

# Impostazioni logging
logging.basicConfig(level=logging.DEBUG)

sqlite_lock = Lock()
SQLITE_DB_PATH = 'stand_db.db'  # Database local MySQLite in cui salveremo le queue
BASE_URL = "http://localhost:2000"  # Bisogna cambiarlo con il sito delle queue si mercenari socs che andremo a creare
qr_img = None

def init_sqlite():
    logging.debug("[QUEUES] Acquisizione del lock per SQLite")
    with sqlite_lock:
        logging.debug("[QUEUES] Lock acquisito")

        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()

        logging.debug("[QUEUES] Creazione tabella, se non esiste")
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS queues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_type TEXT CHECK(player_type IN ('couple', 'single', 'charlie', 'statico')) NOT NULL,
                player_id TEXT NOT NULL,
                player_name TEXT NOT NULL,
                arrival_time DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

        logging.debug("[QUEUES] Connessione chiusa e lock rilasciato")


# Chiama la funzione per inizializzare il database
init_sqlite()


def init_scoring_table():
    logging.debug("[SCORING] Acquisizione del lock per SQLite")
    with sqlite_lock:
        logging.debug("[SCORING] Lock acquisito")

        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()

        logging.debug("[SCORING] Creazione tabella scoring, se non esiste")
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS scoring (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_type TEXT CHECK(player_type IN ('couple', 'single', 'charlie', 'statico')) NOT NULL,
                player_id TEXT NOT NULL,
                player_name TEXT NOT NULL,
                score TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        logging.debug("[SCORING] Connessione chiusa e lock rilasciato")


# Chiama la funzione per inizializzare la tabella scoring
init_scoring_table()

def init_skipped_table():
    logging.debug("[SKIPPED] Acquisizione del lock per SQLite")
    with sqlite_lock:
        logging.debug("[SKIPPED] Lock acquisito")

        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()

        logging.debug("[SKIPPED] Creazione tabella skipped_players, se non esiste")
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS skipped_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_type TEXT CHECK(player_type IN ('couple', 'single', 'charlie', 'statico')) NOT NULL,
                player_id TEXT NOT NULL,
                player_name TEXT NOT NULL,
                skipped_at DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        logging.debug("[SKIPPED] Connessione chiusa e lock rilasciato")

# Chiama la funzione per inizializzare la tabella skipped_players
init_skipped_table()

# Aggiungi questa funzione per caricare gli skippati all'avvio
def load_skipped_from_db():
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT player_type, player_id, player_name FROM skipped_players ORDER BY created_at DESC")
        rows = cursor.fetchall()

        # Pulisci le liste esistenti
        backend.skipped_couples.clear()
        backend.skipped_singles.clear()
        backend.skipped_charlie.clear()
        backend.skipped_statico.clear()

        for row in rows:
            player_type, player_id, player_name = row
            player_data = {'id': player_id, 'name': player_name}
            
            if player_type == 'couple':
                backend.skipped_couples.append(player_data)
            elif player_type == 'single':
                backend.skipped_singles.append(player_data)
            elif player_type == 'charlie':
                backend.skipped_charlie.append(player_data)
            elif player_type == 'statico':
                backend.skipped_statico.append(player_data)

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Errore durante il caricamento degli skippati dal database: {e}")

# Carica gli skippati all'avvio dell'applicazione
load_skipped_from_db()

def load_scores_from_db():
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT player_type, player_id, player_name, score FROM scoring ORDER BY created_at DESC")
        rows = cursor.fetchall()

        # Pulisci gli storici esistenti
        backend.couple_history_total.clear()
        backend.single_history.clear()
        backend.charlie_history.clear()
        backend.statico_history.clear()

        for row in rows:
            player_type, player_id, player_name, score = row
            # Converti il punteggio da stringa a float (es. "2m 30s" → 2.5)
            if 'm' in score:
                minutes = float(score.split('m')[0])
                seconds = float(score.split('m')[1].split('s')[0]) if 's' in score else 0
                score_minutes = minutes + (seconds / 60)

                if player_type == 'couple':
                    backend.couple_history_total.append(score_minutes)
                elif player_type == 'single':
                    backend.single_history.append(score_minutes)
                elif player_type == 'charlie':
                    backend.charlie_history.append(score_minutes)
                elif player_type == 'statico':
                    backend.statico_history.append(score_minutes)

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Errore durante il caricamento degli score dal database: {e}")


# Carica gli score all'avvio dell'applicazione
load_scores_from_db()


# Funzione per caricare le code dal database all'avvio
def load_queues_from_db():
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT player_type, player_id, player_name, arrival_time FROM queues ORDER BY created_at DESC")
        rows = cursor.fetchall()

        backend.queue_couples.clear()
        backend.queue_singles.clear()
        backend.queue_charlie.clear()
        backend.queue_statico.clear()

        for row in rows:
            player_type, player_id, player_name, arrival_time = row
            if player_type == 'couple':
                backend.queue_couples.append({'id': player_id, 'arrival': arrival_time})
            elif player_type == 'single':
                backend.queue_singles.append({'id': player_id, 'arrival': arrival_time})
            elif player_type == 'charlie':
                backend.queue_charlie.append({'id': player_id, 'arrival': arrival_time})
            elif player_type == 'statico':
                backend.queue_statico.append({'id': player_id, 'arrival': arrival_time})

            backend.player_names[player_id] = player_name

            # Imposta il prossimo giocatore per Charlie
        if backend.queue_charlie:
            backend.next_player_charlie_id = backend.queue_charlie[0]['id']
            backend.next_player_charlie_name = backend.get_player_name(backend.next_player_charlie_id)
            backend.next_player_charlie_locked = True
        else:
            backend.next_player_charlie_id = None
            backend.next_player_charlie_name = None
            backend.next_player_charlie_locked = False

        if backend.queue_statico:
            backend.next_player_statico_id = backend.queue_statico[0]['id']
            backend.next_player_statico_name = backend.get_player_name(backend.next_player_statico_id)
            backend.next_player_statico_locked = True
        else:
            backend.next_player_statico_id = None
            backend.next_player_statico_name = None
            backend.next_player_statico_locked = False

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Errore durante il caricamento delle code dal database: {e}")


# Carica le code all'avvio dell'applicazione
load_queues_from_db()


def save_queues_to_db():
    while True:
        try:
            conn = sqlite3.connect(SQLITE_DB_PATH)
            cursor = conn.cursor()

            # Cancella le vecchie code
            cursor.execute("DELETE FROM queues")
            conn.commit()

            # Salva le code delle coppie
            for couple in backend.queue_couples:
                cursor.execute(
                    "INSERT INTO queues (player_type, player_id, player_name, arrival_time) VALUES (?, ?, ?, ?) ",
                    ('couple', couple['id'], backend.get_player_name(couple['id']), couple['arrival'])
                )

            # Salva le code dei singoli
            for single in backend.queue_singles:
                cursor.execute(
                    "INSERT INTO queues (player_type, player_id, player_name, arrival_time) VALUES (?, ?, ?, ?)",
                    ('single', single['id'], backend.get_player_name(single['id']), single['arrival'])
                )

            # Salva le code di Charlie
            for charlie in backend.queue_charlie:
                cursor.execute(
                    "INSERT INTO queues (player_type, player_id, player_name, arrival_time) VALUES (?, ?, ?, ?)",
                    ('charlie', charlie['id'], backend.get_player_name(charlie['id']), charlie['arrival'])
                )

            # Salva le code di Statico
            for statico in backend.queue_statico:
                cursor.execute(
                    "INSERT INTO queues (player_type, player_id, player_name, arrival_time) VALUES (?, ?, ?, ?)",
                    ('statico', statico['id'], backend.get_player_name(statico['id']), statico['arrival'])
                )

            # Salva gli score
            cursor.execute("DELETE FROM scoring")
            for i, score in enumerate(backend.couple_history_total):
                cursor.execute(
                    "INSERT INTO scoring (player_type, player_id, player_name, score) VALUES (?, ?, ?, ?)",
                    ('couple', f"COMPLETATO-{i + 1}", f"COMPLETATO-{i + 1}", backend.format_time(score))
                )
            for i, score in enumerate(backend.single_history):
                cursor.execute(
                    "INSERT INTO scoring (player_type, player_id, player_name, score) VALUES (?, ?, ?, ?)",
                    ('single', f"COMPLETATO-{i + 1}", f"COMPLETATO-{i + 1}", backend.format_time(score))
                )
            for i, score in enumerate(backend.charlie_history):
                cursor.execute(
                    "INSERT INTO scoring (player_type, player_id, player_name, score) VALUES (?, ?, ?, ?)",
                    ('charlie', f"COMPLETATO-{i + 1}", f"COMPLETATO-{i + 1}", backend.format_time(score))
                )
            for i, score in enumerate(backend.statico_history):
                cursor.execute(
                    "INSERT INTO scoring (player_type, player_id, player_name, score) VALUES (?, ?, ?, ?)",
                    ('statico', f"COMPLETATO-{i + 1}", f"COMPLETATO-{i + 1}", backend.format_time(score))
                )

            # Salva gli skippati
            cursor.execute("DELETE FROM skipped_players")
            for player in backend.skipped_couples:
                cursor.execute(
                    "INSERT INTO skipped_players (player_type, player_id, player_name, skipped_at) VALUES (?, ?, ?, ?)",
                    ('couple', player['id'], backend.get_player_name(player['id']), datetime.datetime.now())
                )
            for player in backend.skipped_singles:
                cursor.execute(
                    "INSERT INTO skipped_players (player_type, player_id, player_name, skipped_at) VALUES (?, ?, ?, ?)",
                    ('single', player['id'], backend.get_player_name(player['id']), datetime.datetime.now())
                )
            for player in backend.skipped_charlie:
                cursor.execute(
                    "INSERT INTO skipped_players (player_type, player_id, player_name, skipped_at) VALUES (?, ?, ?, ?)",
                    ('charlie', player['id'], backend.get_player_name(player['id']), datetime.datetime.now())
                )
            for player in backend.skipped_statico:
                cursor.execute(
                    "INSERT INTO skipped_players (player_type, player_id, player_name, skipped_at) VALUES (?, ?, ?, ?)",
                    ('statico', player['id'], backend.get_player_name(player['id']), datetime.datetime.now())
                )

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Errore durante il salvataggio delle code nel database: {e}")
        time.sleep(10)  # Salva ogni 10 secondi


# Avvia il thread per il salvataggio periodico
save_thread = Thread(target=save_queues_to_db, daemon=True)
save_thread.start()



def initialize_queues():
    rome_tz = pytz.timezone('Europe/Rome')
    now = datetime.datetime.now(rome_tz)
    # backend.queue_couples.clear()
    # backend.queue_singles.clear()
    # backend.queue_charlie.clear()


initialize_queues()

# Funzione per generare il QR code
def generate_qrcode(url):
    import qrcode
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

# Aggiungi queste route
@app.route('/controls/statico')
def controls_statico():
    return render_template('controls_statico.html')

@app.route('/add_statico', methods=['POST'])
def add_statico():
    id = request.json.get('id')
    name = request.json.get('name')
    if not id or not name:
        return jsonify(success=False, error="ID and name are required"), 400
    statico_id = f"{name.upper()} {int(id):03d}"
    backend.add_statico_player(statico_id, name)
    return jsonify(success=True)

@app.route('/skip_statico_player', methods=['POST'])
def skip_statico_player():
    player_id = request.json.get('id')
    if player_id:
        backend.skip_statico_player(player_id)
        return jsonify(
            success=True,
            next_player_statico_id=backend.next_player_statico_id,
            next_player_statico_name=backend.next_player_statico_name
        )
    return jsonify(success=False, error="Player ID is required"), 400

@app.route('/statico_start', methods=['POST'])
def statico_start():
    if not backend.queue_statico:
        return jsonify(success=False, error="La coda di Statico è vuota. Non è possibile avviare il gioco.")
    backend.start_statico_game()
    return jsonify(success=True, current_player_delta=backend.current_player_delta,
                  current_player_echo=backend.current_player_echo)

@app.route('/statico_stop', methods=['POST'])
def statico_stop():
    if backend.current_player_delta or backend.current_player_echo:
        player_id = backend.current_player_delta['id'] if backend.current_player_delta else backend.current_player_echo['id']
        now = backend.get_current_time()
        if player_id and player_id in backend.player_start_times:
            backend.record_statico_game((now - backend.player_start_times[player_id]).total_seconds() / 60)
            backend.current_player_delta = None
            backend.current_player_echo = None
            return jsonify(success=True)
        else:
            return jsonify(success=False, error="Errore nel recupero del tempo di inizio del giocatore Statico.")
    return jsonify(success=False, error="Nessun giocatore Statico in pista.")

@app.route('/qrqueue')
def qr_queue():
    queue_url = f"{BASE_URL}/queue"
    return render_template('qrqueue.html', queue_url=queue_url)

@app.route('/qrqueue_img')
def qr_queue_img():
    global qr_img
    if qr_img is None:
        queue_url = f"{BASE_URL}/queue"
        qr_img = generate_qrcode(queue_url)
    
    img_io = BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


@app.route('/')
def index():
    return redirect(url_for('dashboard'))


@app.route('/controls/cassa')
def controls_cassa():
    return render_template('controls_cassa.html')


@app.route('/controls/couple')
def controls_couple():
    return render_template('controls_couple.html')


@app.route('/controls/single')
def controls_single():
    return render_template('controls_single.html')


@app.route('/controls/charlie')
def controls_charlie():
    return render_template('controls_charlie.html')


@app.route('/get_scores', methods=['GET'])
def get_scores():
    leaderboard = backend.get_leaderboard()
    return jsonify(leaderboard)


@app.route('/scoring')
def scoring():
    leaderboard = backend.get_leaderboard()
    return render_template('scoring.html', leaderboard=leaderboard)


@app.route('/keypad')
def keypad():
    return render_template('keypad.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/add_couple', methods=['POST'])
def add_couple():
    id = request.json.get('id')
    name = request.json.get('name')
    if not id or not name:
        return jsonify(success=False, error="ID and name are required"), 400
    couple_id = f"{name.upper()} {int(id):03d}"
    backend.add_couple(couple_id, name)
    return jsonify(success=True)


@app.route('/add_single', methods=['POST'])
def add_single():
    id = request.json.get('id')
    name = request.json.get('name')
    if not id or not name:
        return jsonify(success=False, error="ID and name are required"), 400
    single_id = f"{name.upper()} {int(id):03d}"
    backend.add_single(single_id, name)
    return jsonify(success=True)


@app.route('/add_charlie', methods=['POST'])
def add_charlie():
    id = request.json.get('id')
    name = request.json.get('name')
    if not id or not name:
        return jsonify(success=False, error="ID and name are required"), 400
    charlie_id = f"{name.upper()} {int(id):03d}"
    backend.add_charlie_player(charlie_id, name)
    return jsonify(success=True)


@app.route('/add_charlie_player', methods=['POST'])
def add_charlie_player():
    name = request.json.get('name')
    id = request.json.get('id')
    if not name or not id:
        return jsonify(success=False, error="Name and id are required"), 400
    player_id = f"{name.upper()} {int(id):03d}"
    backend.add_charlie_player(player_id, name)

    if not backend.next_player_charlie_id and backend.queue_charlie:
        backend.next_player_charlie_id = backend.queue_charlie[0]['id']
        backend.next_player_charlie_name = backend.get_player_name(backend.next_player_charlie_id)
        backend.next_player_charlie_locked = True

    return jsonify(success=True, player_id=player_id, name=name)


@app.route('/queue')
def queue():
    return render_template('queue.html')


@app.route('/simulate', methods=['GET'])
def simulate():
    couples_board, singles_board, charlie_board, statico_board = backend.get_waiting_board()
    next_player_alfa_bravo_id = backend.next_player_alfa_bravo_id
    next_player_charlie_id = backend.next_player_charlie_id
    next_player_charlie_name = backend.next_player_charlie_name

    formatted_charlie_board = []
    for pos, player_id, time_est in charlie_board:
        formatted_charlie_board.append({
            'id': player_id,
            'name': backend.get_player_name(player_id),
            'estimated_time': time_est
        })

    formatted_couples_board = []
    for pos, player_id, time_est in couples_board:
        formatted_couples_board.append({
            'id': player_id,
            'name': backend.get_player_name(player_id),
            'estimated_time': time_est
        })

    formatted_singles_board = []
    for pos, player_id, time_est in singles_board:
        formatted_singles_board.append({
            'id': player_id,
            'name': backend.get_player_name(player_id),
            'estimated_time': time_est
        })

    # Aggiungo la board per statico
    formatted_statico_board = []
    for pos, player_id, time_est in statico_board:
        formatted_statico_board.append({
            'id': player_id,
            'name': backend.get_player_name(player_id),
            'estimated_time': time_est
        })    

    next_player_alfa_bravo_name = backend.get_player_name(
        next_player_alfa_bravo_id) if next_player_alfa_bravo_id else None
    current_player_alfa = backend.current_player_alfa
    current_player_bravo = backend.current_player_bravo
    current_player_charlie = backend.current_player_charlie

    single_in_alfa = (
            isinstance(backend.current_player_alfa, dict) and
            'name' in backend.current_player_alfa and
            backend.current_player_alfa['name'] == "BLU"
    )
    couple_in_alfa = (
            isinstance(backend.current_player_alfa, dict) and
            'name' in backend.current_player_alfa and
            backend.current_player_alfa['name'] == "GIALLO"
    )
    couple_in_bravo = (
            isinstance(backend.current_player_bravo, dict) and
            'name' in backend.current_player_bravo and
            backend.current_player_bravo['name'] == "GIALLO"
    )

    now = backend.get_current_time()
    backend.ALFA_next_available = backend.localize_time(backend.ALFA_next_available)
    backend.BRAVO_next_available = backend.localize_time(backend.BRAVO_next_available)
    backend.CHARLIE_next_available = backend.localize_time(backend.CHARLIE_next_available)
    backend.DELTA_next_available = backend.localize_time(backend.DELTA_next_available)
    backend.ECHO_next_available = backend.localize_time(backend.ECHO_next_available)


    alfa_remaining = max(0, (backend.ALFA_next_available - now).total_seconds() / 60)
    bravo_remaining = max(0, (backend.BRAVO_next_available - now).total_seconds() / 60)
    charlie_remaining = max(0, (backend.CHARLIE_next_available - now).total_seconds() / 60)
    delta_remaining = max(0, (backend.DELTA_next_available - now).total_seconds() / 60)
    echo_remaining = max(0, (backend.ECHO_next_available - now).total_seconds() / 60)


    durations = backend.get_durations()

    return jsonify(
        couples=formatted_couples_board,
        singles=formatted_singles_board,
        charlie=formatted_charlie_board,
        statico=formatted_statico_board,
        next_player_alfa_bravo_id=next_player_alfa_bravo_id,
        next_player_alfa_bravo_name=next_player_alfa_bravo_name,
        next_player_charlie_id=next_player_charlie_id,
        next_player_charlie_name=next_player_charlie_name,
        next_player_statico_id=backend.next_player_statico_id,  # Aggiungiamo
        next_player_statico_name=backend.next_player_statico_name,  # Aggiungiamo
        current_player_alfa=current_player_alfa,
        current_player_bravo=current_player_bravo,
        current_player_charlie=current_player_charlie,
        current_player_delta=backend.current_player_delta,  # Aggiungiamo
        current_player_echo=backend.current_player_echo,  # Aggiungiamo
        player_icon_url=url_for('static', filename='icons/Vector.svg'),
        alfa_status='Occupata' if backend.current_player_alfa else 'Libera',
        bravo_status='Occupata' if backend.current_player_bravo else 'Libera',
        charlie_status='Occupata' if backend.current_player_charlie else 'Libera',
        delta_status='Occupata' if backend.current_player_delta else 'Libera',  # Aggiungiamo
        echo_status='Occupata' if backend.current_player_echo else 'Libera',  # Aggiungiamo
        alfa_remaining=f"{int(alfa_remaining)}min" if alfa_remaining > 0 else "0min",
        bravo_remaining=f"{int(bravo_remaining)}min" if bravo_remaining > 0 else "0min",
        charlie_remaining=f"{int(charlie_remaining)}min" if charlie_remaining > 0 else "0min",
        delta_remaining=f"{int(delta_remaining)}min" if delta_remaining > 0 else "0min",  # Aggiungiamo
        echo_remaining=f"{int(echo_remaining)}min" if echo_remaining > 0 else "0min",  # Aggiungiamo
        alfa_duration=durations.get('alfa', "N/D"),
        bravo_duration=durations.get('bravo', "N/D"),
        charlie_duration=durations.get('charlie', "N/D"),
        delta_duration=durations.get('delta', "N/D"),  # Aggiungiamo
        echo_duration=durations.get('echo', "N/D")  # Aggiungiamo
    )


@app.route('/button_press', methods=['POST'])
def button_press():
    button = request.json.get('button')
    now = backend.get_current_time()

    if button == 'first_start':
        if not backend.queue_couples:
            return jsonify(success=False, error="La coda delle coppie è vuota. Non è possibile avviare il gioco.")
        
        backend.start_game(is_couple=True)
        return jsonify(success=True, start_time=now.isoformat(), current_player_bravo=backend.current_player_bravo,
                       current_player_alfa=backend.current_player_alfa)

    elif button == 'second_start':
        if not backend.queue_singles:
            return jsonify(success=False, error="La coda dei singoli è vuota. Non è possibile avviare il gioco.")
        backend.start_game(is_couple=False)
        return jsonify(success=True, start_time=now.isoformat(), current_player_alfa=backend.current_player_alfa)

    elif button == 'first_stop':
        if not backend.can_stop_couple():
            return jsonify(success=False,
                           error="Non è possibile fermare la coppia senza aver prima inserito il codice di metà percorso")
        if backend.current_player_couple:
            backend.record_couple_game(backend.T_mid, (
                    now - backend.player_start_times[backend.current_player_couple['id']]).total_seconds() / 60)
            return jsonify(success=True)
        else:
            return jsonify(success=False, error="Nessuna coppia in pista.")

    elif button == 'second_stop':
        if backend.current_player_alfa:
            player_id = backend.current_player_alfa.get('id')
            if player_id and player_id in backend.player_start_times:
                backend.record_single_game((now - backend.player_start_times[player_id]).total_seconds() / 60)
                return jsonify(success=True)
            else:
                return jsonify(success=False, error="Errore nel recupero del tempo di inizio del giocatore singolo.")
        else:
            return jsonify(success=False, error="Nessun giocatore singolo in pista ALFA.")

    elif button == 'third':
        backend.button_third_pressed()
        return jsonify(success=True)

    elif button == 'charlie_start':
        if not backend.queue_charlie:
            return jsonify(success=False, error="La coda di Charlie è vuota. Non è possibile avviare il gioco.")
        backend.start_charlie_game()
        return jsonify(success=True, current_player_charlie=backend.current_player_charlie)

    elif button == 'charlie_stop':
        if backend.current_player_charlie:
            player_id = backend.current_player_charlie.get('id')
            if player_id and player_id in backend.player_start_times:
                backend.record_charlie_game((now - backend.player_start_times[player_id]).total_seconds() / 60)
                backend.current_player_charlie = None
                return jsonify(success=True)
            else:
                return jsonify(success=False, error="Errore nel recupero del tempo di inizio del giocatore Charlie.")

    # Nuovi casi per Statico DELTA e ECHO
    elif button == 'statico_start_delta':
        if not backend.queue_statico:
            return jsonify(success=False, error="La coda di Statico è vuota. Non è possibile avviare il gioco.")
        if backend.current_player_delta:
            return jsonify(success=False, error="La pista DELTA è già occupata.")
        
        backend.start_statico_game(pista='delta')
        return jsonify(
            success=True,
            current_player_delta=backend.current_player_delta,
            current_player_echo=None
        )

    elif button == 'statico_start_echo':
        if not backend.queue_statico:
            return jsonify(success=False, error="La coda di Statico è vuota. Non è possibile avviare il gioco.")
        if backend.current_player_echo:
            return jsonify(success=False, error="La pista ECHO è già occupata.")
        
        backend.start_statico_game(pista='echo')
        return jsonify(
            success=True,
            current_player_delta=None,
            current_player_echo=backend.current_player_echo
        )

    elif button == 'statico_stop_delta':
        if backend.current_player_delta:
            player_id = backend.current_player_delta.get('id')
            if player_id and player_id in backend.player_start_times:
                backend.record_statico_game(
                    (now - backend.player_start_times[player_id]).total_seconds() / 60,
                    pista='delta'
                )
                backend.current_player_delta = None
                return jsonify(success=True)
            else:
                return jsonify(success=False, error="Errore nel recupero del tempo di inizio del giocatore Statico (DELTA).")
        return jsonify(success=False, error="Nessun giocatore Statico in pista DELTA.")

    elif button == 'statico_stop_echo':
        if backend.current_player_echo:
            player_id = backend.current_player_echo.get('id')
            if player_id and player_id in backend.player_start_times:
                backend.record_statico_game(
                    (now - backend.player_start_times[player_id]).total_seconds() / 60,
                    pista='echo'
                )
                backend.current_player_echo = None
                return jsonify(success=True)
            else:
                return jsonify(success=False, error="Errore nel recupero del tempo di inizio del giocatore Statico (ECHO).")
        return jsonify(success=False, error="Nessun giocatore Statico in pista ECHO.")

    return jsonify(success=False, error="Pulsante non riconosciuto")


@app.route('/skip_next_player_alfa_bravo', methods=['POST'])
def skip_next_player_alfa_bravo():
    player_id = request.json.get('id')
    if player_id:
        backend.skip_player(player_id)
        return jsonify(
            success=True,
            next_player_alfa_bravo_id=backend.next_player_alfa_bravo_id,
            next_player_alfa_bravo_name=backend.next_player_alfa_bravo_name
        )
    return jsonify(success=False, error="Player ID is required"), 400



@app.route('/skip_charlie_player', methods=['POST'])
def skip_charlie_player():
    player_id = request.json.get('id')
    if player_id:
        backend.skip_charlie_player(player_id)
        return jsonify(
            success=True,
            next_player_charlie_id=backend.next_player_charlie_id,
            next_player_charlie_name=backend.next_player_charlie_name
        )
    return jsonify(success=False, error="Player ID is required"), 400



@app.route('/get_skipped', methods=['GET'])
def get_skipped():
    return jsonify({
        'couples': [{'id': c['id']} for c in backend.skipped_couples],
        'singles': [{'id': s['id']} for s in backend.skipped_singles],
        'charlie': [{'id': p['id']} for p in backend.skipped_charlie],
        'statico': [{'id': p['id']} for p in backend.skipped_statico]
    })


@app.route('/restore_skipped_as_next', methods=['POST'])
def restore_skipped():
    player_id = request.json.get('id')
    if player_id:
        backend.restore_skipped_as_next(player_id)
        return jsonify(success=True)
    return jsonify(success=False, error="Player ID is required"), 400


@app.route('/check_availability', methods=['GET'])
def check_availability():
    now = backend.get_current_time()

    alfa_available = (backend.current_player_alfa is None)
    bravo_available = (backend.current_player_bravo is None)

    return jsonify({
        'can_start_couple': alfa_available and bravo_available,
        'can_start_single': alfa_available,
        'alfa_status': 'Libera' if alfa_available else 'Occupata',
        'bravo_status': 'Libera' if bravo_available else 'Occupata'
    })


@app.route('/start_game', methods=['POST'])
def start_game_route():
    try:
        is_couple = request.json.get('is_couple', False)
        backend.start_game(is_couple)
        return jsonify(success=True)
    except ValueError as e:
        return jsonify(success=False, error=str(e)), 400
    except Exception as e:
        return jsonify(success=False, error="An unexpected error occurred."), 500


@app.route('/get_status', methods=['GET'])
def get_status():
    now = backend.get_current_time()
    charlie_remaining = max(0, (backend.CHARLIE_next_available - now).total_seconds() / 60)
    charlie_status = 'Occupata' if charlie_remaining > 0 else 'Libera'

    return jsonify({
        'charlie_status': charlie_status,
        'charlie_remaining': f"{int(charlie_remaining)}min" if charlie_remaining > 0 else "0min"
    })


@app.route('/delete_player', methods=['POST'])
def delete_player():
    player_id = request.json.get('id')
    if player_id:
        backend.delete_player(player_id)
        return jsonify(success=True)
    return jsonify(success=False, error="Player ID is required"), 400


def run_sync_script_periodically():
    while True:
        # Esegui lo script Python
        subprocess.run(['python', 'sync_script.py'])
        # Aspetta 2 minuti (120 secondi)
        time.sleep(120)


# Avvia il thread separato
sync_thread = Thread(target=run_sync_script_periodically, daemon=True)
sync_thread.start()

if __name__ == '__main__':
    app.secret_key = os.urandom(12)

    queue_url = f"{BASE_URL}/queue"
    qr_img = generate_qrcode(queue_url)

    # Esegui Flask con il riavvio automatico disabilitato
    app.run(host='0.0.0.0', port=2000, debug=True, use_reloader=False)
