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

if __name__ == '__main__':
    
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
            parsivel_bytes = parsivel.readline()  # Reads the output the serial communication
            parsivel_str = parsivel_bytes.decode('utf-8') 
            now_utc = datetime.utcnow()
            now_utc_iso = now_utc.isoformat()
            now_utc_ymd = now_utc.strftime("%Y%m%d")
            filename = f"{now_utc_ymd}_{config_dict['Parsivel_name']}.csv"
            filename_field_d61 = f"{now_utc_ymd}_{config_dict['Parsivel_name']}_field61.csv"
            
            if len(parsivel_bytes)> 5 and len(parsivel_bytes) < 20:
                # field 61 condition
                # TODO: process parsivel_bytes to str and remove non-printing chars
                with open(data_dir / filename_field_d61, "a") as g:  # 61
                    writer = csv.writer(g, delimiter=";")
                    writer.writerow([now_utc_iso, parsivel_bytes])
                logger.info(msg=f'Written row to {filename_field_d61} {parsivel_str}')
    
            elif len(parsivel_bytes) >= 20: 
                # message with all fields, except 61
                parsivel_str = parsivel_str.replace('\n','').replace('\r','') # strip non-printing chars
                with open(data_dir / filename, "a") as f:
                    writer = csv.writer(f, delimiter=";")
                    writer.writerow([now_utc_iso, parsivel_bytes])
                logger.info(msg=f'Written row to {filename}')
                parsivel.write(config_dict['parsivel_request_field_61'].encode('utf-8'))  # request field 61
                logger.info(msg=f"Requested F61: {config_dict['parsivel_request_field_61'].encode('utf-8')}")
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)
    