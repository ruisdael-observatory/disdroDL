"""
Imports
"""
import os
from time import sleep
from pathlib import Path
from typing import Dict, Union
import yaml
from modules.now_time import NowTime  # pylint: disable=import-error

if __name__ == '__main__':
    from log import log  # pylint: disable=import-error
else:
    from modules.log import log  # pylint: disable=import-error, ungrouped-imports


def yaml2dict(path: Path) -> Dict:
    """
    This function reads a yaml file and returns a dictionary with all the field and values.
    :param path: the path to the yaml file
    :return: dictionary with all the field and values
    """
    with open(path, 'r') as yaml_f:  # pylint: disable=unspecified-encoding
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
    else:
        raise Exception("unsupported sensor type")


def create_dir(path: Path):
    """
    This function creates a directory if it does not exist.
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


def unpack_telegram_from_db(telegram_str: str) -> Dict[str, Union[str, list]]:
    """
    unpacks telegram string from sqlite DB row into a dictionary

    * key precedes value NN:val
    * key:value pair, seperated by '; '
    * list: converted to str with ',' separator between values
    * empty lists, empty strings: converted to 'None'
    Example Input: '19:None; 20:10; 21:25.05.2023;
    51:000140; 90:-9.999,-9.999,-9.999,-9.999,-9.999 ...'
    Example Output:  {'60': '00000062', '90': '-9.999,-9.999,01.619,...'}
    """
    telegram_dict = {}
    telegram_list = telegram_str.split('; ')
    for telegram_item in telegram_list:
        key, val = telegram_item.split(':')
        if val == 'None':
            val = None
        telegram_dict[key] = val
    return telegram_dict
