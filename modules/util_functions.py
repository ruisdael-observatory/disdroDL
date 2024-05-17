"""
Imports
"""
import os
import sys
from time import sleep
from pathlib import Path
from typing import Dict, Union
import serial
import yaml
from modules.now_time import NowTime # pylint: disable=import-error


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


def init_serial(port: str, baud: int, logger):
    """
    This function initiates a serial connection to the disdrometer.
    :param port: the port to connect to
    :param baud: the baud rate
    :param logger: the logger object
    :return: the serial connection object
    """
    try:
        parsivel = serial.Serial(port, baud, timeout=1)  # Defines the serial port
        logger.info(msg=f'Connected to parsivel, via: {parsivel}')
    except Exception as e:  # pylint: disable= W0703
        logger.error(msg=e)
        # print(e)
        sys.exit()
    return parsivel


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


def create_logger(log_dir, script_name, parsivel_name):
    """
    This function creates a logger object that logs to a file.
    :param log_dir: directory of the log file
    :param script_name: name of the script
    :param parsivel_name: name of the disdrometer
    :return: the logger object
    """
    create_dir(log_dir)
    log_file = log_dir / f'log_{script_name}.json'
    logger = log(log_path=log_file,
                 log_name=f"{script_name}: {parsivel_name}")
    logger.info(msg=f"Starting {script_name} for {parsivel_name}")
    return logger


def parsivel_start_sequence(serialconnection, config_dict, logger):
    """
    This function sends the start sequence commands to the parsivel disdrometer.
    :param serialconnection: the serial connection object
    :param config_dict: dict with the configuration settings
    :param logger: the logger object
    """
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


def thies_start_sequence(serial_connection, thies_id):
    '''
    This function sends the start sequence commands to the Thies disdrometer.
    It sets the sensor in config mode, place sensor in manual mode,
    changes the time to the current time and sets the sensor back to normal mode.
    :param serial_connection: Connection of the thies
    :param thies_id: id of the thies
    '''

    serial_connection.reset_input_buffer()
    serial_connection.reset_output_buffer()

    serial_connection.write(('\r' + thies_id + 'KY00001\r').encode('utf-8')) # place in config mode
    sleep(1)

    serial_connection.write(('\r' + thies_id + 'TM00000\r').encode('utf-8')) # turn of automatic mode
    sleep(1)

    serial_connection.write(('\r' + thies_id + 'ZH000' + NowTime().time_list[0] + '\r').encode('utf-8')) # set hour
    sleep(1)

    serial_connection.write(('\r' + thies_id + 'ZM000' + NowTime().time_list[1] + '\r').encode('utf-8')) # set minutes
    sleep(1)

    serial_connection.write(('\r' + thies_id + 'ZS000' + NowTime().time_list[2] + '\r').encode('utf-8')) # set seconds
    sleep(1)

    serial_connection.write(('\r' + thies_id + 'KY00000\r').encode('utf-8')) # place out of config mode
    sleep(1)

    serial_connection.reset_input_buffer()
    serial_connection.reset_output_buffer()


def parsivel_reset(serialconnection, logger, factoryreset):
    """
    This function resets the parsivel disdrometer.
    :param serialconnection: the serial connection object
    :param logger: the logger object
    :param factoryreset: if the factory reset should be performed
    """
    logger.info(msg="Reseting Parsivel")
    if factoryreset is True:
        parsivel_reset_code = 'CS/F/1\r'.encode('utf-8')
        serialconnection.write(parsivel_reset_code)
    else:
        parsivel_restart = 'CS/Z/1\r'.encode('utf-8')  # restart
        serialconnection.write(parsivel_restart)
    sleep(5)


def unpack_telegram_from_db(telegram_str: str) -> Dict[str, Union[str, list]]:
    '''
    unpacks telegram string from sqlite DB row into a dictionary

    * key precedes value NN:val
    * key:value pair, seperated by '; '
    * list: converted to str with ',' separator between values
    * empty lists, empty strings: converted to 'None'
    Example Input: '19:None; 20:10; 21:25.05.2023;
    51:000140; 90:-9.999,-9.999,-9.999,-9.999,-9.999 ...'
    Example Output:  {'60': '00000062', '90': '-9.999,-9.999,01.619,...'}
    '''
    telegram_dict = {}
    telegram_list = telegram_str.split('; ')
    for telegram_item in telegram_list:
        key, val = telegram_item.split(':')
        if val == 'None':
            val = None
        telegram_dict[key] = val
    return telegram_dict
