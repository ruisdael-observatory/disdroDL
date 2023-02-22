import yaml
import os
import csv
import sys
import re
import serial
from typing import Dict
from time import sleep
if __name__ == '__main__': 
    from log import log 
else:
    from modules.log import log 

def yaml2dict(path: str) -> Dict:
    with open(path, 'r') as yaml_f:
        yaml_content = yaml_f.read()
        yaml_dict = yaml.safe_load(yaml_content)
    return yaml_dict

def create_dir(path: str):
    if not os.path.exists(path):
        path.mkdir(parents=True)
        # os.mkdir(path)
        created_dir = True
    else:
        created_dir = False
    return created_dir

def create_new_csv(csv_path, headers, delimiter=";"):
    if not os.path.exists(csv_path):
        with open(csv_path, "w") as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerow(headers)
        created_csv = True
    else:
        created_csv = False

def csv_headers(sfvs_telegram_resquest, config_dict):
    '''for Single Value Fields 
    config.yml telegram_fields name and unit are used to created the CSV headers
    '''
    headers_numbers = ((sfvs_telegram_resquest.replace('%','')).split(';'))[:-1]
    headers_names = []
    for key in headers_numbers:
        header = f"{config_dict['telegram_fields'][key]['name']}"
        if 'unit' in config_dict['telegram_fields'][key].keys():
            header = f"{header} ({config_dict['telegram_fields'][key]['unit']})"
        headers_names.append(header)
    headers = ['timestamp'] + headers_names
    return headers  

def capture_telegram_prfx_vars(telegram_line):
    ''' input: line received from telegram
        output: line prefix, values
        Through regex the prefix and values are captures from telegram str
Note:  F61 will be an exception since its values are multiline
    '''
    prefix_match = re.match(r'(^.{3,4}):(.*?)$', telegram_line.decode('utf-8')) 
    if prefix_match:
        prefix = prefix_match.group(1)
        values = prefix_match.group(2)
        return prefix, values
    else:
        return None, None 

def append_csv_row(data_dir, filename, delimiter, data_list):
    # import pdb; pdb.set_trace()
    with open(data_dir / filename, "a") as f:
        writer = csv.writer(f, delimiter=delimiter)
        if type(data_list[0]) == list:
            for data_item in data_list:
                writer.writerow(data_item)
                # writer.writerow(delimiter.join(data_list))                
        elif type(data_list[0]) == str:
            writer.writerow(data_list)

def string2row(timestamp, valuestr, delimiter, prefix):
    '''
    Converts a telegram string to a list of values, separated by the delimiter 
    and added timestamp to first item.
    The output is ready to be written to CSV 
    '''
    values_list = (valuestr.replace(f'{prefix}:', '')).split(delimiter)        
    # import pdb; pdb.set_trace()
    values_list = [timestamp] + values_list
    if values_list[-1] == '' or values_list[-1] == '\n':
        values_list = values_list[:-1]  
    return values_list

def join_f61_items(telegram_list):
    '''
    def uses the telegram_list index, of where F61 is positioned
    to mark th start of F61 items in telegram_list.
    Those items (with exception iog last, empty item) are return in the list of string f61_items

    Each one of the f61_items will be a row, with 2 columns (3 if we include timestamp).
    '''
    for index, item in enumerate(telegram_list):
        if 'F61:' in item.decode('utf-8'):
            f61_items = telegram_list[index:-1]  
            f61_items = [item.decode('utf-8').replace('\r\n', '').replace('F61:','') for item in f61_items]
            f61_items = f61_items
    return f61_items

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
    log_file = log_dir / 'log.json'
    logger = log(log_path=log_file, 
                log_name=f"{script_name}: {parsivel_name}")  
    logger.info(msg=f"Starting {script_name} for {parsivel_name}")
    return logger

def parsivel_start_sequence(serialconnection, config_dict, logger):
    logger.info(msg="Starting parsivel start sequence commands")
    serialconnection.reset_input_buffer()  # Flushes input buffer
    parsivel_set_station_name = ('CS/K/' + config_dict['station_name'] + '\r').encode('utf-8')  # Sets the name of the Parsivel, maximum 10 characters
    serialconnection.write(parsivel_set_station_name)
    sleep(1)
    parsivel_set_ID = ('CS/J/' + config_dict['Parsivel_ID'] + '\r').encode('utf-8')  # Sets the ID of the Parsivel, maximum 4 numerical characters
    serialconnection.write(parsivel_set_ID)
    sleep(2)
    parsivel_restart = 'CS/Z/1\r'.encode('utf-8')
    serialconnection.write(parsivel_restart)  # resets rain amount
    sleep(10)
    parsivel_user_telegram = 'CS/M/M/1\r'.encode('utf-8')  # The Parsivel broadcasts the user defined telegram. # DONE = MIGRATED TO SCRIPTS
    serialconnection.write(parsivel_user_telegram) 

def parsivel_reset(serialconnection, logger):
    logger.info(msg="Reseting Parsivel")
    parsivel_restart = 'CS/Z/1\r'.encode('utf-8')
    serialconnection.write(parsivel_restart)