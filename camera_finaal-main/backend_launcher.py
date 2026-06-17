from flask import Flask, jsonify
import subprocess
import os

app = Flask(__name__)

process = None

PYTHON_PATH = r"C:\Users\divya\AppData\Local\Programs\Python\Python311\python.exe"
SCRIPT_PATH = r"C:\temp\Emoheal\main_with_spotify.py"

@app.route("/start")
def start_backend():
    global process

    if process is None:
        process = subprocess.Popen([PYTHON_PATH, SCRIPT_PATH])
        print("✅ Emotion Player Started")
        return jsonify({"status": "started"})
    else:
        return jsonify({"status": "already running"})

@app.route("/stop")
def stop_backend():
    global process

    if process is not None:
        process.terminate()   # 💥 camera process kill
        process = None
        print("🛑 Emotion Player Stopped")
        return jsonify({"status": "stopped"})
    else:
        return jsonify({"status": "not running"})

if __name__ == "__main__":
    app.run(port=5000)