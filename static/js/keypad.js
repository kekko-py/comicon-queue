/* filepath: /c:/Users/Samuel/Desktop/progetto-socs/software_comicon/comicon-queue/static/scripts/keypad.js */
let keypadInput = '';
let currentPlayerAlfa = null;

function addKey(key) {
    if (keypadInput.length < 4) {
        keypadInput += key;
        updateKeypadDisplay();
    }
}

function clearKey() {
    keypadInput = '';
    updateKeypadDisplay();
}

function updateKeypadDisplay() {
    document.getElementById('keypad-display').value = '*'.repeat(keypadInput.length);
}

function checkCode() {
    if (keypadInput === '1234') {
        if (currentPlayerAlfa && currentPlayerAlfa.id.startsWith('GIALLO')) {
            pressThirdButton();
        } else {
            alert("Non c'è una coppia in ALFA.");
        }
    } else {
        alert('Codice non valido');
    }
    clearKey();
}

function pressThirdButton() {
    fetch("/button_press", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ button: "third" }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                alert("Pulsante terzo attivato con successo.");
            } else {
                alert("Errore nell'attivazione del pulsante terzo.");
            }
        })
        .catch((error) => {
            console.error("Errore durante l'attivazione del pulsante terzo:", error);
        });
}

function updateCurrentPlayerAlfa() {
    fetch("/simulate")
        .then((response) => response.json())
        .then((data) => {
            currentPlayerAlfa = data.current_player_alfa;
        })
        .catch((error) => {
            console.error("Errore durante l'aggiornamento del giocatore corrente in ALFA:", error);
        });
}

// Aggiorna il giocatore corrente in ALFA ogni secondo
setInterval(updateCurrentPlayerAlfa, 1000);
updateCurrentPlayerAlfa();