import yaml
import os
import csv
import sys
import serial
from typing import Dict


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



def append_csv_row(data_dir, filename, delimiter, data_list):
    with open(data_dir / filename, "a") as f:
        writer = csv.writer(f, delimiter=delimiter)
        if type(data_list[0]) == list:
            for data_item in data_list:
                writer.writerow(data_list)                
        elif type(data_list[0]) == str:
            writer.writerow(data_list)

def string2row(timestamp, valuestr, delimiter, prefix):
    '''
    Converts a telegram string to a list of values, separated by the delimiter 
    and added timestamp to first item.
    The output is ready to be written to CSV 
    '''
    values_list = (valuestr.replace(f'{prefix}:', '')).split(delimiter)        
    values_list = [timestamp] + values_list
    if values_list[-1] == '\n':
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


# def parsivel_list_2_csv(timestamp, valuestr, delimiter, prefix, data_dir, filename):
#     parsivel_row_value_list = (valuestr.replace(f'{prefix}:', '')).split(delimiter)        
#     parsivel_row_value_list = [timestamp] + parsivel_row_value_list
#     print(prefix, parsivel_row_value_list)
#     if parsivel_row_value_list[-1] == '\n':
#         parsivel_row_value_list = parsivel_row_value_list[:-1]  

#     if prefix == 'F61':
#         if parsivel_row_value_list[1] != '':
#             # prevent writing empty F61 
#             append_csv_row(data_dir=data_dir, filename=filename, delimiter=delimiter, data_list=parsivel_row_value_list)
#     else:
#         append_csv_row(data_dir=data_dir, filename=filename, delimiter=delimiter, data_list=parsivel_row_value_list)


def init_serial(port: str, baud: int, logger):
    try:
        parsivel = serial.Serial(port, baud, timeout=1)  # Defines the serial port
        logger.info(msg=f'Connected to parsivel, via: {parsivel}')
    except Exception as e:
        logger.error(msg=e)
        # print(e)
        sys.exit()
    parsivel.reset_input_buffer()              
    return parsivel
