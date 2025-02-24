let timerInterval;
let startTime;
let isGameActive = false;

function updateNextPlayer() {
    fetch('/simulate')
        .then(response => response.json())
        .then(data => {
            if (data.charlie && data.charlie.length > 0) {
                const nextPlayer = data.charlie[0];  // Ora sarà un oggetto con id e name
                $('#next-player').text(`${nextPlayer.id}`);
                $('#next-player-btn').prop('disabled', false);
                console.log(`Next player to start: ${nextPlayer.id}`);  // Log del prossimo giocatore
            } else {
                $('#next-player').text('-');
                $('#next-player-btn').prop('disabled', true);
            }

            updateTrackStatus(data);
        });
}

function updateTrackStatus(data) {
    const canStart = data.charlie_status === 'Libera';
    $('#start-btn').prop('disabled', !canStart);
    $('#status').text(data.charlie_status + ' - ' + data.charlie_remaining);

    if (!canStart) {
        $('#start-btn').attr('title', 'Attendere che la pista CHARLIE sia libera');
    } else {
        $('#start-btn').attr('title', '');
    }
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
    updateNextPlayer(); // Verifica disponibilità piste
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

            if (button === 'charlie_start') {
                startTime = new Date();
                isGameActive = true;
                timerInterval = setInterval(updateTimer, 1000);
                $('#next-player-btn').prop('disabled', true);
                $('#start-btn').prop('disabled', true);
                $('#stop-btn').prop('disabled', false);
                $('#current-player').text(`${response.current_player_charlie['name']} - ${response.current_player_charlie['id']}`); // Aggiorna il giocatore corrente
            } else if (button === 'charlie_stop' && isGameActive) {
                isGameActive = false;
                clearInterval(timerInterval);
                $('#next-player-btn').prop('disabled', false);
                $('#start-btn, #stop-btn').prop('disabled', true);
                $('#current-player').text('-'); // Resetta il giocatore corrente
                updateNextPlayer();
                updateDashboard(); // Aggiorna la dashboard per riflettere lo stato libero della pista Charlie
            }
        }
    });
}

// timer per aggiornare la disponibilità delle piste e prossimo giocatore
setInterval(() => {
    updateNextPlayer();
}, 1000);

$(document).ready(function () {
    updateNextPlayer();
});