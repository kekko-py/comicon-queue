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
    for i in range(1, 11):
        couple_id = f"GIALLO-{i:02d}"  # Genera C01, C02, ..., C10
        single_id = f"BLU-{i:02d}"  # Genera S01, S02, ..., S10
        charlie_id = f"VERDE-{i:02d}"  # Genera G01, G02, ..., G10
        
        backend.add_couple(couple_id)
        backend.add_single(single_id)
        backend.add_charlie_player(charlie_id)

# Chiama l'inizializzazione subito dopo la creazione dell'app
initialize_queues()

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

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
    couple_id = request.json.get('id')
    backend.add_couple(couple_id)
    return jsonify(success=True)

@app.route('/add_single', methods=['POST'])
def add_single():
    single_id = request.json.get('id')
    backend.add_single(single_id)
    return jsonify(success=True)

@app.route('/add_charlie_player', methods=['POST'])
def add_charlie_player():
    player_id = request.json.get('id')
    backend.add_charlie_player(player_id)
    return jsonify(success=True)

@app.route('/simulate', methods=['GET'])
def simulate():
    couples_board, singles_board, charlie_board = backend.get_waiting_board()
    next_player = backend.next_player
    next_charlie_player = backend.next_charlie_player
    
    # Formatta la coda Charlie nello stesso modo delle altre code
    formatted_charlie_board = []
    for pos, player_id, time_est in charlie_board:
        formatted_charlie_board.append([
            player_id,  # ID del giocatore
            player_id,  # Nome visualizzato
            time_est    # Orario stimato
        ])

    return jsonify(
        couples=couples_board, 
        singles=singles_board,
        charlie=formatted_charlie_board,
        next_player=next_player,
        next_charlie_player=next_charlie_player
    )

@app.route('/get_status', methods=['GET'])
def get_status():
    now = backend.get_current_time()
    backend.ALFA_next_available = backend.localize_time(backend.ALFA_next_available)
    backend.BRAVO_next_available = backend.localize_time(backend.BRAVO_next_available)
    backend.CHARLIE_next_available = backend.localize_time(backend.CHARLIE_next_available)
    
    alfa_remaining = max(0, (backend.ALFA_next_available - now).total_seconds() / 60)
    bravo_remaining = max(0, (backend.BRAVO_next_available - now).total_seconds() / 60)
    charlie_remaining = max(0, (backend.CHARLIE_next_available - now).total_seconds() / 60)
    
    return jsonify({
        'alfa_status': 'Occupata' if alfa_remaining > 0 else 'Libera',
        'bravo_status': 'Occupata' if bravo_remaining > 0 else 'Libera',
        'charlie_status': 'Occupata' if charlie_remaining > 0 else 'Libera',
        'alfa_remaining': f"{int(alfa_remaining)}min" if alfa_remaining > 0 else "0min",
        'bravo_remaining': f"{int(bravo_remaining)}min" if bravo_remaining > 0 else "0min",
        'charlie_remaining': f"{int(charlie_remaining)}min" if charlie_remaining > 0 else "0min"
    })

@app.route('/button_press', methods=['POST'])
def button_press():
    button = request.json.get('button')
    now = backend.get_current_time()
    
    if button == 'first_start':
        # Avvio game coppia
        backend.ALFA_next_available = now + datetime.timedelta(minutes=backend.T_mid)
        backend.BRAVO_next_available = now + datetime.timedelta(minutes=backend.T_total)
        backend.start_game(is_couple=True)
        return jsonify(success=True)
    elif button == 'first_stop':
        # Verifica se il pulsante metà percorso è stato premuto
        if not backend.can_stop_couple():
            return jsonify(
                success=False, 
                error="Non è possibile fermare la coppia senza aver prima inserito il codice di metà percorso"
            )
        # Fine game coppia
        game_time = (now - backend.localize_time(backend.BRAVO_next_available - datetime.timedelta(minutes=backend.T_total))).total_seconds() / 60
        backend.record_couple_game(backend.T_mid, game_time)
        backend.BRAVO_next_available = now
        backend.couple_in_bravo = False
        backend.third_button_pressed = False  # Reset del flag
    elif button == 'second_start':
        # Avvio game singolo
        backend.ALFA_next_available = now + datetime.timedelta(minutes=backend.T_single)
        backend.start_game(is_couple=False)
    elif button == 'second_stop':
        # Fine game singolo
        game_time = (now - backend.localize_time(backend.ALFA_next_available - datetime.timedelta(minutes=backend.T_single))).total_seconds() / 60
        backend.record_single_game(game_time)
        backend.ALFA_next_available = now
        backend.single_in_alfa = False
    elif button == 'third':
        backend.button_third_pressed()
    elif button == 'charlie_start':
        # Avvio game Charlie
        backend.CHARLIE_next_available = now + datetime.timedelta(minutes=backend.T_charlie)
        backend.start_charlie_game()
    elif button == 'charlie_stop':
        # Fine game Charlie
        game_time = (now - backend.localize_time(backend.CHARLIE_next_available - datetime.timedelta(minutes=backend.T_charlie))).total_seconds() / 60
        backend.record_charlie_game(game_time)
        backend.CHARLIE_next_available = now
        backend.player_in_charlie = False
    
    return jsonify(success=True)
@app.route('/skip_next_player', methods=['POST'])
def skip_next_player():
    if backend.next_player:
        backend.skip_player(backend.next_player)
        is_couple = backend.next_player.startswith('GIALLO-')
        print(is_couple)
        # Imposta il prossimo giocatore della stessa categoria
        if is_couple and backend.queue_couples:
            backend.next_player = backend.queue_couples[0]['id']
            backend.next_player_locked = True
        elif not is_couple and backend.queue_singles:
            backend.next_player = backend.queue_singles[0]['id']
            backend.next_player_locked = True
        else:
            backend.next_player = None
            backend.next_player_locked = False
    
    
    return jsonify(success=True)

@app.route('/skip_charlie_player', methods=['POST'])
def skip_charlie_player():
    if backend.next_charlie_player:
        backend.skip_charlie_player(backend.next_charlie_player)
        
        if backend.queue_charlie:
            backend.next_charlie_player = backend.queue_charlie[0]['id']
            backend.next_charlie_player_locked = True
        else:
            backend.next_charlie_player = None
            backend.next_charlie_player_locked = False
    
    return jsonify(success=True)

@app.route('/get_skipped', methods=['GET'])
def get_skipped():
    return jsonify({
        'couples': [{'id': c['id']} for c in backend.skipped_couples],
        'singles': [{'id': s['id']} for s in backend.skipped_singles],
        'charlie': [{'id': p['id']} for p in backend.skipped_charlie]
    })

@app.route('/restore_skipped', methods=['POST'])
def restore_skipped():
    player_id = request.json.get('id')
    if player_id:
        backend.restore_skipped(player_id)
    return jsonify(success=True)

@app.route('/check_availability', methods=['GET'])
def check_availability():
    now = backend.get_current_time()
    
    # Verifica disponibilità ALFA e BRAVO
    alfa_available = (backend.ALFA_next_available - now).total_seconds() <= 0
    bravo_available = (backend.BRAVO_next_available - now).total_seconds() <= 0
    
    return jsonify({
        'can_start_couple': alfa_available and bravo_available,  # Coppia ha bisogno di entrambe le piste
        'can_start_single': alfa_available,  # Singolo ha bisogno solo di ALFA
        'alfa_status': 'Libera' if alfa_available else 'Occupata',
        'bravo_status': 'Libera' if bravo_available else 'Occupata'
    })

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0', port=2000, debug=True)