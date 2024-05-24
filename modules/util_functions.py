"""
This module contains a variety of functions with different utilities.

Functions:
- yaml2dict: This function reads a yaml file and returns a dictionary with all the field and values.
- get_general_config: This function returns a general config file based on the provided sensor type.
- create_dir: This function creates a directory if it does not already exist.
- resetSerialBuffers: This function resets the input and output buffers of the serial connection.
- interruptHandler: This function interrupts the execution of the serial connection.
- create_logger: This function creates a logger object that logs to a file.
"""

import os
from time import sleep
from pathlib import Path
from typing import Dict
import yaml


if __name__ == '__main__':
    from log import log # pylint: disable=import-error
else:
    from modules.log import log # pylint: disable=import-error, ungrouped-imports


def yaml2dict(path: Path) -> Dict:
    """
    This function reads a yaml file and returns a dictionary with all the field and values.
    :param path: the path to the yaml file
    :return: dictionary with all the field and values
    """
    with open(path, 'r') as yaml_f: # pylint: disable=unspecified-encoding
        yaml_content = yaml_f.read()
        yaml_dict = yaml.safe_load(yaml_content)
    return yaml_dict

def get_general_config(path: Path, sensor_type: str) -> Dict:
    """
    This function returns a general config file based on the provided sensor type.
    :param path: the path to the directory
    :param sensor_type: a string indicating the sensor type
    :return: dict of the respective general config file
    """
    if sensor_type == 'OTT Hydromet Parsivel2':
        return yaml2dict(path=path / 'configs_netcdf' / 'config_general_parsivel.yml')
    if sensor_type == 'Thies Clima':
        return yaml2dict(path=path / 'configs_netcdf' / 'config_general_thies.yml')

    raise Exception("unsupported sensor type")

def create_dir(path: Path):
    """
    This function creates a directory if it does not already exist.
    :param path: the path to the directory
    :return: True if the directory was created, False if it already existed
    """
    if not os.path.exists(path):
        Path.mkdir(path, parents=True)
        created_dir = True
    else:
        created_dir = False
    return created_dir


def resetSerialBuffers(serial_connection):
    """
    This function resets the input and output buffers of the serial connection.
    :param serial_connection: the serial connection object that needs to be reset
    """
    serial_connection.reset_input_buffer()
    sleep(1)
    serial_connection.reset_output_buffer()


def interruptHandler(serial_connection, logger):
    """
    This function interrupts the execution of the serial connection.
    :param serial_connection: the serial connection object to interrupt
    :param logger: the logger object
    """
    msg = 'Interrupting execution'
    print(msg)
    logger.info(msg=msg)
    resetSerialBuffers(serial_connection=serial_connection)
    serial_connection.close()


def create_logger(log_dir, script_name, sensor_name):
    """
    This function creates a logger object that logs to a file.
    :param log_dir: directory of the log file
    :param script_name: name of the script
    :param sensor_name: name of the disdrometer
    :return: the logger object
    """
    create_dir(log_dir)
    log_file = log_dir / f'log_{script_name}.json'
    logger = log(log_path=log_file,
                 log_name=f"{script_name}: {sensor_name}")
    logger.info(msg=f"Starting {script_name} for {sensor_name}")
    return logger
