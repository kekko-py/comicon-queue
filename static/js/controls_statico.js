let timerIntervalDelta;
let timerIntervalEcho;
let startTimeDelta;
let startTimeEcho;
let isGameActiveDelta = false;
let isGameActiveEcho = false;

function updateNextPlayer() {
    fetch('/simulate')
        .then(response => response.json())
        .then(data => {
            if (data.statico && data.statico.length > 0) {
                const nextPlayer = data.statico[0];
                $('#next-player').text(`${nextPlayer.id}`);
                $('#next-player-btn').prop('disabled', false);
            } else {
                $('#next-player').text('-');
                $('#next-player-btn').prop('disabled', true);
            }

            updateTrackStatus(data);
        });
}

function updateTrackStatus(data) {
    const canStartDelta = data.delta_status === 'Libera';
    const canStartEcho = data.echo_status === 'Libera';
    
    $('#start-delta-btn').prop('disabled', !canStartDelta);
    $('#start-echo-btn').prop('disabled', !canStartEcho);
    
    $('#status-delta').text(data.delta_status + ' - ' + data.delta_remaining);
    $('#status-echo').text(data.echo_status + ' - ' + data.echo_remaining);

    if (!canStartDelta) {
        $('#start-delta-btn').attr('title', 'Pista DELTA occupata');
    } else {
        $('#start-delta-btn').attr('title', '');
    }

    if (!canStartEcho) {
        $('#start-echo-btn').attr('title', 'Pista ECHO occupata');
    } else {
        $('#start-echo-btn').attr('title', '');
    }
}

function updateTimerDelta() {
    if (!isGameActiveDelta) return;
    const now = new Date();
    const diff = Math.floor((now - startTimeDelta) / 1000);
    const minutes = Math.floor(diff / 60).toString().padStart(2, '0');
    const seconds = (diff % 60).toString().padStart(2, '0');
    $('#timer-delta').text(`${minutes}:${seconds}`);
}

function updateTimerEcho() {
    if (!isGameActiveEcho) return;
    const now = new Date();
    const diff = Math.floor((now - startTimeEcho) / 1000);
    const minutes = Math.floor(diff / 60).toString().padStart(2, '0');
    const seconds = (diff % 60).toString().padStart(2, '0');
    $('#timer-echo').text(`${minutes}:${seconds}`);
}

function activateNextPlayer() {
    $('#next-player-btn').prop('disabled', true);
    $('#stop-delta-btn, #stop-echo-btn').prop('disabled', false);
    $('#timer-delta, #timer-echo').text('00:00');
    $('#current-player-delta, #current-player-echo').text('-');
    updateNextPlayer();
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

            if (button === 'statico_start_delta') {
                startTimeDelta = new Date();
                isGameActiveDelta = true;
                timerIntervalDelta = setInterval(updateTimerDelta, 1000);
                $('#current-player-delta').text(`${response.current_player_delta.name || response.current_player_delta.id}`);
                $('#start-delta-btn').prop('disabled', true);
                $('#stop-delta-btn').prop('disabled', false);
            } 
            else if (button === 'statico_start_echo') {
                startTimeEcho = new Date();
                isGameActiveEcho = true;
                timerIntervalEcho = setInterval(updateTimerEcho, 1000);
                $('#current-player-echo').text(`${response.current_player_echo.name || response.current_player_echo.id}`);
                $('#start-echo-btn').prop('disabled', true);
                $('#stop-echo-btn').prop('disabled', false);
            }
            else if (button === 'statico_stop_delta') {
                isGameActiveDelta = false;
                clearInterval(timerIntervalDelta);
                $('#current-player-delta').text('-');
                $('#start-delta-btn').prop('disabled', false);
                $('#stop-delta-btn').prop('disabled', true);
                updateNextPlayer();
            }
            else if (button === 'statico_stop_echo') {
                isGameActiveEcho = false;
                clearInterval(timerIntervalEcho);
                $('#current-player-echo').text('-');
                $('#start-echo-btn').prop('disabled', false);
                $('#stop-echo-btn').prop('disabled', true);
                updateNextPlayer();
            }
        },
        error: function(xhr, status, error) {
            alert("Errore nella comunicazione con il server: " + error);
        }
    });
}

// Aggiorna la disponibilità delle piste e il prossimo giocatore ogni secondo
setInterval(() => {
    updateNextPlayer();
}, 1000);

$(document).ready(function () {
    updateNextPlayer();
    $('#stop-delta-btn, #stop-echo-btn').prop('disabled', true);
});