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
      if (couplesBoard) {
        couplesBoard.innerHTML = "";
        data.couples.forEach((player) => {
          const timeDisplay =
            player.estimated_time === "PROSSIMO INGRESSO"
              ? "PROSSIMO INGRESSO"
              : formatTimeRome(player.estimated_time);
          const li = document.createElement("li");
          li.innerHTML = `${player.id} - Ingresso: ${timeDisplay} <button class="trash-button" onclick="deletePlayer('${player.id}')"><img class="trash-icon" src="/static/icons/trash.svg" alt="Delete"></button>`;
          couplesBoard.appendChild(li);
        });
      }

      // Aggiorna la coda singoli
      const singlesBoard = document.getElementById("singles-board");
      if (singlesBoard) {
        singlesBoard.innerHTML = "";
        data.singles.forEach((player) => {
          const timeDisplay =
            player.estimated_time === "PROSSIMO INGRESSO"
              ? "PROSSIMO INGRESSO"
              : formatTimeRome(player.estimated_time);
          const li = document.createElement("li");
          li.innerHTML = `${player.id} - Ingresso: ${timeDisplay} <button class="trash-button" onclick="deletePlayer('${player.id}')"><img class="trash-icon" src="/static/icons/trash.svg" alt="Delete"></button>`;
          singlesBoard.appendChild(li);
        });
      }

      // se non ci sono singoli ne coppie in coda nella board, resettami il prossimo giocatore
      if (data.couples.length === 0 && data.singles.length === 0) {
        const nextPlayerAlfaBravoText = document.getElementById("next-player-alfa-bravo-text");
        if (nextPlayerAlfaBravoText) {
          nextPlayerAlfaBravoText.textContent = "Nessun Giocatore in coda";
        }
      }

      // se non ci sono charlie in coda nella board, resettami il prossimo giocatore
      if (data.charlie.length === 0) {
        const nextCharlieText = document.getElementById("next-charlie-text");
        if (nextCharlieText) {
          nextCharlieText.textContent = "Nessun Giocatore in coda";
        }
      }


      // Aggiorna la coda Charlie
      const charlieBoard = document.getElementById("charlie-board");
      if (charlieBoard) {
        charlieBoard.innerHTML = "";
        data.charlie.forEach((player) => {
          const timeDisplay =
            player.estimated_time === "PROSSIMO INGRESSO"
              ? "PROSSIMO INGRESSO"
              : formatTimeRome(player.estimated_time);
          const li = document.createElement("li");
          li.innerHTML = `${player.id} - Ingresso: ${timeDisplay} <button class="trash-button" onclick="deletePlayer('${player.id}')"><img class="trash-icon" src="/static/icons/trash.svg" alt="Delete"></button>`;
          charlieBoard.appendChild(li);
        });
      }

      const nextPlayerAlfaBravoText = document.getElementById("next-player-alfa-bravo-text");
      if (nextPlayerAlfaBravoText && data.next_player_alfa_bravo_id && data.next_player_alfa_bravo_name) {
        nextPlayerAlfaBravoText.textContent =
          `${data.next_player_alfa_bravo_id}` || "nessun giocatore in coda";
      }

      const nextCharlieText = document.getElementById("next-charlie-text");
      if (nextCharlieText && data.next_player_charlie_id && data.next_player_charlie_name) {
        nextCharlieText.textContent =
          `${data.next_player_charlie_id}` || "nessun giocatore in coda";
      }

      const nextCharliePlayer = document.getElementById("next-charlie-player");
      if (nextCharliePlayer) {
        nextCharliePlayer.textContent = data.next_charlie_player || "-";
      }

      // Aggiorna il giocatore corrente in Alfa
      const currentPlayerAlfa = document.getElementById("current-player-alfa");
      const alfaDuration = document.getElementById("alfa-duration");
      if (currentPlayerAlfa && alfaDuration) {
        if (data.current_player_alfa) {
          currentPlayerAlfa.textContent = data.current_player_alfa["id"];
          alfaDuration.textContent = data.alfa_duration;
        } else {
          currentPlayerAlfa.textContent = "Nessun giocatore";
          alfaDuration.textContent = "-";
        }
      }

      // Aggiorna il giocatore corrente in Bravo
      const currentPlayerBravo = document.getElementById("current-player-bravo");
      const bravoDuration = document.getElementById("bravo-duration");
      if (currentPlayerBravo && bravoDuration) {
        if (data.current_player_bravo) {
          currentPlayerBravo.textContent = data.current_player_bravo.id;
          bravoDuration.textContent = data.bravo_duration;
        } else {
          currentPlayerBravo.textContent = "Nessun giocatore";
          bravoDuration.textContent = "-";
        }
      }

      // Aggiorna il giocatore corrente in Charlie
      const currentPlayerCharlie = document.getElementById("current-player-charlie");
      const charlieDuration = document.getElementById("charlie-duration");
      if (currentPlayerCharlie && charlieDuration) {
        if (data.current_player_charlie) {
          currentPlayerCharlie.textContent = data.current_player_charlie.id;
          charlieDuration.textContent = data.charlie_duration;
        } else {
          currentPlayerCharlie.textContent = "Nessun giocatore";
          charlieDuration.textContent = "-";
        }
      }

      // Aggiorna lo stato e il colore della card ALFA
      const alfaState = $("#alfa-state");
      const alfaRemaining = $("#alfa-remaining");
      const alfaStatus = $("#alfa-status");
      if (alfaState && alfaRemaining && alfaStatus) {
        alfaState.text(data.alfa_status);
        alfaRemaining.text(data.alfa_remaining);
        alfaStatus
          .removeClass("occupied free")
          .addClass(data.alfa_status === "Occupata" ? "occupied" : "free");
      }

      // Aggiorna lo stato e il colore della card BRAVO
      const bravoState = $("#bravo-state");
      const bravoRemaining = $("#bravo-remaining");
      const bravoStatus = $("#bravo-status");
      if (bravoState && bravoRemaining && bravoStatus) {
        bravoState.text(data.bravo_status);
        bravoRemaining.text(data.bravo_remaining);
        bravoStatus
          .removeClass("occupied free")
          .addClass(data.bravo_status === "Occupata" ? "occupied" : "free");
      }

      // Aggiorna lo stato e il colore della card CHARLIE
      const charlieState = $("#charlie-state");
      const charlieRemaining = $("#charlie-remaining");
      const charlieStatus = $("#charlie-status");
      if (charlieState && charlieRemaining && charlieStatus) {
        charlieState.text(data.charlie_status);
        charlieRemaining.text(data.charlie_remaining);
        charlieStatus
          .removeClass("occupied free")
          .addClass(data.charlie_status === "Occupata" ? "occupied" : "free");
      }
    });

  // Aggiorna la visualizzazione degli skippati
  updateSkipped();
}

function skipNextPlayerAlfaBravo() {
  const nextPlayer = document.getElementById("next-player-alfa-bravo-text").textContent;
  if (nextPlayer && nextPlayer !== "-") {
    fetch("/skip_next_player_alfa_bravo", {
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
              document.getElementById("next-player-alfa-bravo-text").textContent =
                data.couples[0][1];
            }

            // Se non ci sono coppie, controlla i singoli
            else if (data.singles && data.singles.length > 0) {
              document.getElementById("next-player-alfa-bravo-text").textContent =
                data.singles[0][1];
            }
            // Se non ci sono né coppie né singoli
            else {
              document.getElementById("next-player-alfa-bravo-text").textContent = "-";
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

function skipNextPlayerCharlie() {
  const nextPlayer = document.getElementById("next-charlie-text").textContent;
  if (nextPlayer && nextPlayer !== "-") {
    fetch("/skip_charlie_player", {
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
            if (data.charlie && data.charlie.length > 0) {
              document.getElementById("next-charlie-text").textContent =
                data.charlie[0][1];
            } else {
              document.getElementById("next-charlie-text").textContent = "-";
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
  const nextPlayer = document.getElementById("next-charlie-text").textContent;
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
      if (couplesBoard) {
        couplesBoard.innerHTML = "";
        data.couples.forEach((player) => {
          const timeDisplay =
            player.estimated_time === "PROSSIMO INGRESSO"
              ? "PROSSIMO INGRESSO"
              : formatTimeRome(player.estimated_time);
          const li = document.createElement("li");
          li.innerHTML = `${player.id} - Ingresso: ${timeDisplay} <button class="trash-button" onclick="deletePlayer('${player.id}')"><img class="trash-icon" src="/static/icons/trash.svg" alt="Delete"></button>`;
          couplesBoard.appendChild(li);
        });
      }

      // Aggiorna la coda singoli
      const singlesBoard = document.getElementById("singles-board");
      if (singlesBoard) {
        singlesBoard.innerHTML = "";
        data.singles.forEach((player) => {
          const timeDisplay =
            player.estimated_time === "PROSSIMO INGRESSO"
              ? "PROSSIMO INGRESSO"
              : formatTimeRome(player.estimated_time);
          const li = document.createElement("li");
          li.innerHTML = `${player.id} - Ingresso: ${timeDisplay} <button class="trash-button" onclick="deletePlayer('${player.id}')"><img class="trash-icon" src="/static/icons/trash.svg" alt="Delete"></button>`;
          singlesBoard.appendChild(li);
        });
      }

      // se non ci sono singoli ne coppie in coda nella board, resettami il prossimo giocatore
      if (data.couples.length === 0 && data.singles.length === 0) {
        const nextPlayerAlfaBravoText = document.getElementById("next-player-alfa-bravo-text");
        if (nextPlayerAlfaBravoText) {
          nextPlayerAlfaBravoText.textContent = "Nessun Giocatore in coda";
        }
      }

      // Aggiorna la coda Charlie
      const charlieBoard = document.getElementById("charlie-board");
      if (charlieBoard) {
        charlieBoard.innerHTML = "";
        data.charlie.forEach((player) => {
          const timeDisplay =
            player.estimated_time === "PROSSIMO INGRESSO"
              ? "PROSSIMO INGRESSO"
              : formatTimeRome(player.estimated_time);
          const li = document.createElement("li");
          li.innerHTML = `${player.id} - Ingresso: ${timeDisplay} <button onclick="deletePlayer('${player.id}')"><img src="/static/icons/trash.svg" alt="Delete"></button>`;
          charlieBoard.appendChild(li);
        });
      }

      const nextPlayerAlfaBravoText = document.getElementById("next-player-alfa-bravo-text");
      if (nextPlayerAlfaBravoText && data.next_player_alfa_bravo_id && data.next_player_alfa_bravo_name) {
        nextPlayerAlfaBravoText.textContent =
          `${data.next_player_alfa_bravo_id}` || "nessun giocatore in coda";
      }

      const nextCharlieText = document.getElementById("next-charlie-text");
      if (nextCharlieText && data.next_player_charlie_id && data.next_player_charlie_name) {
        nextCharlieText.textContent =
          `${data.next_player_charlie_id}` || "nessun giocatore in coda";
      }

      // Aggiorna il giocatore corrente in Alfa
      const currentPlayerAlfa = document.getElementById("current-player-alfa");
      const alfaDuration = document.getElementById("alfa-duration");
      if (currentPlayerAlfa && alfaDuration) {
        if (data.current_player_alfa) {
          currentPlayerAlfa.textContent = data.current_player_alfa["id"];
          alfaDuration.textContent = data.alfa_duration;
        } else {
          currentPlayerAlfa.textContent = "Nessun giocatore";
          alfaDuration.textContent = "-";
        }
      }

      // Aggiorna il giocatore corrente in Bravo
      const currentPlayerBravo = document.getElementById("current-player-bravo");
      const bravoDuration = document.getElementById("bravo-duration");
      if (currentPlayerBravo && bravoDuration) {
        if (data.current_player_bravo) {
          currentPlayerBravo.textContent = data.current_player_bravo.id;
          bravoDuration.textContent = data.bravo_duration;
        } else {
          currentPlayerBravo.textContent = "Nessun giocatore";
          bravoDuration.textContent = "-";
        }
      }

      // Aggiorna il giocatore corrente in Charlie
      const currentPlayerCharlie = document.getElementById("current-player-charlie");
      const charlieDuration = document.getElementById("charlie-duration");
      if (currentPlayerCharlie && charlieDuration) {
        if (data.current_player_charlie) {
          currentPlayerCharlie.textContent = data.current_player_charlie.id;
          charlieDuration.textContent = data.charlie_duration;
        } else {
          currentPlayerCharlie.textContent = "Nessun giocatore";
          charlieDuration.textContent = "-";
        }
      }

      // Aggiorna lo stato e il colore della card ALFA
      const alfaState = $("#alfa-state");
      const alfaRemaining = $("#alfa-remaining");
      const alfaStatus = $("#alfa-status");
      if (alfaState && alfaRemaining && alfaStatus) {
        alfaState.text(data.alfa_status);
        alfaRemaining.text(data.alfa_remaining);
        alfaStatus
          .removeClass("occupied free")
          .addClass(data.alfa_status === "Occupata" ? "occupied" : "free");
      }

      // Aggiorna lo stato e il colore della card BRAVO
      const bravoState = $("#bravo-state");
      const bravoRemaining = $("#bravo-remaining");
      const bravoStatus = $("#bravo-status");
      if (bravoState && bravoRemaining && bravoStatus) {
        bravoState.text(data.bravo_status);
        bravoRemaining.text(data.bravo_remaining);
        bravoStatus
          .removeClass("occupied free")
          .addClass(data.bravo_status === "Occupata" ? "occupied" : "free");
      }

      // Aggiorna lo stato e il colore della card CHARLIE
      const charlieState = $("#charlie-state");
      const charlieRemaining = $("#charlie-remaining");
      const charlieStatus = $("#charlie-status");
      if (charlieState && charlieRemaining && charlieStatus) {
        charlieState.text(data.charlie_status);
        charlieRemaining.text(data.charlie_remaining);
        charlieStatus
          .removeClass("occupied free")
          .addClass(data.charlie_status === "Occupata" ? "occupied" : "free");
      }
    });
}

function addCharliePlayer() {
  const name = document.getElementById("playerName").value;
  const id = document.getElementById("playerId").value;
  fetch("/add_charlie_player", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name: name, id: id }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        alert("Giocatore aggiunto con successo!");
        updateDashboard(); // Update the dashboard to reflect the new Charlie player
      } else {
        alert("Errore nell'aggiunta del giocatore.");
      }
    });
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
        alert("Errore nella cancellazione del giocatore.");
      }
    });
}
