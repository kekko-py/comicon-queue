/* filepath: /c:/Users/Samuel/Desktop/progetto-socs/software_comicon/comicon-queue/static/scripts/keypad.js */
let keypadInput = '';

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
        $.ajax({
            url: '/button_press',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({button: 'third'}),
            success: function() {
                alert('Codice corretto - Metà percorso attivato');
            }
        });
    } else {
        alert('Codice non valido');
    }
    clearKey();
}