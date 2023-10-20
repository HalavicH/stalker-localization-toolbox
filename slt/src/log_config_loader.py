import logging.config
import os

import colorlog


def configure_logging():
    curr_dir = os.path.dirname(__file__)
    file_path = os.path.abspath(os.path.join(curr_dir, '../resources/logger_config.ini'))
    colors = colorlog.default_log_colors
    colors['INFO'] = "reset"
    logging.config.fileConfig(fname=file_path, disable_existing_loggers=False, defaults={'log_color': colors}, )


def get_main_logger() -> logging.Logger:
    configure_logging()
    return logging.getLogger('main')


log = get_main_logger()
