import json
import logging
import os.path
import subprocess
import threading
import time
import webbrowser
from threading import Timer

import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from src.commands.common import get_xml_files_and_log
from src.log_config_loader import log
from src.utils.misc import set_default, remove_invalid_paths
from src.utils.watch_files_for_change import watch_directories, thread_watch_directories
from src.config import file_changes_msg_queue

app = Flask(__name__)

ARGS_KEY = "args"
CALLBACK_KEY = "callback"
LAST_REPORT_KEY = "last_report"
LAST_REPORT_HASH_KEY = "last_report_hash"
CTX = {
    ARGS_KEY: None,
    CALLBACK_KEY: None,
    LAST_REPORT_KEY: None,
    LAST_REPORT_HASH_KEY: None
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


@app.route('/report-hash', methods=['GET'])
def get_report_hash():
    return json.dumps(CTX[LAST_REPORT_HASH_KEY]), 200


@app.route('/report', methods=['GET'])
def get_report():
    json_dumps = json.dumps(CTX[LAST_REPORT_KEY], default=set_default)
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


def calc_report_hash(report):
    return hash(json.dumps(report, default=set_default))


def worker():
    # Initial analysis
    _, report = CTX[CALLBACK_KEY](CTX[ARGS_KEY], True)
    CTX[LAST_REPORT_KEY] = report
    CTX[LAST_REPORT_HASH_KEY] = calc_report_hash(report)

    while True:
        log.info("Watching for changes in files")
        event = file_changes_msg_queue.get()
        if event is None:  # Exit condition
            break
        log.info(f"{event['file_path']} has been {event['action']}")
        try:
            _, report = CTX[CALLBACK_KEY](CTX[ARGS_KEY], True)
        except FileNotFoundError:
            # file was removed in the middle of process. Will just retry
            continue

        if report != CTX[LAST_REPORT_KEY]:
            log.info("Files changed")
            CTX[LAST_REPORT_KEY] = report
            CTX[LAST_REPORT_HASH_KEY] = calc_report_hash(report)
        else:
            log.info("Files are the same")


def check_endpoint_and_open_browser():
    url = "http://127.0.0.1:5000/"
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                webbrowser.open_new(url)
                break  # Exit the loop once the page is opened
        except requests.exceptions.RequestException as e:
            # Handle exceptions (like connection errors) if needed
            pass
        time.sleep(1)  # Wait for a short time before checking again


def run_flask_server(args, get_report_callback):
    CTX[ARGS_KEY] = args
    CTX[CALLBACK_KEY] = get_report_callback

    thread_watch_directories(args.paths)
    threading.Thread(target=worker).start()

    Timer(0, check_endpoint_and_open_browser).start()
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.run()
