var songs = [
    [id=2, titulo="prueba", procesado=false, estilo="me da igual"]];

var btn = document.querySelector("#btn");
btn.onclick = function(ev){
    actualizarsongs();
}

function actualizarsongs() {
    var tBody = document.querySelector("tbody#tablesongs");

    var filas = "";

    for (var indice in songs) {
        var song = songs[indice];

        filas += "<tr>" +
            "<td>" + song.id + "</td>" +
            "<td>" + song.titulo + "</td>" +
            "<td>" + song.procesado + "</td>" +
            "<td>" + song.estilo + "</td>" +
            "</tr>";
    };
    tBody.innerHTML = filas;
}