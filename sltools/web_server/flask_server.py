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

from sltools.baseline.config import file_changes_msg_queue, DefaultArgs
from sltools.log_config_loader import log
from sltools.root_commands.SortFilesWithDuplicates import SortFilesWithDuplicates
from sltools.utils.lang_utils import trn
from sltools.utils.misc import set_default
from sltools.utils.watch_files_for_change import thread_watch_directories

app = Flask(__name__)

ARGS_KEY = "args"
CALLBACK_KEY = "callback"
LAST_REPORT_KEY = "last_report"
LAST_REPORT_HASH_KEY = "last_report_hash"

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


class WebUiServer:
    def __init__(self, args, get_report_callback):
        self.app = Flask(__name__)
        self.args = args
        self.get_report_callback = get_report_callback
        self.CTX = {
            ARGS_KEY: None,
            CALLBACK_KEY: None,
            LAST_REPORT_KEY: None,
            LAST_REPORT_HASH_KEY: None
        }

        # Setup the Flask logger
        self.setup_logger()

        # Register routes
        self.register_routes()

        # Setup CORS
        CORS(self.app, resources={r"/*": {"origins": "*"}})

        # Start watching directories and worker thread
        thread_watch_directories(args.paths)
        threading.Thread(target=self.worker).start()

    def setup_logger(self):
        flask_logger = logging.getLogger('werkzeug')
        flask_logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        flask_logger.addHandler(ch)

    def register_routes(self):
        # Common API
        @self.app.route('/shutdown', methods=['POST'])
        def shutdown():
            Timer(1, self.kill_server).start()
            return jsonify(trn('Dead :D')), 200

        @self.app.route('/diff', methods=['POST'])
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

        # Find string duplicates API
        @self.app.route('/')
        def index():
            html_ = 'index.html'
            log.debug(trn("Try to open %s") % html_)
            return render_template(html_)

        @self.app.route('/report-hash', methods=['GET'])
        def get_report_hash():
            return json.dumps(self.CTX[LAST_REPORT_HASH_KEY]), 200

        @self.app.route('/report', methods=['GET'])
        def get_report():
            json_dumps = json.dumps(self.CTX[LAST_REPORT_KEY], default=set_default)
            return json_dumps, 200

        @self.app.route('/sort-duplicates-only', methods=['POST'])
        def sort__duplicates_in_files():
            file1 = request.json.get('file1')
            file2 = request.json.get('file2')

            args = DefaultArgs()
            args.paths = [file1, file2]
            args.sort_duplicates_only = True

            try:
                SortFilesWithDuplicates().execute(args)
                return jsonify({"message": trn("Command executed successfully!")}), 200
            except Exception as e:
                log.error(trn("Can't sort files: %s") % e)
                return jsonify({"error": str(e)}), 500

    # Common methods
    def run(self):
        Timer(0, self.check_endpoint_and_open_browser).start()
        self.app.run(port=5555)

    @staticmethod
    def check_endpoint_and_open_browser():
        url = "http://127.0.0.1:5555/"
        while True:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    webbrowser.open_new(url)
                    break  # Exit the loop once the page is opened
            except requests.exceptions.RequestException as e:
                pass  # Handle exceptions if needed
            time.sleep(1)  # Wait for a short time before checking again

    @staticmethod
    def kill_server():
        log.info(trn("Shutting down server!!!"))
        os.kill(os.getpid(), signal.SIGINT)

    # Find string duplicates methods
    def worker(self):
        self.CTX[CALLBACK_KEY] = self.get_report_callback
        self.CTX[ARGS_KEY] = self.args
        # Initial analysis
        _, report = self.get_report_callback(self.args, True)
        self.CTX[LAST_REPORT_KEY] = report
        self.CTX[LAST_REPORT_HASH_KEY] = self.calc_report_hash(report)

        while True:
            log.info(trn("Watching for changes in files"))
            event = file_changes_msg_queue.get()
            if event is None:  # Exit condition
                break
            log.info(trn("%s has been %s") % (event['file_path'], event['action']))
            try:
                _, report = self.get_report_callback(self.args, True)
            except FileNotFoundError:
                # file was removed in the middle of process. Will just retry
                continue

            if report != self.CTX[LAST_REPORT_KEY]:
                log.info(trn("Files changed"))
                self.CTX[LAST_REPORT_KEY] = report
                self.CTX[LAST_REPORT_HASH_KEY] = self.calc_report_hash(report)
            else:
                log.info(trn("Files are the same"))

    @staticmethod
    def calc_report_hash(report):
        return hash(json.dumps(report, default=set_default))

