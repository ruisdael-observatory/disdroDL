import yaml
import os
import sys
import serial
from typing import Dict
from time import sleep
from pathlib import Path

if __name__ == '__main__':
    from log import log
else:
    from modules.log import log


def yaml2dict(path: Path) -> Dict:
    with open(path, 'r') as yaml_f:
        yaml_content = yaml_f.read()
        yaml_dict = yaml.safe_load(yaml_content)
    return yaml_dict


def create_dir(path: Path):
    if not os.path.exists(path):
        Path.mkdir(path, parents=True)
        created_dir = True
    else:
        created_dir = False
    return created_dir


def init_serial(port: str, baud: int, logger):
    try:
        parsivel = serial.Serial(port, baud, timeout=1)  # Defines the serial port
        logger.info(msg=f'Connected to parsivel, via: {parsivel}')
    except Exception as e:
        logger.error(msg=e)
        # print(e)
        sys.exit()
    return parsivel


def resetSerialBuffers(serial_connection):
    serial_connection.reset_input_buffer()
    sleep(1)
    serial_connection.reset_output_buffer()


def interruptHandler(serial_connection, logger):
    msg = 'Interrupting execution'
    print(msg)
    logger.info(msg=msg)
    resetSerialBuffers(serial_connection=serial_connection)
    serial_connection.close()


def create_logger(log_dir, script_name, parsivel_name):
    create_dir(log_dir)
    log_file = log_dir / f'log_{script_name}.json'
    logger = log(log_path=log_file,
                 log_name=f"{script_name}: {parsivel_name}")
    logger.info(msg=f"Starting {script_name} for {parsivel_name}")
    return logger


def parsivel_start_sequence(serialconnection, config_dict, logger):
    logger.info(msg="Starting parsivel start sequence commands")
    serialconnection.reset_input_buffer()  # Flushes input buffer
    # Sets the name of the Parsivel, maximum 10 characters
    parsivel_set_station_code = ('CS/K/' + config_dict['station_code'] + '\r').encode('utf-8')
    serialconnection.write(parsivel_set_station_code)
    sleep(1)
    # Sets the ID of the Parsivel, maximum 4 numerical characters
    parsivel_set_ID = ('CS/J/' + config_dict['global_attrs']['sensor_name'] + '\r').encode('utf-8')
    serialconnection.write(parsivel_set_ID)
    sleep(2)
    parsivel_restart = 'CS/Z/1\r'.encode('utf-8')
    serialconnection.write(parsivel_restart)  # resets rain amount
    sleep(10)
    # The Parsivel broadcasts the user defined telegram.
    parsivel_user_telegram = 'CS/M/M/1\r'.encode('utf-8')
    serialconnection.write(parsivel_user_telegram)


def parsivel_reset(serialconnection, logger, factoryreset):
    logger.info(msg="Reseting Parsivel")
    if factoryreset is True:
        parsivel_reset = 'CS/F/1\r'.encode('utf-8')
        serialconnection.write(parsivel_reset)
    else:
        parsivel_restart = 'CS/Z/1\r'.encode('utf-8')  # restart
        serialconnection.write(parsivel_restart)
    sleep(5)
