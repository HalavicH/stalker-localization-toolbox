import logging.config


def configure_logging():
    logging.config.fileConfig(fname='../resources/logging_config.ini', disable_existing_loggers=False)


def get_main_logger() -> logging.Logger:
    configure_logging()
    return logging.getLogger('main')
