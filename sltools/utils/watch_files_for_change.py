import os
import threading
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from sltools.commands.common import get_xml_files_and_log
from sltools.config import file_changes_msg_queue


class MyHandler(FileSystemEventHandler):
    def __init__(self, q):
        super().__init__()
        self.q = q

    def on_modified(self, event):
        if event.src_path.endswith('.xml'):
            self.q.put({'file_path': event.src_path, 'action': 'modified'})

    def on_created(self, event):
        if event.src_path.endswith('.xml'):
            self.q.put({'file_path': event.src_path, 'action': 'created'})

    def on_deleted(self, event):
        if event.src_path.endswith('.xml'):
            self.q.put({'file_path': event.src_path, 'action': 'deleted'})


def watch_directories(paths, q):
    all_files = get_xml_files_and_log(paths, "Monitoring")
    unique_directories = {os.path.dirname(file) for file in all_files}
    event_handler = MyHandler(q)
    observer = Observer()
    for dir_name in unique_directories:
        observer.schedule(event_handler, path=dir_name, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(9999)
            pass  # Keep the script running.
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def thread_watch_directories(paths):
    watch_thread = threading.Thread(target=watch_directories, args=(paths, file_changes_msg_queue))
    watch_thread.start()
