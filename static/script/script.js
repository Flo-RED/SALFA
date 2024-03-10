var socketio = io();

socketio.on("message", (data) => {

  // log fucntion
  function log(text) {
    const log_element = document.querySelector("#log > ul");
    log_element.innerHTML += "<li>" + text + "</li>"
  }

  // player join / left
  if (["JOIN", "LEFT"].includes(data.message)) {
    const players_list = document.querySelector("#players > ul");
    players_list.innerHTML = "";
    data.players.forEach(player => {
      players_list.innerHTML +=  "<li>" + player + "</li>";
    });
    log(data.name + " joined!")
  }

});
