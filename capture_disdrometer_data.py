import time
import csv
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict
import serial
from  util_functions import yaml2dict
from parsivel_cmds import *
from log import log 

def init_serial(port: str, baud: int):
    try:
        parsivel = serial.Serial(port, baud, timeout=1)  # Defines the serial port
        logger.info(msg=f'Connected to parsivel, via: {parsivel}')
    except Exception as e:
        logger.error(msg=e)
        print(e)
        sys.exit()
    parsivel.reset_input_buffer()              
    return parsivel

def binary2list(binarystr, spliter):
    binarystr = binarystr.decode('utf-8') 
    binarystr = binarystr.replace('\n','').replace('\r','') # strip non-printing chars
    binarystr_list = binarystr.split(spliter) 
    return binarystr_list  

print('starting script')

wd = Path(__file__).parent 
print(wd)
config_dict = yaml2dict(path = wd / 'config.yml')

# set up log
log_dir = wd / config_dict['log_dir']
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
log_file = log_dir / 'log.json'
logger = log(log_path=log_file, 
            log_name=f"{config_dict['script_name']}: {config_dict['Parsivel_name']}")  
logger.info(msg=f"Starting {config_dict['script_name']} for {config_dict['Parsivel_name']}")

# set up data dir
data_dir = wd / config_dict['data_dir']
if not os.path.exists(data_dir):
    os.mkdir(data_dir)
print(f'{__file__} running\nLogs written to {log_dir}\nData written to {data_dir}')

def create_new_csv(csv_path):
    if not os.path.exists(csv_path):
        logger.info(msg=f"Creating {csv_path}")
        parsivel_set_telegram_list_str = parsivel_set_telegram_list.decode('utf-8')
        parsivel_set_telegram_list_str = parsivel_set_telegram_list_str.replace('CS/M/S/', '').replace('\r','').replace('%', 'Field_')
        headers = ['Timestamp (UTC)']+ parsivel_set_telegram_list_str.split(';')
        with open(csv_path, "w") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(headers)
            
# intiated serial connection
parsivel = init_serial(port=config_dict['port'], baud=config_dict['baud'])

# setup parsivel config commands 
parsivel.write(parsivel_user_telegram) # set up parsivel: to send user defined telegram 
time.sleep(2) 
parsivel.write(parsivel_set_telegram_list)  # set up parsivel: defining list of fields 
time.sleep(2)
parsivel.write(parsivel_current_configuration) # ask parsivel for config
for config_line in parsivel.readlines(): # print config
    logger.info(msg=f'Config: {config_line}')


while True:
    try:
        parsivel_lines = parsivel.readlines()  # Reads the output the serial communication
        now_utc = datetime.utcnow()
        now_utc_iso = now_utc.isoformat()
        now_utc_ymd = now_utc.strftime("%Y%m%d")
        filename = f"{now_utc_ymd}_{config_dict['Parsivel_name']}.csv"
        create_new_csv(csv_path=data_dir / filename) # if does not exist
        filename_field_d61 = f"{now_utc_ymd}_{config_dict['Parsivel_name']}_field61.csv"
        if len(parsivel_lines) == 1 and len(parsivel_lines[0]) >= 20:
            # single message with all fields, except 61
            parsivel_str_list = binary2list(binarystr=parsivel_lines[0], spliter=';')
            with open(data_dir / filename, "a") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([now_utc_iso] + parsivel_str_list)
            logger.info(msg=f'Written row to {filename}')
            parsivel.write(parsivel_request_field_61)  # request field 61
        elif len(parsivel_lines) > 1:
            # field 61 condition
            with open(data_dir / filename_field_d61, "a") as g:  # 61
                writer = csv.writer(g, delimiter=";")
                for line in parsivel_lines:
                    if len(line) > 5 and len(line) < 20:
                        # TODO: process parsivel_lines to str and remove non-printing chars
                        parsivel_str_list = binary2list(binarystr=line, spliter=';')
                        writer.writerow([now_utc_iso] + parsivel_str_list)
                        logger.info(msg=f'Written row to {filename_field_d61} {parsivel_str_list}')
    except Exception as e:
        if hasattr(e, 'message'):
            print(e.message)
        else:
            print(e)
