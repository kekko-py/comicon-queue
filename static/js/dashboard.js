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

function updateDashboard() {
  fetch("/simulate")
    .then((response) => response.json())
    .then((data) => {
      // Aggiorna la coda coppie
      const couplesBoard = document.getElementById("couples-board");
      couplesBoard.innerHTML = "";
      data.couples.forEach((player) => {
        const timeDisplay =
          player.estimated_time === "PROSSIMO INGRESSO"
            ? "PROSSIMO INGRESSO"
            : formatTimeRome(player.estimated_time);
        const li = document.createElement("li");
        li.textContent = `${player.name} ${player.id} - Ingresso: ${timeDisplay}`;
        couplesBoard.appendChild(li);
      });

      // Aggiorna la coda singoli
      const singlesBoard = document.getElementById("singles-board");
      singlesBoard.innerHTML = "";
      data.singles.forEach((player) => {
        const timeDisplay =
          player.estimated_time === "PROSSIMO INGRESSO"
            ? "PROSSIMO INGRESSO"
            : formatTimeRome(player.estimated_time);
        const li = document.createElement("li");
        li.textContent = `${player.name} ${player.id} - Ingresso: ${timeDisplay}`;
        singlesBoard.appendChild(li);
      });

      // se non ci sono singoli ne coppie in coda nella board, resettami il prossimo giocatore
      if (data.couples.length === 0 && data.singles.length === 0) {
        document.getElementById("next-player-text").textContent = "Nessun Giocatore in coda";
      }

      // Aggiorna la coda Charlie
      const charlieBoard = document.getElementById("charlie-board");
      charlieBoard.innerHTML = "";
      data.charlie.forEach((player) => {
        const timeDisplay =
          player.estimated_time === "PROSSIMO INGRESSO"
            ? "PROSSIMO INGRESSO"
            : formatTimeRome(player.estimated_time);
        const li = document.createElement("li");
        li.textContent = `${player.name} ${player.id} - Ingresso: ${timeDisplay}`;
        charlieBoard.appendChild(li);
      });

      if (data.next_player_alfa_bravo_id && data.next_player_alfa_bravo_name) {
        document.getElementById("next-player-text").textContent =
          `${data.next_player_alfa_bravo_id}` || "nessun giocatore in coda";
      }

      document.getElementById("next-charlie-player").textContent =
        data.next_charlie_player || "-";

      // Aggiorna il giocatore corrente in Alfa
      if (data.current_player_alfa) {
        document.getElementById("current-player-alfa").textContent = data.current_player_alfa["id"];
        document.getElementById("alfa-duration").textContent = data.alfa_duration;
      } else {
        document.getElementById("current-player-alfa").textContent = "Nessun giocatore";
        document.getElementById("alfa-duration").textContent = "-";
      }

      // Aggiorna il giocatore corrente in Bravo
      if (data.current_player_bravo) {
        document.getElementById("current-player-bravo").textContent = data.current_player_bravo.id;
        document.getElementById("bravo-duration").textContent = data.bravo_duration;
      } else {
        document.getElementById("current-player-bravo").textContent = "Nessun giocatore";
        document.getElementById("bravo-duration").textContent = "-";
      }

      // Aggiorna il giocatore corrente in Charlie
      if (data.current_player_charlie) {
        document.getElementById("current-player-charlie").textContent = data.current_player_charlie.id;
        document.getElementById("charlie-duration").textContent = data.charlie_duration;
      } else {
        document.getElementById("current-player-charlie").textContent = "Nessun giocatore";
        document.getElementById("charlie-duration").textContent = "-";
      }

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

  // Aggiorna la visualizzazione degli skippati
  updateSkipped();
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
      .then((response) => {
        if (!response.ok) {
          throw new Error("Errore nella chiamata di skip");
        }
        return response.json();
      })
      .then(() => {
        fetch("/simulate")
          .then((response) => {
            if (!response.ok) {
              throw new Error("Errore nella chiamata di simulate");
            }
            return response.json();
          })
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
          })
          .catch((error) => {
            console.error("Errore durante la chiamata di simulate:", error);
          });
      })
      .catch((error) => {
        console.error("Errore durante la chiamata di skip:", error);
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
    url: "/restore_skipped_as_next",
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



// Aggiorna la visualizzazione degli skippati
function updateSkipped() {
  fetch("/get_skipped")
    .then((response) => response.json())
    .then((data) => {
      const skippedCouplesContainer = document.getElementById("skipped-couples-buttons");
      const skippedSinglesContainer = document.getElementById("skipped-singles-buttons");
      const skippedCharlieContainer = document.getElementById("skipped-charlie-buttons");

      skippedCouplesContainer.innerHTML = "";
      skippedSinglesContainer.innerHTML = "";
      skippedCharlieContainer.innerHTML = "";

      // Gestione coppie skippate
      if (data.couples && data.couples.length > 0) {
        data.couples.forEach((player) => {
          const button = document.createElement("button");
          button.className = "skipped-button couple";
          button.setAttribute("data-id", player.id);
          button.textContent = player.id;
          button.onclick = () => restoreSkipped(player.id);
          skippedCouplesContainer.appendChild(button);
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
          skippedSinglesContainer.appendChild(button);
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
          skippedCharlieContainer.appendChild(button);
        });
      }
    })
    .catch((error) => {
      console.error("Errore durante il recupero degli skipped:", error);
    });
}

// Assicurati che la funzione venga chiamata regolarmente
setInterval(() => {
  updateSkipped();
  updateDashboard();
}, 1000);
// Aggiorna la dashboard ogni secondo

$(document).ready(function () {
  updateSkipped();
  updateDashboard();
});

function updateBoards() {
  fetch("/simulate")
    .then((response) => response.json())
    .then((data) => {
      // Aggiorna la coda coppie
      const couplesBoard = document.getElementById("couples-board");
      couplesBoard.innerHTML = "";
      data.couples.forEach((player) => {
        const timeDisplay =
          player.estimated_time === "PROSSIMO INGRESSO"
            ? "PROSSIMO INGRESSO"
            : formatTimeRome(player.estimated_time);
        const li = document.createElement("li");
        li.textContent = `${player.name} ${player.id} - Ingresso: ${timeDisplay}`;
        couplesBoard.appendChild(li);
      });

      // Aggiorna la coda singoli
      const singlesBoard = document.getElementById("singles-board");
      singlesBoard.innerHTML = "";
      data.singles.forEach((player) => {
        const timeDisplay =
          player.estimated_time === "PROSSIMO INGRESSO"
            ? "PROSSIMO INGRESSO"
            : formatTimeRome(player.estimated_time);
        const li = document.createElement("li");
        li.textContent = `${player.name} ${player.id} - Ingresso: ${timeDisplay}`;
        singlesBoard.appendChild(li);
      });

      // se non ci sono singoli ne coppie in coda nella board, resettami il prossimo giocatore
      if (data.couples.length === 0 && data.singles.length === 0) {
        document.getElementById("next-player-text").textContent = "Nessun Giocatore in coda";
      }

      // Aggiorna la coda Charlie
      const charlieBoard = document.getElementById("charlie-board");
      charlieBoard.innerHTML = "";
      data.charlie.forEach((player) => {
        const timeDisplay =
          player.estimated_time === "PROSSIMO INGRESSO"
            ? "PROSSIMO INGRESSO"
            : formatTimeRome(player.estimated_time);
        const li = document.createElement("li");
        li.textContent = `${player.name} ${player.id} - Ingresso: ${timeDisplay}`;
        charlieBoard.appendChild(li);
      });

      if (data.next_player_alfa_bravo_id && data.next_player_alfa_bravo_name) {
        document.getElementById("next-player-text").textContent =
          `${data.next_player_alfa_bravo_id}` || "nessun giocatore in coda";
      }

      document.getElementById("next-charlie-player").textContent =
        data.next_charlie_player || "-";

      // Aggiorna il giocatore corrente in Alfa
      if (data.current_player_alfa) {
        document.getElementById("current-player-alfa").textContent = data.current_player_alfa["id"];
        document.getElementById("alfa-duration").textContent = data.alfa_duration;
      } else {
        document.getElementById("current-player-alfa").textContent = "Nessun giocatore";
        document.getElementById("alfa-duration").textContent = "-";
      }

      // Aggiorna il giocatore corrente in Bravo
      if (data.current_player_bravo) {
        document.getElementById("current-player-bravo").textContent = data.current_player_bravo.id;
        document.getElementById("bravo-duration").textContent = data.bravo_duration;
      } else {
        document.getElementById("current-player-bravo").textContent = "Nessun giocatore";
        document.getElementById("bravo-duration").textContent = "-";
      }

      // Aggiorna il giocatore corrente in Charlie
      if (data.current_player_charlie) {
        document.getElementById("current-player-charlie").textContent = data.current_player_charlie.id;
        document.getElementById("charlie-duration").textContent = data.charlie_duration;
      } else {
        document.getElementById("current-player-charlie").textContent = "Nessun giocatore";
        document.getElementById("charlie-duration").textContent = "-";
      }

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
