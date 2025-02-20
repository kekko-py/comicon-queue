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
                alert('Giocatore aggiunto con successo!');
            } else {
                alert('Errore nell\'aggiunta del giocatore.');
            }
        });
});

document.getElementById('add-couple-btn').addEventListener('click', function () {
    if (coupleCounter <= 100) {
        addPlayer('couple', coupleCounter, 'GIALLO');
        coupleCounter++;
        this.textContent = `Aggiungi Coppia (GIALLO) ${coupleCounter}`;
    } else {
        alert('Limite massimo di 100 coppie raggiunto.');
    }
});

document.getElementById('add-single-btn').addEventListener('click', function () {
    if (singleCounter <= 100) {
        addPlayer('single', singleCounter, 'BLU');
        singleCounter++;
        this.textContent = `Aggiungi Singolo (BLU) ${singleCounter}`;
    } else {
        alert('Limite massimo di 100 singoli raggiunto.');
    }
});

document.getElementById('add-charlie-btn').addEventListener('click', function () {
    if (charlieCounter <= 100) {
        addPlayer('charlie', charlieCounter, 'VERDE');
        charlieCounter++;
        this.textContent = `Aggiungi Charlie (VERDE) ${charlieCounter}`;
    } else {
        alert('Limite massimo di 100 Charlie raggiunto.');
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
                alert(`${name} ${id} aggiunto con successo!`);
            } else {
                alert('Errore nell\'aggiunta del giocatore.');
            }
        });
}
