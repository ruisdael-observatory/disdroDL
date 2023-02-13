import csv
from datetime import datetime
from pathlib import Path
from  util_functions import yaml2dict, create_dir, create_new_csv, binary2list, init_serial
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
parsivel.write('CS/Z/1\r\n'.encode('utf-8'))  # Restart sensor, reset the rain amount
sleep(10)
parsivel.write('CS/M/M/1\r\n'.encode('utf-8')) # User defined telegram


flag_zero_seconds = False
while True:
    now_utc = datetime.utcnow()
    now_hour_min_secs = now_utc.strftime("%H:%M:%S")
    now_hour_min_secs = now_hour_min_secs.split(":")
    if int(now_hour_min_secs[2]) == 0 and flag_zero_seconds == False:
        print(now_hour_min_secs, datetime.utcnow().strftime("%H:%M:%S"))
        flag_zero_seconds = True

        # create dir
        now_utc_ym = now_utc.strftime("%Y%m")
        data_dir = Path(config_dict['data_dir']) / now_utc_ym # create monthly data dir
        created_data_dir = create_dir(data_dir)
        if created_data_dir:
            logger.info(msg=f'Created data directory: {data_dir}')
        # request telegram
        parsivel.write('CS/M/S/SFs:%01,%02,%03,%04,%05,%06,%07,%08,%09,%10,%11,%12,%13,%14,%15,%16,%17,%18,%20,%21,%22,%23,%24,%25,%26,%27,%28,%30,%31,%32,%33,%34,%35,%60,\nF90:%90,\nF91:%91,\nF93:%93,\nF61:%61;\r\n'.encode('utf-8'))
        sleep(1)
        parsivel.write('CS/P\r\n'.encode('utf-8'))
        telegram_single_values=parsivel.readlines()
        for index, item in enumerate(telegram_single_values):
            print(index, item)
        print('\n')

    elif int(now_hour_min_secs[2]) != 0 and flag_zero_seconds == True:

        # once we passed 00secs 
        # reset flag_zero_seconds
        flag_zero_seconds = False
    sleep(1)


# TODO:
# * check how field 61 is written 
# * monthly dir creation