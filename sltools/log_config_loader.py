import logging.config
import os
import sys

import colorlog
import rich

from sltools.utils.colorize import cf

# Define a custom logging level
ALWAYS_LEVEL = 55
ALWAYS_NAME = ''
logging.addLevelName(ALWAYS_LEVEL, ALWAYS_NAME)


# Define custom logger class for autocompletion
def color_log(level, msg):
    if level == logging.CRITICAL:
        return cf(msg, "bright_red")
    elif level == logging.ERROR:
        return cf(msg, "red")
    elif level == logging.WARNING:
        return cf(msg, "yellow")
    elif level == logging.DEBUG:
        return cf(msg, "grey69")
    else:
        return msg


# Init Flask logger
flask_logger = logging.getLogger('werkzeug')
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
flask_logger.addHandler(ch)
flask_logger.setLevel(logging.INFO)


class ExtendedLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        self.console = rich.get_console()

    def _log(self, level, msg, args,
             exc_info=None, extra=None,
             stack_info=False, stacklevel=1):
        # For console logging, use Rich
        # Except Flask
        if level >= self.level and not self.name.startswith('werkzeug'):
            msg = str(msg)  # Ensure msg is a string
            if args:
                msg = msg % args  # Only apply formatting if args is non-empty

            res = color_log(level, f"{logging.getLevelName(level)} {msg}")
            self.console.print(res)

        # For file logging, use the standard logging mechanism
        try:
            super()._log(level, msg, args, exc_info=exc_info,
                         extra=extra, stack_info=stack_info,
                         stacklevel=stacklevel)
        except Exception as e:
            print("Can't log error due to fucking rich formatter. Fixme.")

    def always(self, message="", *args, **kws):
        self._log(ALWAYS_LEVEL, message, args, **kws)


logging.setLoggerClass(ExtendedLogger)


# class CustomFormatter(logging.Formatter):
#     def format(self, record):
#         if record.levelno == ALWAYS_LEVEL:
#             # Use a different format for ALWAYS level messages
#             self._fmt = '%(asctime)s - ALWAYS - %(message)s'
#         else:
#             # Use the default format for all other log levels
#             self._fmt = '%(asctime)s - %(levelname)s - %(message)s'
#         return super().format(record)


def configure_logging():
    colors = colorlog.default_log_colors
    colors['INFO'] = "reset"

    loggers = {
        '': {
            'level': 'INFO',
            'handlers': ['consoleHandler'],
        },
        'main': {
            'level': 'INFO',
            'handlers': ['fileHandler'],
            'propagate': False,
        },
    }

    handlers = {
        'consoleHandler': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'colorConsoleFormatter',
            'stream': sys.stdout,
        },
        'fileHandler': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'formatter': 'fileFormatter',
            'filename': 'app.log',
            'mode': 'a',
        },
    }

    formatters = {
        'fileFormatter': {
            'format': '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'colorConsoleFormatter': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(levelname)s - %(message)s %(reset)s',
        },
    }

    logging.config.dictConfig({
        'version': 1,
        'loggers': loggers,
        'handlers': handlers,
        'formatters': formatters,
    })


# def configure_logging():
#     curr_dir = os.path.dirname(__file__)
#     colors = colorlog.default_log_colors
#     colors['INFO'] = "reset"
#     # colors[ALWAYS_NAME] = "green"
#     print(file_path)
#     logging.config.fileConfig(fname=file_path, disable_existing_loggers=False, defaults={'log_color': colors}, )


def update_log_level(_log):
    plog_level = os.environ.get("PLOG_LEVEL")
    if plog_level is None:
        return _log

    level_lower = plog_level.lower()
    if level_lower == "error":
        new_log_level = logging.ERROR
    elif level_lower == "warning":
        new_log_level = logging.WARNING
    elif level_lower == "info":
        new_log_level = logging.INFO
    elif level_lower == "debug":
        new_log_level = logging.DEBUG
    else:
        _log.warning(f"Unknown loglevel: {plog_level}")
        return _log

    _log.always(f"New log level: {plog_level}")
    _log.setLevel(new_log_level)
    return _log


def _get_main_logger() -> ExtendedLogger:
    configure_logging()
    _logger = logging.getLogger('main')
    return update_log_level(_logger)


log = _get_main_logger()
