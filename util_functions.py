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

def append_csv_row(data_dir, filename, delimiter, row_list):
    with open(data_dir / filename, "a") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(row_list)

def binary2list(binarystr, delimiter, prefix):
    binarystr = binarystr.decode('utf-8') 
    binarystr = binarystr.replace(prefix, '')
    # binarystr = binarystr.replace('\n','').replace('\r','') # strip non-printing chars
    binarystr_list = binarystr.split(delimiter) 
    return binarystr_list  

def parsivel_str_2_csv(binarystr, delimiter, prefix):
        # in progress
    parsivel_str_list = binary2list(binarystr=item, delimiter=';', prefix=svfs_prefix)
    if parsivel_str_list[-1] == '\n':
        parsivel_str_list = parsivel_str_list[:-1]  
    filename = csvs_suffixes['SVFS']

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
