import csv
import re
from datetime import datetime
from pathlib import Path
from  util_functions import yaml2dict, create_dir, create_new_csv, init_serial, parsivel_list_2_csv
from parsivel_cmds import *
from log import log 
from time import sleep


print('starting script')

wd = Path(__file__).parent 
config_dict = yaml2dict(path = wd / 'config.yml')

# set up log
log_dir = Path(config_dict['log_dir'])
created_log_dir = create_dir(log_dir)
log_file = log_dir / 'log.json'
logger = log(log_path=log_file, 
            log_name=f"{config_dict['script_name']}: {config_dict['Parsivel_name']}")  
logger.info(msg=f"Starting {__file__} for {config_dict['Parsivel_name']}")
print(f'{__file__} running\nLogs written to {log_dir}')



# intiated serial connection
parsivel = init_serial(port=config_dict['port'], baud=config_dict['baud'], logger=logger)
parsivel.reset_input_buffer()  # Flushes input buffer
sleep(10)
parsivel.write('CS/M/M/1\r\n'.encode('utf-8')) # User defined telegram

svfs_cmd = 'CS/M/S/F61:%61;\r\n'.encode('utf-8')
parsivel.write(svfs_cmd)
sleep(1)
parsivel.write('CS/P\r\n'.encode('utf-8'))
telegram_lines=parsivel.readlines()
print(telegram_lines)

while True:
    now_utc = datetime.utcnow()
    now_hour_min_secs = now_utc.strftime("%H:%M:%S")    
    print(now_hour_min_secs)
    for telegram_line in telegram_lines:
        print('line', telegram_line)
    sleep(60)
