import logging.config
import os


def configure_logging():
    curr_dir = os.path.dirname(__file__)

    ini = os.path.abspath(os.path.join(curr_dir, '../resources/logger_config.ini'))
    # print("Starting with logger config at " + ini)
    logging.config.fileConfig(fname=(ini), disable_existing_loggers=False)


def get_main_logger() -> logging.Logger:
    configure_logging()
    return logging.getLogger('main')
