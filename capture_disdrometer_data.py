import csv
import re
from datetime import datetime
from pathlib import Path
from  util_functions import yaml2dict, create_dir, create_new_csv, binary2list, init_serial, parsivel_list_2_csv
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
    try:
        now_utc = datetime.utcnow()
        now_hour_min_secs = now_utc.strftime("%H:%M:%S")
        now_hour_min_secs = now_hour_min_secs.split(":")
        print(now_hour_min_secs)
        if int(now_hour_min_secs[2]) == 0 and flag_zero_seconds == False:
            print('time to write:', now_hour_min_secs, datetime.utcnow().strftime("%H:%M:%S"))
            flag_zero_seconds = True
            # dates
            now_utc_iso = now_utc.isoformat()
            now_utc_ym = now_utc.strftime("%Y%m")
            now_utc_ymd = now_utc.strftime("%Y%m%d")
            # create dir
            data_dir = Path(config_dict['data_dir']) / now_utc_ym # create monthly data dir
            created_data_dir = create_dir(data_dir)
            if created_data_dir:
                logger.info(msg=f'Created data directory: {data_dir}')

            # request telegram
            svfs = '%01;%02;%03;%04;%05;%06;%07;%08;%09;%10;%11;%12;%13;%14;%15;%16;%17;%18;%20;%21;%22;%23;%24;%25;%26;%27;%28;%30;%31;%32;%33;%34;%35;%60;'
            svfs_prefix = 'SVFS:'  # Single Value Fields; for identification 
            svfs_cmd = 'CS/M/S/' + svfs_prefix
            svfs_cmd = (svfs_cmd + svfs + '\nF90:%90;\nF91:%91;\nF93:%93;\nF61:%61;\r\n').encode('utf-8')
            parsivel.write(svfs_cmd)
            sleep(1)
            parsivel.write('CS/P\r\n'.encode('utf-8'))
            telegram_single_values=parsivel.readlines()

            # create CSVs
            csvs_suffixes = {'SVFS':None, 'F90':None, 'F91':None, 'F93':None, 'F61':None}
            for suffix in csvs_suffixes:
                filename = f"{now_utc_ymd}_{config_dict['station_site']}-{config_dict['station_name']}_{config_dict['Parsivel_name']}_{suffix}.csv"
                csvs_suffixes[suffix] = filename
                if suffix == 'SVFS':
                    headers = ["timestamp"] + ((svfs.replace('%','')).split(';'))
                    headers = headers[:-1] # remove last (empty) item from headers list
                    print('headers:', headers)  
                else:
                    headers = []
                created_new_csv = create_new_csv(csv_path=data_dir / csvs_suffixes[suffix], headers=headers)
                if created_new_csv:
                    logger.info(msg=f'Created CSV: {data_dir / csvs_suffixes[suffix]}')
            parsivel_str_list = None
            prefix = None
            filename = None
            for item in telegram_single_values:
                #capture prefix 
                prefix_match = re.match(r'(^F\d\d:)', item.decode('utf-8'))
                prefix = prefix_match.group(0)
                print('RE prefix:', prefix)
                filename=csvs_suffixes[prefix.replace(":",'')]
                # if (item.decode('utf-8')).startswith(svfs_prefix):
                #     filename=csvs_suffixes['SVFS']
                #     prefix = 'SVFS:'
                # elif (item.decode('utf-8')).startswith('F90'):
                #     print("F90:", item)
                #     filename=csvs_suffixes['F90']
                #     prefix = 'F90:'
                # elif (item.decode('utf-8')).startswith('F91'):
                #     filename=csvs_suffixes['F91']
                #     prefix = 'F91:'
                #     print("F91:", item)
                # elif (item.decode('utf-8')).startswith('F93'):
                #     filename=csvs_suffixes['F93']
                #     prefix = 'F93:'
                #     print("F93:", item)
                # elif (item.decode('utf-8')).startswith('F61'):
                #     filename=csvs_suffixes['F61']
                #     prefix = 'F61:'
                #     print("F61:", item) 
    
                if item and prefix and filename:
                    print('write to:', filename, 'prefix:', prefix)
                    parsivel_list_2_csv(timestamp=now_utc_iso, binarystr=item, delimiter=';', 
                                        prefix=prefix, data_dir=data_dir, filename=filename)
                    # reset vars
                    parsivel_str_list = None
                    prefix = None
                    filename = None 
            print('\n')


        elif int(now_hour_min_secs[2]) != 0 and flag_zero_seconds == True:
            # once we passed 00secs: reset flag_zero_seconds
            flag_zero_seconds = False
    except Exception as e:
        if hasattr(e, 'message'):
            print(e.message)
            logger.error(msg=e.message)
        else:
            print(e)
    sleep(1)


# TODO:
# * check how field 61 is written 
# * monthly dir creation
# - [X] write to CSV 
#   - [ ] Single Value Fields 
# - [ ] CSV headers: 
    # - [x] numbers
    # - [ ] parameter names
# * write to several CSVs
# * add timestamp to CSV headers
# documentation on seperate CSVs