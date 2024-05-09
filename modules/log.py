"""
This module is used to create a logger object that logs to a file.
"""
import logging
import json
import time
from logging.handlers import TimedRotatingFileHandler


def log(log_path, log_name):
    """
    This function creates a logger object that logs to a file.
    :param log_path: the path to the log file
    :param log_name: the name of the logger
    :return: logger object
    """
    logger = logging.getLogger(log_name)
    logging.Formatter.converter = time.gmtime  # set log time to utc/gmt
    log_format = logging.Formatter(
        json.dumps({'date': '%(asctime)s',
                    'name': '%(name)s',
                    'level': '%(levelname)s',
                    'msg': '%(message)s',
                    })
    )
    log_handler = TimedRotatingFileHandler(
        filename=log_path,
        when='midnight',
        backupCount=7,
        utc=True)
    log_handler.suffix = "%Y%m%d"
    log_handler.setFormatter(log_format)
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)
    return logger
