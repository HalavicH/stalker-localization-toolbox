import logging.config
import os

import colorlog

# Define a custom logging level
ALWAYS_LEVEL = 55
ALWAYS_NAME = '\u27A4'
logging.addLevelName(ALWAYS_LEVEL, ALWAYS_NAME)


def always(self, message, *args, **kws):
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
    curr_dir = os.path.dirname(__file__)
    file_path = os.path.abspath(os.path.join(curr_dir, '../resources/logger_config.ini'))
    colors = colorlog.default_log_colors
    colors['INFO'] = "reset"
    # colors[ALWAYS_NAME] = "green"
    logging.config.fileConfig(fname=file_path, disable_existing_loggers=False, defaults={'log_color': colors}, )


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

    _log.info(f"New log level: {plog_level}")
    _log.setLevel(new_log_level)
    return _log


def _get_main_logger() -> logging.Logger:
    configure_logging()
    _logger = logging.getLogger('main')
    return update_log_level(_logger)


log = _get_main_logger()
