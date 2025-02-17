let keypadInput = "";

function addKey(key) {
  if (keypadInput.length < 4) {
    keypadInput += key;
    updateKeypadDisplay();
  }
}

function clearKey() {
  keypadInput = "";
  updateKeypadDisplay();
}

function updateKeypadDisplay() {
  document.getElementById("keypad-display").value = "*".repeat(
    keypadInput.length
  );
}

function checkCode() {
  if (keypadInput === "1234") {
    pressButton("third");
    clearKey();
  } else {
    alert("Codice non valido");
    clearKey();
  }
}

function handleCoupleSwitch(checkbox) {
  if (checkbox.checked) {
    pressButton("first_start");
  } else {
    pressButton("first_stop");
  }
}

function handleSingleSwitch(checkbox) {
  if (checkbox.checked) {
    pressButton("second_start");
  } else {
    pressButton("second_stop");
  }
}

function simulate() {
  $.get(
    "/simulate",
    function (data) {
      $("#couples-board").empty();
      $("#singles-board").empty();

      data.couples.forEach(function (item) {
        $("#couples-board").append(
          `<li>${item[1]} - Tempo stimato: ${item[2]}</li>`
        );
      });

      data.singles.forEach(function (item) {
        $("#singles-board").append(
          `<li>${item[1]} - Tempo stimato: ${item[2]}</li>`
        );
      });
    },
    "json"
  );
}

function pressButton(button) {
  $.ajax({
    url: "/button_press",
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify({ button: button }),
    success: function () {
      updateStatus();
      simulate();
    },
  });
}

function updateStatus() {
  $.get("/get_status", function (data) {
    $("#alfa-state").text(data.alfa_status);
    $("#bravo-state").text(data.bravo_status);
    $("#alfa-remaining").text(data.alfa_remaining);
    $("#bravo-remaining").text(data.bravo_remaining);

    $("#alfa-status")
      .removeClass("occupied free")
      .addClass(data.alfa_status === "Occupata" ? "occupied" : "free");
    $("#bravo-status")
      .removeClass("occupied free")
      .addClass(data.bravo_status === "Occupata" ? "occupied" : "free");
  });
}

setInterval(updateStatus, 1000);
setInterval(simulate, 1000);

$(document).ready(function () {
  updateStatus();
  simulate();
});