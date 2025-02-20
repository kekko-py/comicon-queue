from flask import Flask, render_template, jsonify, request, redirect, url_for
from main import GameBackend  # Assicurati che il tuo file principale si chiami main.py
import datetime
import os
import pytz

app = Flask(__name__)
backend = GameBackend()

# Sostituisci @app.before_first_request con questa implementazione
def initialize_queues():
    rome_tz = pytz.timezone('Europe/Rome')
    now = datetime.datetime.now(rome_tz)
    
    # Svuota le code esistenti
    backend.queue_couples.clear()
    backend.queue_singles.clear()
    backend.queue_charlie.clear()
    
    # Popola le code con 10 elementi ciascuna
    # for i in range(1, 11):
    #     couple_id = f"GIALLO-{i:02d}"  # Genera C01, C02, ..., C10
    #     single_id = f"BLU-{i:02d}"  # Genera S01, S02, ..., S10
    #     charlie_id = f"VERDE-{i:02d}"  # Genera G01, G02, ..., G10
        
    #     backend.add_couple(couple_id)
    #     backend.add_single(single_id)
    #     backend.add_charlie_player(charlie_id)

# Chiama l'inizializzazione subito dopo la creazione dell'app
initialize_queues()

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
    if not id:
        return jsonify(success=False, error="id is required"), 400
    name = "GIALLO"
    couple_id = f"{name}-{int(id):02d}"
    backend.add_couple(couple_id, name)
    return jsonify(success=True)

@app.route('/add_single', methods=['POST'])
def add_single():
    id = request.json.get('id')
    if not id:
        return jsonify(success=False, error="id is required"), 400
    name = "BLU"
    single_id = f"{name}-{int(id):02d}"
    backend.add_single(single_id, name)
    return jsonify(success=True)

@app.route('/add_charlie', methods=['POST'])
def add_charlie():
    id = request.json.get('id')
    if not id:
        return jsonify(success=False, error="id is required"), 400
    name = "VERDE"
    charlie_id = f"{name}-{int(id):02d}"
    backend.add_charlie_player(charlie_id, name)
    return jsonify(success=True)

@app.route('/add_charlie_player', methods=['POST'])
def add_charlie_player():
    name = request.json.get('name')
    id = request.json.get('id')
    if not name or not id:
        return jsonify(success=False, error="Name and id are required"), 400
    player_id = f"{name.upper()}-{int(id):02d}"
    backend.add_charlie_player(player_id, name)
    
    # Update the next Charlie player
    if not backend.next_player_charlie_id and backend.queue_charlie:
        backend.next_player_charlie_id = backend.queue_charlie[0]['id']
        backend.next_player_charlie_name = backend.get_player_name(backend.next_player_charlie_id)
        backend.next_player_charlie_locked = True
    
    return jsonify(success=True, player_id=player_id, name=name)

@app.route('/simulate', methods=['GET'])
def simulate():
    couples_board, singles_board, charlie_board = backend.get_waiting_board()
    next_player_alfa_bravo_id = backend.next_player_alfa_bravo_id
    next_player_charlie_id = backend.next_player_charlie_id
    next_player_charlie_name = backend.next_player_charlie_name
    
    # Formatta la coda Charlie nello stesso modo delle altre code
    formatted_charlie_board = []
    for pos, player_id, time_est in charlie_board:
        formatted_charlie_board.append({
            'id': player_id,  # ID del giocatore
            'name': backend.get_player_name(player_id),  # Nome del giocatore
            'estimated_time': time_est  # Orario stimato
        })
    
    # Formatta la coda delle coppie
    formatted_couples_board = []
    for pos, player_id, time_est in couples_board:
        formatted_couples_board.append({
            'id': player_id,  # ID del giocatore
            'name': backend.get_player_name(player_id),  # Nome del giocatore
            'estimated_time': time_est  # Orario stimato
        })
    
    # Formatta la coda dei singoli
    formatted_singles_board = []
    for pos, player_id, time_est in singles_board:
        formatted_singles_board.append({
            'id': player_id,  # ID del giocatore
            'name': backend.get_player_name(player_id),  # Nome del giocatore
            'estimated_time': time_est  # Orario stimato
        })
    
    # Aggiungi il nome del giocatore per il prossimo giocatore
    next_player_alfa_bravo_name = backend.get_player_name(next_player_alfa_bravo_id) if next_player_alfa_bravo_id else None
    current_player_alfa = backend.current_player_alfa
    current_player_bravo = backend.current_player_bravo
    current_player_charlie = backend.current_player_charlie

    # Informazioni di stato
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
    
    alfa_remaining = max(0, (backend.ALFA_next_available - now).total_seconds() / 60)
    bravo_remaining = max(0, (backend.BRAVO_next_available - now).total_seconds() / 60)
    charlie_remaining = max(0, (backend.CHARLIE_next_available - now).total_seconds() / 60)

    durations = backend.get_durations()

    return jsonify(
        couples=formatted_couples_board, 
        singles=formatted_singles_board,
        charlie=formatted_charlie_board,
        next_player_alfa_bravo_id=next_player_alfa_bravo_id,
        next_player_alfa_bravo_name=next_player_alfa_bravo_name,
        next_player_charlie_id=next_player_charlie_id,
        next_player_charlie_name=next_player_charlie_name,
        current_player_alfa=current_player_alfa,
        current_player_bravo=current_player_bravo,
        current_player_charlie=current_player_charlie,
        player_icon_url=url_for('static', filename='icons/Vector.svg'),
        alfa_status='Occupata' if backend.current_player_alfa else 'Libera',
        bravo_status='Occupata' if backend.current_player_bravo else 'Libera',
        charlie_status='Occupata' if backend.current_player_charlie else 'Libera',
        alfa_remaining=f"{int(alfa_remaining)}min" if alfa_remaining > 0 else "0min",
        bravo_remaining=f"{int(bravo_remaining)}min" if bravo_remaining > 0 else "0min",
        charlie_remaining=f"{int(charlie_remaining)}min" if charlie_remaining > 0 else "0min",
        alfa_duration=durations.get('alfa', "N/D"),
        bravo_duration=durations.get('bravo', "N/D"),
        charlie_duration=durations.get('charlie', "N/D")
    )

@app.route('/button_press', methods=['POST'])
def button_press():
    button = request.json.get('button')
    now = backend.get_current_time()
    
    if button == 'first_start':
        # Logica per avviare un gioco di coppia
        if not backend.queue_couples:
            return jsonify(success=False, error="La coda delle coppie è vuota. Non è possibile avviare il gioco.")
        
        backend.start_game(is_couple=True)
        return jsonify(success=True, start_time=now.isoformat(), current_player_bravo=backend.current_player_bravo , current_player_alfa=backend.current_player_alfa)
    
    elif button == 'second_start':
        # Logica per avviare un gioco singolo
        if not backend.queue_singles:
            return jsonify(success=False, error="La coda dei singoli è vuota. Non è possibile avviare il gioco.")
        backend.start_game(is_couple=False)
        return jsonify(success=True, start_time=now.isoformat(), current_player_alfa=backend.current_player_alfa) 
    
    elif button == 'first_stop':
        # Logica per fermare un gioco di coppia
        if not backend.can_stop_couple():
            return jsonify(success=False, error="Non è possibile fermare la coppia senza aver prima inserito il codice di metà percorso")
        if backend.current_player_couple:
            backend.record_couple_game(backend.T_mid, (now - backend.player_start_times[backend.current_player_couple['id']]).total_seconds() / 60)
            return jsonify(success=True)
        else:
            return jsonify(success=False, error="Nessuna coppia in pista.")
    
    elif button == 'second_stop':
        # Logica per fermare un gioco singolo
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
        # Logica per fermare un gioco charlie
        if backend.current_player_charlie:
            player_id = backend.current_player_charlie.get('id')
            if player_id and player_id in backend.player_start_times:
                backend.record_charlie_game((now - backend.player_start_times[player_id]).total_seconds() / 60)
                backend.current_player_charlie = None  # Libera la pista Charlie
                return jsonify(success=True)
            else:
                return jsonify(success=False, error="Errore nel recupero del tempo di inizio del giocatore Charlie.")
    
    return jsonify(success=False, error="Pulsante non riconosciuto")

@app.route('/skip_next_player_alfa_bravo', methods=['POST'])
def skip_next_player_alfa_bravo():
    player_id = request.json.get('id')
    if player_id:
        backend.skip_player(player_id)
        is_couple = player_id.startswith("GIALLO")
        
        # Set the next player based on the type and availability in the queue
        if is_couple and backend.queue_couples:
            backend.next_player_alfa_bravo_id = backend.queue_couples[0]['id']
            backend.next_player_alfa_bravo_name = backend.get_player_name(backend.next_player_alfa_bravo_id)
            backend.next_player_alfa_bravo_locked = True
        elif not is_couple and backend.queue_singles:
            backend.next_player_alfa_bravo_id = backend.queue_singles[0]['id']
            backend.next_player_alfa_bravo_name = backend.get_player_name(backend.next_player_alfa_bravo_id)
            backend.next_player_alfa_bravo_locked = True
        else:
            backend.next_player_alfa_bravo_id = None
            backend.next_player_alfa_bravo_name = None
            backend.next_player_alfa_bravo_locked = False

        print(f"Next player: {backend.next_player_alfa_bravo_id}")
    
    can_start_couple = not backend.single_in_alfa and not backend.couple_in_alfa and backend.queue_couples
    can_start_single = not backend.single_in_alfa and backend.queue_singles

    return jsonify(
        success=True, 
        can_start_couple=can_start_couple, 
        can_start_single=can_start_single,
        next_player_alfa_bravo_id=backend.next_player_alfa_bravo_id,
        next_player_alfa_bravo_name=backend.next_player_alfa_bravo_name
    )

@app.route('/skip_charlie_player', methods=['POST'])
def skip_charlie_player():
    player_id = request.json.get('id')
    if player_id:
        backend.skip_charlie_player(player_id)
        can_start_charlie = not backend.player_in_charlie and backend.queue_charlie
        return jsonify(success=True, can_start_charlie=can_start_charlie)
    return jsonify(success=False, error="Player ID is required"), 400

@app.route('/get_skipped', methods=['GET'])
def get_skipped():
    return jsonify({
        'couples': [{'id': c['id']} for c in backend.skipped_couples],
        'singles': [{'id': s['id']} for s in backend.skipped_singles],
        'charlie': [{'id': p['id']} for p in backend.skipped_charlie]
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
    
    # Verifica disponibilità ALFA e BRAVO
    alfa_available = (backend.current_player_alfa is None ) 
    bravo_available = (backend.current_player_bravo is None )
    
    return jsonify({
        'can_start_couple': alfa_available and bravo_available ,  # Coppia ha bisogno di entrambe le piste
        'can_start_single': alfa_available,  # Singolo ha bisogno solo di ALFA
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

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0', port=2000, debug=True)