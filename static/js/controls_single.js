let timerInterval;
let startTime;
let isGameActive = false;

function updateNextPlayer() {
    if ($('#current-player').text() !== '-' && !$('#next-player-btn').prop('disabled')) {
        return;
    }

    fetch('/simulate')
        .then(response => response.json())
        .then(data => {
            if (data.singles && data.singles.length > 0) {
                const playerId = data.singles[0][1];  // Ora sarà nel formato BLU-XX
                $('#current-player').text(playerId);
                $('#next-player-btn').prop('disabled', false);
            } else {
                $('#current-player').text('-');
                $('#next-player-btn').prop('disabled', true);
            }
        });
}

function updateAvailability() {
    $.get('/check_availability', function(data) {
        const canStart = data.can_start_single;
        $('#start-btn').prop('disabled', !canStart);
        $('#status').text(`ALFA: ${data.alfa_status} - BRAVO: ${data.bravo_status}`);
        
        if (!canStart) {
            $('#start-btn').attr('title', 'Attendere che la pista ALFA sia libera');
        } else {
            $('#start-btn').attr('title', '');
        }
        updateNextPlayer();
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
        data: JSON.stringify({button: button}),
        success: function(response) {
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
            } else if (button === 'second_stop') {
                isGameActive = false;
                clearInterval(timerInterval);
                $('#next-player-btn').prop('disabled', false);
                $('#start-btn, #stop-btn').prop('disabled', true);
            }
            
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
            fetch('/simulate')
                .then(response => response.json())
                .then(data => {
                    // Cerca il prossimo giocatore di tipo singolo (blu)
                    if (data.singles && data.singles.length > 0) {
                        $('#current-player').text(data.singles[0][1]);
                        $('#next-player-btn').prop('disabled', false);
                    } //else {
                    //     $('#current-player').text('-');
                    //     $('#next-player-btn').prop('disabled', true);
                    // }
                });
        });
    }
}

setInterval(updateAvailability, 1000);
$(document).ready(function() {
    $.get('/check_availability', function(data) {
        isGameActive = data.alfa_status === 'Occupata' || data.bravo_status === 'Occupata';
        updateAvailability();
    });
});