let coupleCounter = 1;
let singleCounter = 1;
let charlieCounter = 1;
let staticoCounter = 1;
$(document).ready(function () {
    fetchLastPlayerIds(); // Imposta i counter basati sugli ID attuali
    updateDashboard();
});


function fetchLastPlayerIds() {
    fetch('/simulate')
        .then(response => response.json())
        .then(data => {
            let maxCouple = 0, maxSingle = 0, maxCharlie = 0, maxStatico = 0;

            if (data.couples.length > 0) {
                let lastCouple = data.couples[data.couples.length - 1];
                maxCouple = parseInt(lastCouple.id.split(' ')[1]) || 0;
            }

            if (data.singles.length > 0) {
                let lastSingle = data.singles[data.singles.length - 1];
                maxSingle = parseInt(lastSingle.id.split(' ')[1]) || 0;
            }

            if (data.charlie.length > 0) {
                let lastCharlie = data.charlie[data.charlie.length - 1];
                maxCharlie = parseInt(lastCharlie.id.split(' ')[1]) || 0;
            }

            if (data.statico && data.statico.length > 0) {
                let lastStatico = data.statico[data.statico.length - 1];
                maxStatico = parseInt(lastStatico.id.split(' ')[1]) || 0;
            }

            // Imposta i counter al numero successivo
            coupleCounter = maxCouple + 1;
            singleCounter = maxSingle + 1;
            charlieCounter = maxCharlie + 1;
            staticoCounter = maxStatico + 1;

            // Aggiorna i pulsanti con il valore corretto
            document.getElementById('playerId-coppia').value = `${coupleCounter}`;
            document.getElementById('playerId-singolo').value = `${singleCounter}`;
            document.getElementById('playerId-charlie').value = `${charlieCounter}`;
            document.getElementById('playerId-statico').value = `${staticoCounter}`;
        })
        .catch(error => console.error('Errore nel recupero degli ID:', error));
}

// Aggiungi questo codice per sincronizzare con dashboard.js
function handleSkip(playerType) {
    let elementId, endpoint;
    
    switch(playerType) {
        case 'alfa-bravo':
            elementId = "next-player-alfa-bravo-text";
            endpoint = "/skip_next_player_alfa_bravo";
            break;
        case 'charlie':
            elementId = "next-charlie-text";
            endpoint = "/skip_charlie_player";
            break;
        case 'statico':
            elementId = "next-statico-text";
            endpoint = "/skip_statico_player";
            break;
        default:
            return;
    }

    const nextPlayer = document.getElementById(elementId).textContent;
    if (nextPlayer && nextPlayer !== "Nessun Giocatore In Coda" && nextPlayer !== "-") {
        fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ id: nextPlayer }),
        })
        .then(response => {
            if (!response.ok) throw new Error("Errore nella chiamata di skip");
            return response.json();
        })
        .then(data => {
            // Forza l'aggiornamento completo della dashboard
            updateDashboard();
            showNotification("Giocatore skippato con successo");
        })
        .catch(error => {
            console.error("Errore durante lo skip:", error);
            showNotification("Errore durante lo skip del giocatore", true);
        });
    }
}

// Sostituisci le funzioni esistenti con queste
function skipNextPlayerAlfaBravo() {
    handleSkip('alfa-bravo');
}

function skipNextPlayerCharlie() {
    handleSkip('charlie');
}

function skipNextPlayerStatico() {
    handleSkip('statico');
}

document.getElementById('queueForm-coppia').addEventListener('submit', function (event) {
    event.preventDefault();
    const playerType = document.getElementById('playerType').value;
    const playerId =  document.getElementById('playerId-coppia').value;

    fetch(`/add_couple`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: playerId, name: 'GIALLO' })
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

        document.getElementById('playerId-coppia').value = `${Number(document.getElementById('playerId-coppia').value)   + 1}`;
});

document.getElementById('queueForm-singolo').addEventListener('submit', function (event) {
    event.preventDefault();
    const playerType = document.getElementById('playerType').value;
    const playerId = document.getElementById('playerId-singolo').value;
    fetch(`/add_single`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: playerId, name: 'BLU' })
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

    document.getElementById('playerId-singolo').value = `${Number(document.getElementById('playerId-singolo').value)   + 1}`;
});

document.getElementById('queueForm-charlie').addEventListener('submit', function (event) {
    event.preventDefault();
    const playerType = document.getElementById('playerType').value;
    const playerId = document.getElementById('playerId-charlie').value;
    fetch(`/add_charlie`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: playerId, name: 'VERDE' })
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

    document.getElementById('playerId-charlie').value = `${Number(document.getElementById('playerId-charlie').value)   + 1}`;
});

document.getElementById('queueForm-statico').addEventListener('submit', function (event) {
    event.preventDefault();
    const playerType = document.getElementById('playerType').value;
    const playerId = document.getElementById('playerId-statico').value;
    fetch(`/add_statico`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: playerId, name: 'ROSSO' })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`${playerName} ${playerId} aggiunto con successo!`);
            updateDashboard();
        } else {
            showNotification('Errore nell\'aggiunta del giocatore.', true);
        }
    });

    document.getElementById('playerId-statico').value = `${Number(document.getElementById('playerId-statico').value) + 1}`;
});

// document.getElementById('add-couple-btn').addEventListener('click', function () {
//     if (coupleCounter < 100) {
//         addPlayer('couple', coupleCounter, 'GIALLO');
//         coupleCounter++;
//         this.textContent = `Aggiungi Coppia (GIALLO) ${coupleCounter}`;
//     } else {
//         showNotification('Limite massimo di 100 coppie raggiunto.', true);
//         addPlayer('couple', coupleCounter, 'GIALLO');
//         coupleCounter = 1; // Reset the counter
//         this.textContent = `Aggiungi Coppia (GIALLO) ${coupleCounter}`;
//     }
// });

// document.getElementById('add-single-btn').addEventListener('click', function () {
//     if (singleCounter < 100) {
//         addPlayer('single', singleCounter, 'BLU');
//         singleCounter++;
//         this.textContent = `Aggiungi Singolo (BLU) ${singleCounter}`;
//     } else {
//         showNotification('Limite massimo di 100 singoli raggiunto.', true);
//         addPlayer('single', singleCounter, 'BLU');
//         singleCounter = 1; // Reset the counter
//         this.textContent = `Aggiungi Singolo (BLU) ${singleCounter}`;
//     }
// });

// document.getElementById('add-charlie-btn').addEventListener('click', function () {
//     if (charlieCounter < 100) {
//         addPlayer('charlie', charlieCounter, 'VERDE');
//         charlieCounter++;
//         this.textContent = `Aggiungi Charlie (VERDE) ${charlieCounter}`;
//     } else {
//         showNotification('Limite massimo di 100 Charlie raggiunto.', true);
//         addPlayer('charlie', charlieCounter, 'VERDE');
//         charlieCounter = 1; // Reset the counter
//         this.textContent = `Aggiungi Charlie (VERDE) ${charlieCounter}`;
//     }
// });

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
