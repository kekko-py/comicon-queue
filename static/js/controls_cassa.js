let coupleCounter = 1;
let singleCounter = 1;
let charlieCounter = 1;

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
                showNotification(`${playerName} ${playerId} aggiunto con successo!`);
                updateDashboard(); // Update the dashboard to reflect the new player
            } else {
                showNotification('Errore nell\'aggiunta del giocatore.', true);
            }
        });
});

document.getElementById('add-couple-btn').addEventListener('click', function () {
    if (coupleCounter < 100) {
        addPlayer('couple', coupleCounter, 'GIALLO');
        coupleCounter++;
        this.textContent = `Aggiungi Coppia (GIALLO) ${coupleCounter}`;
    } else {
        showNotification('Limite massimo di 100 coppie raggiunto.', true);
        addPlayer('couple', coupleCounter, 'GIALLO');
        coupleCounter = 1; // Reset the counter
        this.textContent = `Aggiungi Coppia (GIALLO) ${coupleCounter}`;
    }
});

document.getElementById('add-single-btn').addEventListener('click', function () {
    if (singleCounter < 100) {
        addPlayer('single', singleCounter, 'BLU');
        singleCounter++;
        this.textContent = `Aggiungi Singolo (BLU) ${singleCounter}`;
    } else {
        showNotification('Limite massimo di 100 singoli raggiunto.', true);
        addPlayer('single', singleCounter, 'BLU');
        singleCounter = 1; // Reset the counter
        this.textContent = `Aggiungi Singolo (BLU) ${singleCounter}`;
    }
});

document.getElementById('add-charlie-btn').addEventListener('click', function () {
    if (charlieCounter < 100) {
        addPlayer('charlie', charlieCounter, 'VERDE');
        charlieCounter++;
        this.textContent = `Aggiungi Charlie (VERDE) ${charlieCounter}`;
    } else {
        showNotification('Limite massimo di 100 Charlie raggiunto.', true);
        addPlayer('charlie', charlieCounter, 'VERDE');
        charlieCounter = 1; // Reset the counter
        this.textContent = `Aggiungi Charlie (VERDE) ${charlieCounter}`;
    }
});

function addPlayer(type, id, name) {
    fetch(`/add_${type}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: id, name: name })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(`${name} ${id} aggiunto con successo!`);
                updateDashboard(); // Update the dashboard to reflect the new player
            } else {
                showNotification('Errore nell\'aggiunta del giocatore.', true);
            }
        });
}

function showNotification(message, isError = false) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.style.color = isError ? 'red' : 'green';
    setTimeout(() => {
        notification.textContent = '';
    }, 3000);
}

function deletePlayer(playerId) {
    fetch(`/delete_player`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ id: playerId }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                updateDashboard();
            } else {
                showNotification("Errore nella cancellazione del giocatore.", true);
            }
        });
}

// Ensure the dashboard updates are also applied in the cassa page
setInterval(() => {
    updateDashboard();
}, 1000);

$(document).ready(function () {
    updateDashboard();
});
