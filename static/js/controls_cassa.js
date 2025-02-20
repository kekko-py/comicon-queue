document.getElementById('queueForm').addEventListener('submit', function (event) {
    event.preventDefault();
    const playerType = document.getElementById('playerType').value;
    const playerId = document.getElementById('playerId').value;
    let playerName = '';

    if (playerType === 'couple') {
        playerName = 'GIALLO';
    } else if (playerType === 'single') {
        playerName = 'BLU';
    } else if (playerType === 'charlie') {
        playerName = 'VERDE';
    }

    fetch(`/add_${playerType}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: playerId, name: playerName })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Giocatore aggiunto con successo!');
            } else {
                alert('Errore nell\'aggiunta del giocatore.');
            }
        });
});

document.getElementById('add-charlie-btn').addEventListener('click', addCharliePlayer);
