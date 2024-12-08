import logging

from pythonjsonlogger.jsonlogger import JsonFormatter


def configure_logs():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logHandler = logging.StreamHandler()
    formatter = JsonFormatter()
    logHandler.setFormatter(formatter)
    logHandler.setLevel(logging.DEBUG)
    logger.handlers = [logHandler]
