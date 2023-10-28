import json
import logging
import os.path
import subprocess
import threading
import time
import webbrowser
from threading import Timer

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from src.log_config_loader import log
from src.utils.misc import set_default, remove_invalid_paths

app = Flask(__name__)

FILES_KEY = "files"
ARGS_KEY = "args"
CALLBACK_KEY = "callback"
LAST_DATA_KEY = "last_data"
NEW_REPORT_AVAILABLE = "new_report_available"
CTX = {
    FILES_KEY: None,
    ARGS_KEY: None,
    CALLBACK_KEY: None,
    LAST_DATA_KEY: None,
    NEW_REPORT_AVAILABLE: True
}

current_working_directory = os.getcwd()

flask_logger = logging.getLogger('werkzeug')
flask_logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
flask_logger.addHandler(ch)


@app.route('/')
def index():
    html_ = 'index.html'
    print("Try to open", html_)

    return render_template(html_)


@app.route('/new-report-available', methods=['GET'])
def new_report_available():
    return json.dumps(CTX[NEW_REPORT_AVAILABLE]), 200


@app.route('/report', methods=['GET'])
def get_report():
    json_dumps = json.dumps(CTX[LAST_DATA_KEY], default=set_default)
    CTX[NEW_REPORT_AVAILABLE] = False
    return json_dumps, 200


@app.route('/diff', methods=['POST'])
def diff_files():
    file1 = request.json.get('file1')
    file2 = request.json.get('file2')

    if not file1 or not file2:
        return jsonify({"error": "Both file paths are required!"}), 400

    file1 = os.path.join(current_working_directory, file1)
    file2 = os.path.join(current_working_directory, file2)
    log.info(f"Running diff on: '{file1}', '{file2}'")

    try:
        # Call the shell command
        subprocess.call(["code", "--diff", file1, file2])
        return jsonify({"message": "Command executed successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def worker():
    while True:
        log.info("Watching for changes in files")
        CTX[FILES_KEY] = remove_invalid_paths(CTX[FILES_KEY])
        try:
            _, report = CTX[CALLBACK_KEY](CTX[ARGS_KEY], CTX[FILES_KEY], True)
        except FileNotFoundError:
            # file was removed in the middle of process. Will just retry
            continue

        if report != CTX[LAST_DATA_KEY]:
            log.info("Files changed")
            CTX[NEW_REPORT_AVAILABLE] = True
            CTX[LAST_DATA_KEY] = report
        else:
            log.info("Files are the same")
        time.sleep(5)


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')


def run_flask_server(args, files, get_report_callback):
    CTX[CALLBACK_KEY] = get_report_callback
    CTX[FILES_KEY] = files

    _, CTX[LAST_DATA_KEY] = get_report_callback(args, files, True)

    t = threading.Thread(target=worker)
    t.start()

    Timer(1, open_browser).start()
    cors = CORS(app, resources={r"/*": {"origins": "*"}})
    app.run()
