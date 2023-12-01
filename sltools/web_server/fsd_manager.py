import json
import threading
from abc import ABC, abstractmethod

from flask import render_template, jsonify, request

from sltools.baseline.config import DefaultArgs, file_changes_msg_queue
from sltools.log_config_loader import log
from sltools.root_commands.SortFilesWithDuplicates import SortFilesWithDuplicates
from sltools.utils.lang_utils import trn
from sltools.utils.misc import set_default
from sltools.utils.watch_files_for_change import thread_watch_directories


class ICommandManager(ABC):
    @abstractmethod
    def register_routes(self, app):
        """Register command-specific routes to the Flask app."""
        pass

    @abstractmethod
    def get_startup_route(self):
        pass


class FindStringDuplicatesManager(ICommandManager):
    def get_startup_route(self):
        return "/"

    def __init__(self, args, callback):
        self.args = args
        self.get_report_callback = callback
        self.last_report = None
        self.last_report_hash = None

        # Start watching directories and worker thread
        thread_watch_directories(args.paths)
        threading.Thread(target=self.worker).start()

    def register_routes(self, app):
        @app.route('/')
        def index():
            html_ = 'index.html'
            log.debug(trn("Try to open %s") % html_)
            return render_template(html_)

        @app.route('/report-hash', methods=['GET'])
        def get_report_hash():
            return json.dumps(self.last_report_hash), 200

        @app.route('/report', methods=['GET'])
        def get_report():
            json_dumps = json.dumps(self.last_report, default=set_default)
            return json_dumps, 200

        @app.route('/sort-duplicates-only', methods=['POST'])
        def sort_duplicates_in_files():
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

    def worker(self):
        # Initial analysis
        _, report = self.get_report_callback(self.args)
        self.last_report = report
        self.last_report_hash = self.calc_report_hash(report)

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

            if report != self.last_report:
                log.info(trn("Files changed"))
                self.last_report = report
                self.last_report_hash = self.calc_report_hash(report)
            else:
                log.info(trn("Files are the same"))

    @staticmethod
    def calc_report_hash(report):
        return hash(json.dumps(report, default=set_default))
