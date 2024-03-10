from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "flored"
socketio = SocketIO(app)

rooms = {}

# function : generate room code
def generate_code():
  while True:
    code = ""
    for _ in range(4):
      code += str(random.choice(range(10)))
    if code not in rooms:
      break
  return code

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: INDEX
@app.route("/", methods=["POST", "GET"])
def index():
  session.clear()
  if request.method == "POST":
    name = request.form.get("name")
    code = request.form.get("code")
    join = request.form.get("join", False)
    create = request.form.get("create", False)
    room = code
    # if name is empty
    if not name:
      return render_template("index.html", error="Enter name", name=name, code=code)
    # if code is empty
    if join != False and not code:
      return render_template("index.html", error="Enter code", name=name, code=code)
    # if join room
    if join != False and code not in rooms:
      return render_template("index.html", error="Room does not exist", name=name, code=code)
    # if create room
    if create != False:
      room = generate_code()
      rooms[room] = {"members": 0, "players": []}

    session["room"] = room
    session["name"] = name
    return redirect(url_for("room"))

  return render_template("index.html")

# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: ROOM
@app.route("/room")
def room():
  room = session.get("room")
  name = session.get("name")
  if room is None or name is None or room not in rooms:
    return redirect(url_for("index"))
  
  return render_template("room.html", code=room)

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: CONNECT
@socketio.on("connect")
def connect(auth):
  room = session.get("room")
  name = session.get("name")
  if not room or not name:
    return
  if room not in rooms:
    leave_room(room)
    return

  join_room(room)
  rooms[room]["members"] += 1
  rooms[room]["players"] += [name]
  send({"name": name, "message": "JOIN", "players": rooms[room]["players"]}, to=room)
  print(f":::: {name} joined {room}")

# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: DISCONNECT
@socketio.on("disconnect")
def disconnect():
  room = session.get("room")
  name = session.get("name")
  leave_room(room)

  if room in rooms:
    rooms[room]["members"] -= 1
    rooms[room]["players"].remove(name)
    if rooms[room]["members"] <= 0:
      del rooms[room]

  send({"name": name, "message": "LEFT", "players": rooms[room]["players"]}, to=room)
  print(f":::: {name} left {room}")


if __name__ == "__main__":
  socketio.run(app, debug=True)
