from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from celery import chain
from demo_integration import extract_data, json_to_csv, store_csv, update_visualization
import time  # Import time for delays

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

shared_logs = []  # Local log list

def log_to_frontend(message):
    print(message)
    shared_logs.append(message)
    socketio.emit('log', {'message': message})

# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route("/")
def main_ui():
    return render_template("main.html")


@socketio.on('start_pipeline')
def handle_start_pipeline():
    log_to_frontend("🚀 Starting pipeline...")

    task_chain = chain(
        extract_data.s(),
        json_to_csv.s(),
        store_csv.s(),
        update_visualization.s()
    )
    task_chain.apply_async()

    # Start delayed logging in a background thread
    socketio.start_background_task(target=delayed_logs)

@app.route('/logs')
def get_logs():
    return jsonify(shared_logs)

def delayed_logs():
    steps = [
        "✅ Pipeline triggered.",
        "🔄 Extracting data from source...",
        "📦 Converting JSON to CSV...",
        "📁 Storing CSV in MySQL...",
        "📊 Updating Power BI dashboard...",
        "✅ Done!"
    ]

    for step in steps:
        time.sleep(2)  # Delay 2 seconds
        log_to_frontend(step)

if __name__ == '__main__':
    socketio.run(app, debug=True)
