import os.path
import webbrowser
from threading import Timer

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    html_ = os.path.dirname(__file__) + '/../../d3-standalone/index.html'
    print("Try to open", html_)
    return render_template(html_)


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')


def run_flask_server():
    Timer(1, open_browser).start()
    app.run()
