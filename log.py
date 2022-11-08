import logging
import os
import json
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from  util_functions import yaml2dict



def log(log_path, log_name):
    logger = logging.getLogger(log_name)
    logging.Formatter.converter = time.gmtime  # set log time to utc/gmt
    log_format = logging.Formatter(
        json.dumps({'date': '%(asctime)s',
                    'name': '%(name)s',
                    'level': '%(levelname)s',
                    'msg': '%(message)s',
                    })
    )
    log_handler = RotatingFileHandler(filename=log_path,
                                      maxBytes=512000,
                                      backupCount=2)  # 512Kb log file
    log_handler.setFormatter(log_format)
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)
    return logger


if __name__ == '__main__':
    config_dict = yaml2dict(path = wd / 'config.yml')
    wd = Path(__file__).parent 
    log_dir = wd / config_dict['log_dir']
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    log_file = log_dir / 'log.json'

    logger = log(log_path=log_file, 
                log_name=f"{config_dict['script_name']}: {config_dict['Parsivel_name']}")  
    logger.info(msg='hello info')
    logger.debug(msg='I am debugging')
    logger.error(msg='I am an an error')
