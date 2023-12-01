import logging
import os.path
import signal
import subprocess
import time
import webbrowser
from threading import Timer

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

from sltools.log_config_loader import log
from sltools.utils.lang_utils import trn
from sltools.web_server.fsd_manager import ICommandManager


class WebUiServer:
    def __init__(self, cmd_manager: ICommandManager):
        self.app = Flask(__name__)
        self.manager = cmd_manager

        # Setup the Flask logger
        self.__setup_logger()

        # Register routes
        self.register_common_routes()
        cmd_manager.register_routes(self.app)

        # Setup CORS
        CORS(self.app, resources={r"/*": {"origins": "*"}})

    @staticmethod
    def __setup_logger():
        flask_logger = logging.getLogger('werkzeug')
        flask_logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        flask_logger.addHandler(ch)

    def register_common_routes(self):
        # Common API
        @self.app.route('/health', methods=['GET'])
        def health():
            return "Ok", 200

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

    # Common methods
    def run(self):
        Timer(0, self.check_endpoint_and_open_browser).start()
        self.app.run(port=5555)

    def check_endpoint_and_open_browser(self):
        health_url = "http://127.0.0.1:5555/health"
        target_url = "http://127.0.0.1:5555" + self.manager.get_startup_route()
        while True:
            try:
                response = requests.get(health_url)
                if response.status_code == 200:
                    time.sleep(0.2)
                    webbrowser.open_new(target_url)
                    break  # Exit the loop once the page is opened
            except requests.exceptions.RequestException as e:
                pass  # Handle exceptions if needed
            time.sleep(1)  # Wait for a short time before checking again

    @staticmethod
    def kill_server():
        log.info(trn("Shutting down server!!!"))
        os.kill(os.getpid(), signal.SIGINT)
