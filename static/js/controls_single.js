let timerInterval;
let startTime;
let isGameActive = false;

function updateNextPlayer() {
    fetch('/simulate')
        .then(response => response.json())
        .then(data => {
            if (data.singles && data.singles.length > 0) {
                const nextPlayer = data.singles[0];  // Ora sarà un oggetto con id e name
                $('#next-player').text(`${nextPlayer.name} - ${nextPlayer.id}`);
                $('#next-player-btn').prop('disabled', false);
                console.log(`Next player to start: ${nextPlayer.name}`);  // Log del prossimo giocatore
            } else {
                $('#next-player').text('-');
                $('#next-player-btn').prop('disabled', true);
            }
            if (data.current_player_name) {
                $('#current-player').text(`${data.current_player_name} - ${data.current_player_id}`);
            } else {
                $('#current-player').text('-');
            }
        });
}

function updateAvailability() {
    $.get('/check_availability', function (data) {
        const canStart = data.can_start_single;
        $('#start-btn').prop('disabled', !canStart);
        $('#status').text(`ALFA: ${data.alfa_status} - BRAVO: ${data.bravo_status}`);

        if (!canStart) {
            $('#start-btn').attr('title', 'Attendere che la pista ALFA sia libera');
        } else {
            $('#start-btn').attr('title', '');
        }
    });
}

function updateTimer() {
    if (!isGameActive) return;
    const now = new Date();
    const diff = Math.floor((now - startTime) / 1000);
    const minutes = Math.floor(diff / 60).toString().padStart(2, '0');
    const seconds = (diff % 60).toString().padStart(2, '0');
    $('#timer').text(`${minutes}:${seconds}`);
}

function activateNextPlayer() {
    $('#next-player-btn').prop('disabled', true);
    $('#stop-btn').prop('disabled', false);
    $('#timer').text('00:00');
    $('#current-player').text('-');
    updateAvailability(); // Verifica disponibilità piste
}

function pressButton(button) {
    $.ajax({
        url: '/button_press',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ button: button }),
        success: function (response) {
            if (!response.success) {
                alert(response.error);
                return;
            }

            if (button === 'second_start') {
                startTime = new Date();
                isGameActive = true;
                timerInterval = setInterval(updateTimer, 1000);
                $('#next-player-btn').prop('disabled', true);
                $('#start-btn').prop('disabled', true);
                $('#stop-btn').prop('disabled', false);
                $('#current-player').text(response.current_player.name); // Aggiorna il giocatore corrente
            } else if (button === 'second_stop' && isGameActive) {
                isGameActive = false;
                clearInterval(timerInterval);
                $('#next-player-btn').prop('disabled', false);
                $('#start-btn, #stop-btn').prop('disabled', true);
                $('#current-player').text('-'); // Resetta il giocatore corrente
            }

            updateNextPlayer();
            updateAvailability();
        }
    });
}

function skipPlayer() {
    const currentPlayer = $('#current-player').text();
    if (currentPlayer !== '-') {
        fetch('/skip_player', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ id: currentPlayer })
        })
            .then(response => response.json())
            .then(() => {
                // Dopo lo skip, aggiorna immediatamente per mostrare il prossimo giocatore dello stesso tipo
                updateNextPlayer();
            });
    }
}

// timer per aggiornare la disponibilità delle piste e prossimo giocatore
setInterval(() => {
    updateAvailability();
    updateNextPlayer();
}, 1000);

$(document).ready(function () {
    updateAvailability();
    updateNextPlayer();
});