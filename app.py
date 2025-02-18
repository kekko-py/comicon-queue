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
    couple_id = request.json.get('id')
    name = request.json.get('name')
    backend.add_couple(couple_id, name)
    return jsonify(success=True)

@app.route('/add_single', methods=['POST'])
def add_single():
    single_id = request.json.get('id')
    name = request.json.get('name')
    backend.add_single(single_id, name)
    return jsonify(success=True)

@app.route('/add_charlie_player', methods=['POST'])
def add_charlie_player():
    player_id = request.json.get('id')
    name = request.json.get('name')
    backend.add_charlie_player(player_id, name)
    return jsonify(success=True)

@app.route('/simulate', methods=['GET'])
def simulate():
    couples_board, singles_board, charlie_board = backend.get_waiting_board()
    next_player_id = backend.next_player_id
    next_charlie_player = backend.next_charlie_player
    
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
    next_player_name = backend.get_player_name(next_player_id) if next_player_id else None
    current_player_alfa = backend.current_player_alfa
    current_player_bravo = backend.current_player_bravo
    current_player_charlie = backend.current_player_charlie

    return jsonify(
        couples=formatted_couples_board, 
        singles=formatted_singles_board,
        charlie=formatted_charlie_board,
        next_player_id=next_player_id,
        next_player_name=next_player_name,
        next_charlie_player=next_charlie_player,
        current_player_alfa=current_player_alfa,
        current_player_bravo=current_player_bravo,
        current_player_charlie=current_player_charlie,
        player_icon_url=url_for('static', filename='icons/Vector.svg')
    )

@app.route('/get_status', methods=['GET'])
def get_status():
    print({
            'single_in_alfa': backend.single_in_alfa,
            'couple_in_alfa': backend.couple_in_alfa,
            'couple_in_bravo': backend.couple_in_bravo,
            'third_button_pressed': backend.third_button_pressed
        })
    now = backend.get_current_time()
    backend.ALFA_next_available = backend.localize_time(backend.ALFA_next_available)
    backend.BRAVO_next_available = backend.localize_time(backend.BRAVO_next_available)
    backend.CHARLIE_next_available = backend.localize_time(backend.CHARLIE_next_available)
    
    alfa_remaining = max(0, (backend.ALFA_next_available - now).total_seconds() / 60)
    bravo_remaining = max(0, (backend.BRAVO_next_available - now).total_seconds() / 60)
    charlie_remaining = max(0, (backend.CHARLIE_next_available - now).total_seconds() / 60)
    
    return jsonify({
        'alfa_status': 'Occupata' if backend.single_in_alfa or backend.couple_in_alfa else 'Libera',
        'bravo_status': 'Occupata' if (backend.couple_in_bravo) else 'Libera',
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
        print({
            'single_in_alfa': backend.single_in_alfa,
            'couple_in_alfa': backend.couple_in_alfa,
            'couple_in_bravo': backend.couple_in_bravo,
            'third_button_pressed': backend.third_button_pressed
        })
        if not backend.queue_couples:
            return jsonify(success=False, error="La coda delle coppie è vuota. Non è possibile avviare il gioco.")
        if backend.single_in_alfa:
            return jsonify(success=False, error="Non è possibile avviare il gioco di coppia mentre ALFA è occupata da un singolo.")
        # Avvio game coppia
        backend.ALFA_next_available = now + datetime.timedelta(minutes=backend.T_mid)
        backend.BRAVO_next_available = now + datetime.timedelta(minutes=backend.T_total)
        backend.couple_in_alfa = True
        backend.couple_in_bravo = True
        backend.current_player_alfa = backend.queue_couples[0]
        backend.current_player_bravo = backend.queue_couples[0]
        backend.start_game(is_couple=True)
        return jsonify(success=True, start_time=now.isoformat(), next_player_id=backend.next_player_id, current_player=backend.current_player_couple)
  
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
        backend.current_player_couple = None  # Reset current player couple

    elif button == 'second_start':
        if not backend.queue_singles:
            return jsonify(success=False, error="La coda dei singoli è vuota. Non è possibile avviare il gioco.")
        
        # Avvio game singolo
        backend.ALFA_next_available = now + datetime.timedelta(minutes=backend.T_single)
        backend.single_in_alfa = True
        backend.current_player_alfa = backend.queue_singles[0]
        backend.start_game(is_couple=False)
        return jsonify(success=True, start_time=now.isoformat(), next_player_id=backend.next_player_id, current_player=backend.current_player_single)
    
    elif button == 'second_stop':
        # Fine game singolo
        game_time = (now - backend.localize_time(backend.ALFA_next_available - datetime.timedelta(minutes=backend.T_single))).total_seconds() / 60
        backend.current_player_alfa = None
        backend.record_single_game(game_time)
        
        backend.ALFA_next_available = now
        backend.single_in_alfa = False
        backend.current_player_single = None  # Reset current player single

    elif button == 'third':
        backend.button_third_pressed()
    elif button == 'charlie_start':
        if not backend.queue_charlie:
            return jsonify(success=False, error="La coda di Charlie è vuota. Non è possibile avviare il gioco.")
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
    if backend.next_player_id:
        print(f"Current player: {backend.next_player_id}")
        backend.skip_player(backend.next_player_id)
        is_couple = backend.next_player_id in backend.couples
        print(f"Is couple: {is_couple}")
        # Imposta il prossimo giocatore della stessa categoria
        if is_couple and backend.queue_couples:
            backend.next_player_id = backend.queue_couples[0]['id']
            backend.next_player_locked = True
        elif not is_couple and backend.queue_singles:
            backend.next_player_id = backend.queue_singles[0]['id']
            backend.next_player_locked = True
        else:
            backend.next_player_id = None
            backend.next_player_locked = False
            # Aggiungi una logica per gestire la coda vuota
            if is_couple:
                print("La coda delle coppie è vuota.")
                # Esegui un'azione specifica, come notificare l'utente
            else:
                print("La coda dei singoli è vuota.")
                # Esegui un'azione specifica, come notificare l'utente

        print(f"Next player: {backend.next_player_id}")
    
    can_start_couple = not backend.single_in_alfa and not backend.couple_in_alfa and backend.queue_couples
    can_start_single = not backend.single_in_alfa and backend.queue_singles
    can_start_charlie = not backend.player_in_charlie and backend.queue_charlie

    return jsonify(success=True, can_start_couple=can_start_couple, can_start_single=can_start_single, can_start_charlie=can_start_charlie)


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
    print({
            'single_in_alfa': backend.single_in_alfa,
            'couple_in_alfa': backend.couple_in_alfa,
            'couple_in_bravo': backend.couple_in_bravo,
            'third_button_pressed': backend.third_button_pressed
        })
    now = backend.get_current_time()
    
    # Verifica disponibilità ALFA e BRAVO
   
    alfa_available = (backend.single_in_alfa == False and backend.couple_in_alfa == False)
    bravo_available = (backend.couple_in_bravo == False and backend.couple_in_alfa == False and backend.single_in_alfa == False)
    
    return jsonify({
        'can_start_couple': alfa_available and bravo_available ,  # Coppia ha bisogno di entrambe le piste
        'can_start_single': alfa_available,  # Singolo ha bisogno solo di ALFA
        'alfa_status': 'Libera' if alfa_available else 'Occupata',
        'bravo_status': 'Libera' if bravo_available else 'Occupata'
    })

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0', port=2000, debug=True)