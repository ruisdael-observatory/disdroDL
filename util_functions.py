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

def create_new_csv(csv_path, headers):
    if not os.path.exists(csv_path):
        with open(csv_path, "w") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(headers)
        created_csv = True
    else:
        created_csv = False

def binary2list(binarystr, spliter, prefix):
    binarystr = binarystr.decode('utf-8') 
    print('binarystr:' binarystr[0:10])
    binarystr = binarystr.replace(prefix, '')
    print('binarystr w/out prefix:' binarystr[0:10])

    # binarystr = binarystr.replace('\n','').replace('\r','') # strip non-printing chars
    binarystr_list = binarystr.split(spliter) 
    return binarystr_list  

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