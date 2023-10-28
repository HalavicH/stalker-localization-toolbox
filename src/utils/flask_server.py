import json
import os.path
import subprocess
import webbrowser
from threading import Timer

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from src.log_config_loader import log
from src.utils.misc import set_default

app = Flask(__name__)

report_data = None
current_working_directory = os.getcwd()


@app.route('/')
def index():
    html_ = 'index.html'
    print("Try to open", html_)
    data_json = json.dumps(report_data, default=set_default, ensure_ascii=False, indent=4)

    return render_template(html_, data_json=data_json)


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


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')


def run_flask_server(report):
    global report_data
    report_data = report
    Timer(1, open_browser).start()
    cors = CORS(app, resources={r"/*": {"origins": "*"}})
    app.run()

