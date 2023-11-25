import json
import logging
import os.path
import signal
import subprocess
import threading
import time
import webbrowser
from threading import Timer

import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from sltools.commands.sort_strings_in_files import sort_files_with_duplicates
from sltools.config import file_changes_msg_queue, DefaultArgs
from sltools.log_config_loader import log
from sltools.utils.misc import set_default
from sltools.utils.watch_files_for_change import thread_watch_directories
from sltools.utils.lang_utils import trn

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

# Dictionary to store client heartbeats
client_heartbeats = {}

# Timeout for detecting inactivity (in seconds)
heartbeat_timeout = 10
last_heartbeat_time = time.time()


def kill_server():
    log.info(trn("Shutting down server!!!"))
    os.kill(os.getpid(), signal.SIGINT)


# Route to update the heartbeat
@app.route('/shutdown', methods=['POST'])
def shutdown():
    Timer(1, kill_server).start()

    return jsonify(trn('Dead :D')), 200


@app.route('/')
def index():
    html_ = 'index.html'
    log.debug(trn("Try to open %s") % html_)

    return render_template(html_)


@app.route('/report-hash', methods=['GET'])
def get_report_hash():
    return json.dumps(CTX[LAST_REPORT_HASH_KEY]), 200


@app.route('/report', methods=['GET'])
def get_report():
    json_dumps = json.dumps(CTX[LAST_REPORT_KEY], default=set_default)
    return json_dumps, 200


@app.route('/sort-duplicates-only', methods=['POST'])
def sort__duplicates_in_files():
    file1 = request.json.get('file1')
    file2 = request.json.get('file2')

    args = DefaultArgs()
    args.paths = [file1, file2]
    args.sort_duplicates_only = True

    try:
        sort_files_with_duplicates(args, False)
        return jsonify({"message": trn("Command executed successfully!")}), 200
    except Exception as e:
        log.error(trn("Can't sort files: %s") % e)
        return jsonify({"error": str(e)}), 500


@app.route('/diff', methods=['POST'])
def diff_files():
    file1 = request.json.get('file1')
    file2 = request.json.get('file2')

    if not file1 or not file2:
        return jsonify({"error": trn("Both file paths are required!")}), 400

    file1 = os.path.abspath(file1)
    file2 = os.path.abspath(file2)

    cmd = 'code --diff "%s" "%s"' % (file1, file2)
    log.info(trn("Running diff with: '%s'") % cmd)

    try:
        # Call the shell command using Popen
        subprocess.Popen(cmd, shell=True)
        return jsonify({"message": trn("Command executed successfully!")}), 200
    except Exception as e:
        log.error(trn("Can't diff files: %s") % e)
        return jsonify({"error": str(e)}), 500


def calc_report_hash(report):
    return hash(json.dumps(report, default=set_default))


def worker():
    # Initial analysis
    _, report = CTX[CALLBACK_KEY](CTX[ARGS_KEY], True)
    CTX[LAST_REPORT_KEY] = report
    CTX[LAST_REPORT_HASH_KEY] = calc_report_hash(report)

    while True:
        log.info(trn("Watching for changes in files"))
        event = file_changes_msg_queue.get()
        if event is None:  # Exit condition
            break
        log.info(trn("%s has been %s") % (event['file_path'], event['action']))
        try:
            _, report = CTX[CALLBACK_KEY](CTX[ARGS_KEY], True)
        except FileNotFoundError:
            # file was removed in the middle of process. Will just retry
            continue

        if report != CTX[LAST_REPORT_KEY]:
            log.info(trn("Files changed"))
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
