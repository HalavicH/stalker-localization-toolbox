import logging.config
import os
import sys

import colorlog
import pkg_resources

# Define a custom logging level
ALWAYS_LEVEL = 55
ALWAYS_NAME = '\u27A4'
logging.addLevelName(ALWAYS_LEVEL, ALWAYS_NAME)

file_path = pkg_resources.resource_filename('src', 'resources/logger-config.ini')


# file_path = os.path.abspath(os.path.join(curr_dir, 'resources/logger_config.ini'))


# Define custom logger class for autocompletion
class ExtendedLogger(logging.Logger):
    def always(self, message="", *args, **kws):
        pass


def always(self, message="", *args, **kws):
    self.log(ALWAYS_LEVEL, message, *args, **kws)


logging.Logger.always = always


class CustomFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == ALWAYS_LEVEL:
            # Use a different format for ALWAYS level messages
            self._fmt = '%(asctime)s - ALWAYS - %(message)s'
        else:
            # Use the default format for all other log levels
            self._fmt = '%(asctime)s - %(levelname)s - %(message)s'
        return super().format(record)


def configure_logging():
    colors = colorlog.default_log_colors
    colors['INFO'] = "reset"

    loggers = {
        '': {
            'level': 'WARNING',
            'handlers': ['consoleHandler'],
        },
        'main': {
            'level': 'WARNING',
            'handlers': ['consoleHandler', 'fileHandler'],
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
