import json
import os
import threading
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sock import Sock
from database import init_db, create_user, authenticate_user, username_exists, add_user_to_default_rooms, get_rooms, get_user_room_ids, get_messages, save_message

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "development-only-change-before-deployment")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
sock = Sock(app)
init_db()

connections = {}
connections_lock = threading.RLock()

def send_json(ws, payload):
    try:
        ws.send(json.dumps(payload))
        return True
    except Exception:
        return False

def room_connections(room_id):
    with connections_lock:
        return [c for c in connections.values() if c["room_id"] == room_id]

def broadcast(room_id, payload):
    with connections_lock:
        recipients = [c["ws"] for c in connections.values() if c["room_id"] == room_id]
    for ws in recipients:
        send_json(ws, payload)

def presence(room_id):
    if room_id is not None:
        count = len({c["user_id"] for c in room_connections(room_id)})
        broadcast(room_id, {"type": "online_count", "room_id": room_id, "count": count})

@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

@app.route("/")
def index():
    return redirect(url_for("chat" if session.get("user_id") else "login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        error = None
        if not username or not password or not confirm:
            error = "Please complete every field."
        elif not 3 <= len(username) <= 20:
            error = "Username must be between 3 and 20 characters."
        elif not username.replace("_", "").isalnum():
            error = "Use only letters, numbers and underscores."
        elif len(password) < 8:
            error = "Password must contain at least 8 characters."
        elif password != confirm:
            error = "The passwords do not match."
        elif username_exists(username):
            error = "That username is already taken."
        if error:
            flash(error, "error")
        else:
            user_id = create_user(username, password)
            if user_id:
                add_user_to_default_rooms(user_id)
                flash("Your account is ready. Please sign in.", "success")
                return redirect(url_for("login"))
            flash("Unable to create the account. Please try again.", "error")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("chat"))
    if request.method == "POST":
        user = authenticate_user(request.form.get("username", "").strip(), request.form.get("password", ""))
        if user:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("chat"))
        flash("Incorrect username or password.", "error")
    return render_template("login.html")

@app.route("/chat")
def chat():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return render_template("chat.html", username=session["username"], rooms=get_rooms())

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("login"))

@sock.route("/ws")
def websocket_chat(ws):
    user_id, username = session.get("user_id"), session.get("username")
    if not user_id or not username:
        ws.close()
        return
    key = id(ws)
    with connections_lock:
        connections[key] = {"ws": ws, "user_id": user_id, "username": username, "room_id": None}
    current_room = None
    try:
        while True:
            raw = ws.receive()
            if raw is None:
                break
            if len(raw) > 6000:
                send_json(ws, {"type": "error", "message": "Request is too large."})
                continue
            try:
                data = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                send_json(ws, {"type": "error", "message": "Invalid message format."})
                continue
            if not isinstance(data, dict):
                send_json(ws, {"type": "error", "message": "Invalid request."})
                continue
            if data.get("type") == "join":
                try:
                    room_id = int(data.get("room_id"))
                except (TypeError, ValueError):
                    send_json(ws, {"type": "error", "message": "Invalid room."})
                    continue
                if room_id not in get_user_room_ids(user_id):
                    send_json(ws, {"type": "error", "message": "You do not have access to that room."})
                    continue
                old_room = current_room
                current_room = room_id
                with connections_lock:
                    connections[key]["room_id"] = room_id
                if old_room is not None:
                    presence(old_room)
                send_json(ws, {"type": "history", "room_id": room_id, "messages": get_messages(room_id, 100)})
                presence(room_id)
            elif data.get("type") == "message":
                if current_room is None:
                    send_json(ws, {"type": "error", "message": "Choose a channel first."})
                    continue
                content = data.get("content", "")
                if not isinstance(content, str):
                    send_json(ws, {"type": "error", "message": "Message must be text."})
                    continue
                content = content.strip()
                if not content:
                    continue
                if len(content) > 1000:
                    send_json(ws, {"type": "error", "message": "Messages are limited to 1,000 characters."})
                    continue
                message = save_message(user_id, current_room, content)
                broadcast(current_room, {"type": "message", "message": message})
            elif data.get("type") == "ping":
                send_json(ws, {"type": "pong"})
            else:
                send_json(ws, {"type": "error", "message": "Unknown event."})
    except Exception:
        pass
    finally:
        with connections_lock:
            connections.pop(key, None)
        presence(current_room)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, threaded=True)
