function formatTimeRome(date) {
  if (!date) return "N/D";

  // Crea un formatter per l'ora di Roma
  const options = {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZone: "Europe/Rome",
  };

  return new Date(date).toLocaleTimeString("it-IT", options);
}

function updateStatus() {
  $.get("/get_status", function (data) {
    // Aggiorna lo stato e il colore della card ALFA
    $("#alfa-state").text(data.alfa_status);
    $("#alfa-remaining").text(data.alfa_remaining);
    $("#alfa-status")
      .removeClass("occupied free")
      .addClass(data.alfa_status === "Occupata" ? "occupied" : "free");

    // Aggiorna lo stato e il colore della card BRAVO
    $("#bravo-state").text(data.bravo_status);
    $("#bravo-remaining").text(data.bravo_remaining);
    $("#bravo-status")
      .removeClass("occupied free")
      .addClass(data.bravo_status === "Occupata" ? "occupied" : "free");

    // Aggiorna lo stato e il colore della card CHARLIE
    $("#charlie-state").text(data.charlie_status);
    $("#charlie-remaining").text(data.charlie_remaining);
    $("#charlie-status")
      .removeClass("occupied free")
      .addClass(data.charlie_status === "Occupata" ? "occupied" : "free");
  });
}

function updateBoards() {
  $.get("/simulate", function (data) {
    $("#couples-board").empty();
    $("#singles-board").empty();

    // Aggiorna i tabelloni
    data.couples.forEach(function (item) {
      let timeDisplay =
        item[2] === "PROSSIMO INGRESSO"
          ? "PROSSIMO INGRESSO"
          : formatTimeRome(item[2]);
      $("#couples-board").append(
        `<li>${item[1]} - Ingresso: ${timeDisplay}</li>`
      );
    });

    data.singles.forEach(function (item) {
      let timeDisplay =
        item[2] === "PROSSIMO INGRESSO"
          ? "PROSSIMO INGRESSO"
          : formatTimeRome(item[2]);
      $("#singles-board").append(
        `<li>${item[1]} - Ingresso: ${timeDisplay}</li>`
      );
    });

    // Gestisci la notifica del prossimo giocatore
    if (data.next_player) {
      $("#next-player-notification")
        .removeClass("hidden")
        .addClass("highlight");
      $("#next-player-text").text(data.next_player);
    } else {
      $("#next-player-notification")
        .addClass("hidden")
        .removeClass("highlight");
      $("#next-player-text").text("-");
    }
  });
}

function skipNextPlayer() {
  const nextPlayer = document.getElementById("next-player-text").textContent;
  if (nextPlayer && nextPlayer !== "-") {
    fetch("/skip_next_player", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ id: nextPlayer }),
    })
      .then((response) => response.json())
      .then(() => {
        fetch("/simulate")
          .then((response) => response.json())
          .then((data) => {
            // Prima controlla se ci sono coppie
            if (data.couples && data.couples.length > 0) {
              document.getElementById("next-player-text").textContent =
                data.couples[0][1];
            }
            // Se non ci sono coppie, controlla i singoli
            else if (data.singles && data.singles.length > 0) {
              document.getElementById("next-player-text").textContent =
                data.singles[0][1];
            }
            // Se non ci sono né coppie né singoli
            else {
              document.getElementById("next-player-text").textContent = "-";
            }
            updateDashboard();
            updateSkipped();
          });
      });
  }
}

function updateSkippedList() {
  $.get("/get_skipped", function (data) {
    const skippedList = $("#skipped-list");
    skippedList.empty();

    data.couples.forEach(function (couple) {
      skippedList.append(`
                  <div class="skipped-item couple" onclick="restoreSkipped('${couple.id}')">
                      ${couple.id}
                  </div>
              `);
    });

    data.singles.forEach(function (single) {
      skippedList.append(`
                  <div class="skipped-item single" onclick="restoreSkipped('${single.id}')">
                      ${single.id}
                  </div>
              `);
    });
  });
}

function restoreSkipped(playerId) {
  console.log("Tentativo di ripristino giocatore:", playerId);
  $.ajax({
    url: "/restore_skipped",
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify({ id: playerId }),
    success: function (response) {
      console.log("Giocatore ripristinato con successo:", playerId);
      console.log("Risposta server:", response);
      updateSkippedList();
      updateBoards();
    },
    error: function (error) {
      console.error("Errore durante il ripristino del giocatore:", error);
    },
  });
}

function updateDashboard() {
  fetch("/simulate")
    .then((response) => response.json())
    .then((data) => {
      // Aggiorna la coda coppie
      const couplesBoard = document.getElementById("couples-board");
      couplesBoard.innerHTML = "";
      data.couples.forEach((player) => {
        const timeDisplay =
          player[2] === "PROSSIMO INGRESSO"
            ? "PROSSIMO INGRESSO"
            : formatTimeRome(player[2]);
        const li = document.createElement("li");
        li.textContent = `${player[1]} - Ingresso: ${timeDisplay}`;
        couplesBoard.appendChild(li);
      });

      // Aggiorna la coda singoli
      const singlesBoard = document.getElementById("singles-board");
      singlesBoard.innerHTML = "";
      data.singles.forEach((player) => {
        const timeDisplay =
          player[2] === "PROSSIMO INGRESSO"
            ? "PROSSIMO INGRESSO"
            : formatTimeRome(player[2]);
        const li = document.createElement("li");
        li.textContent = `${player[1]} - Ingresso: ${timeDisplay}`;
        singlesBoard.appendChild(li);
      });

      // Aggiorna la coda Charlie
      const charlieBoard = document.getElementById("charlie-board");
      charlieBoard.innerHTML = "";
      data.charlie.forEach((player) => {
        const timeDisplay =
          player[2] === "PROSSIMO INGRESSO"
            ? "PROSSIMO INGRESSO"
            : formatTimeRome(player[2]);
        const li = document.createElement("li");
        li.textContent = `${player[1]} - Ingresso: ${timeDisplay}`;
        charlieBoard.appendChild(li);
      });

      // Aggiorna i prossimi giocatori
      document.getElementById("next-player-text").textContent =
        data.next_player || "-";
      document.getElementById("next-charlie-player").textContent =
        data.next_charlie_player || "-";
    });

  // Aggiorna la visualizzazione degli skippati
  updateSkipped();
}

function skipCharliePlayer() {
  fetch("/skip_charlie_player", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then(() => updateDashboard());
}

// Aggiorna la dashboard ogni secondo
setInterval(updateDashboard, 1000);

// Aggiorna lo stato ogni secondo
setInterval(updateStatus, 1000);
updateDashboard();

// Aggiorna lo stato all'avvio della pagina
$(document).ready(function () {
  updateStatus();
  updateDashboard();
});

// Aggiorna la visualizzazione degli skippati
function updateSkipped() {
  fetch("/get_skipped")
    .then((response) => response.json())
    .then((data) => {
      const skippedContainer = document.querySelector(".skipped-buttons");
      skippedContainer.innerHTML = "";

      // Gestione coppie skippate
      if (data.couples && data.couples.length > 0) {
        data.couples.forEach((player) => {
          const button = document.createElement("button");
          button.className = "skipped-button couple";
          button.setAttribute("data-id", player.id);
          button.textContent = player.id;
          button.onclick = () => restoreSkipped(player.id);
          skippedContainer.appendChild(button);
        });
      }

      // Gestione singoli skippati
      if (data.singles && data.singles.length > 0) {
        data.singles.forEach((player) => {
          const button = document.createElement("button");
          button.className = "skipped-button single";
          button.setAttribute("data-id", player.id);
          button.textContent = player.id;
          button.onclick = () => restoreSkipped(player.id);
          skippedContainer.appendChild(button);
        });
      }

      // Gestione charlie skippati
      if (data.charlie && data.charlie.length > 0) {
        data.charlie.forEach((player) => {
          const button = document.createElement("button");
          button.className = "skipped-button charlie";
          button.setAttribute("data-id", player.id);
          button.textContent = player.id;
          button.onclick = () => restoreSkipped(player.id);
          skippedContainer.appendChild(button);
        });
      }
    })
    .catch((error) => {
      console.error("Errore durante il recupero degli skipped:", error);
    });
}

// Assicurati che la funzione venga chiamata regolarmente
setInterval(updateSkipped, 1000);
$(document).ready(function () {
  updateSkipped();
});