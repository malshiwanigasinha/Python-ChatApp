from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Python dictionary to store connected users. Key is socket ID, value is username and avatar URL
users = {}

@app.route('/')
def index():
    return render_template('index.html')

# Listening for the connect event
@socketio.on("user_info")
def handle_user_info(data):
    username = data["username"]
    gender = data["gender"]
    
    # Validate gender to avoid issues
    if gender not in ["girl", "boy"]:
        gender = "boy"  # Default to "boy" if invalid
    
    avatar_url = f"https://avatar.iran.liara.run/public/{gender}?username={username}"

    # Store user info by their socket ID
    users[request.sid] = {"username": username, "avatar": avatar_url}

    # Inform other users that a new user has joined
    emit("user_joined", {"username": username, "avatar": avatar_url}, broadcast=True)

    # Set the username for the current user
    emit("set_username", {"username": username})

@socketio.on("disconnect")
def handle_disconnect():
    user = users.pop(request.sid, None)
    if user:
        emit("user_left", {"username": user["username"]}, broadcast=True)

@socketio.on("send_message")
def handle_message(data):
    user = users.get(request.sid)
    if user:
        emit("new_message", {
            "username": user["username"],
            "avatar": user["avatar"],
            "message": data["message"]
        }, broadcast=True)

@socketio.on("update_username")
def handle_update_username(data):
    old_username = users[request.sid]["username"]
    new_username = data["username"]
    users[request.sid]["username"] = new_username

    emit("username_updated", {
        "old_username": old_username,
        "new_username": new_username
    }, broadcast=True)

if __name__ == "__main__":
    socketio.run(app)
