import yaml
import os
import sys
import serial
from time import sleep
from pathlib import Path
from typing import Dict, Union
from modules.now_time import NowTime

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


def thies_start_sequence(serial_connection, thies_id):

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
    logger.info(msg="Reseting Parsivel")
    if factoryreset is True:
        parsivel_reset = 'CS/F/1\r'.encode('utf-8')
        serialconnection.write(parsivel_reset)
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
