function formatTimeRome(date) {
    // Se il valore è nullo o "N/D", restituisci "N/D"
    if (!date || date === "N/D") return "N/D";

    // Se il valore è una stringa come "PROSSIMO INGRESSO", restituiscila così com'è
    if (isNaN(Date.parse(date))) return date;

    // Converti la data nel formato corretto per il fuso orario di Roma
    const options = {
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
        timeZone: "Europe/Rome",
    };

    return new Date(date).toLocaleTimeString("it-IT", options);
}


function loadQueue() {
    $.getJSON("/simulate", function(data) {
        $("#couples-list, #singles-list, #charlie-list").empty();

        data.couples.forEach((player, index) => {
            $("#couples-list").append(`<tr>
                <td>${index + 1}</td>
                <td>${player.id}</td>
                <td>${formatTimeRome(player.estimated_time)}</td>
            </tr>`);
        });

        data.singles.forEach((player, index) => {
            $("#singles-list").append(`<tr>
                <td>${index + 1}</td>
                <td>${player.id}</td>
                <td>${formatTimeRome(player.estimated_time)}</td>
            </tr>`);
        });

        data.charlie.forEach((player, index) => {
            $("#charlie-list").append(`<tr>
                <td>${index + 1}</td>
                <td>${player.id}</td>
                <td>${formatTimeRome(player.estimated_time)}</td>
            </tr>`);
        });
    });
}

// Aggiorna la lista ogni 5 secondi
setInterval(loadQueue, 5000);
loadQueue();

// Gestione delle tab
$(".tab").click(function () {
    $(".tab").removeClass("active");
    $(".content").removeClass("active");
    $(this).addClass("active");
    $("#" + $(this).data("tab")).addClass("active");
});
