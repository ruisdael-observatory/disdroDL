import re
from datetime import datetime
from pathlib import Path
from time import sleep
from modules.util_functions import yaml2dict, create_dir, create_new_csv, init_serial, capture_telegram_prfx_vars, append_csv_row, string2row, join_f61_items, csv_headers
from modules.parsivel_cmds import *
from modules.log import log 

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
parsivel.write(parsivel_set_station_name)
sleep(1)
parsivel.write(parsivel_set_ID)
sleep(2)
parsivel.write(parsivel_restart)  # resets rain amount
sleep(10)
parsivel.write(parsivel_user_telegram) 

flag_zero_seconds = False
while True:
    # try:
    now_utc = datetime.utcnow()
    now_hour_min_secs = now_utc.strftime("%H:%M:%S")
    now_hour_min_secs = now_hour_min_secs.split(":")
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
        # although requested in the same telegram string,
        # single value fields(svfs) and multi value fields are appended to telegram string
        # so that svfs numbers can be used in CSV headers 
        svfs = '%01;%02;%03;%04;%05;%06;%07;%08;%09;%10;%11;%12;%13;%14;%15;%16;%17;%18;%20;%21;%22;%23;%24;%25;%26;%27;%28;%30;%31;%32;%33;%34;%35;%60;'
        svfs_prefix = 'SVFS:'  # Single Value Fields; for identification 
        svfs_cmd = 'CS/M/S/' + svfs_prefix
        svfs_cmd = (svfs_cmd + svfs + '\nF90:%90;\nF91:%91;\nF93:%93;\nF61:%61;\r').encode('utf-8')
        parsivel.write(svfs_cmd)
        sleep(1)
        parsivel.write('CS/P\r\n'.encode('utf-8'))
        telegram_lines=parsivel.readlines()

        # create CSVs
        csvs_suffixes = {'SVFS':None, 'F90':None, 'F91':None, 'F93':None, 'F61':None}
        for suffix in csvs_suffixes:
            filename = f"{now_utc_ymd}_{config_dict['station_site']}-{config_dict['station_name']}_{config_dict['Parsivel_name']}_{suffix}.csv"
            csvs_suffixes[suffix] = filename
            if suffix == 'SVFS':
                headers = csv_headers(sfvs_telegram_resquest=svfs, config_dict=config_dict)
                print('headers:', headers)  
            else:
                headers = []
            created_new_csv = create_new_csv(csv_path=data_dir / csvs_suffixes[suffix], headers=headers)
            if created_new_csv:
                logger.info(msg=f'Created CSV: {data_dir / csvs_suffixes[suffix]}')
        parsivel_str_list = None
        prefix = None
        filename = None
        print('telegram_lines:', telegram_lines)
        for telegram_line in telegram_lines:
            prefix, values = capture_telegram_prfx_vars(telegram_line=telegram_line)
            if prefix and values and prefix == 'F61':
                f61_rows =[]
                f61_values_items = join_f61_items(telegram_list=telegram_lines)
                for f61_item in f61_values_items:
                    f61row = string2row(timestamp=now_utc_iso, valuestr=f61_item, delimiter=';', prefix=prefix)
                    f61_rows.append(f61row)
                print('F61:', f61_rows)
                values_list = f61_rows
                append_csv_row(data_dir=data_dir, filename=csvs_suffixes[prefix], delimiter=';', data_list=values_list)
                filename=csvs_suffixes[prefix]                    
                print('write to:', filename, 'prefix:', prefix)

            elif prefix and values and prefix != 'F61':
                values_list = string2row(timestamp=now_utc_iso, valuestr=values, delimiter=';', prefix=prefix)
                append_csv_row(data_dir=data_dir, filename=csvs_suffixes[prefix], delimiter=';', data_list=values_list)
                filename=csvs_suffixes[prefix]                    
                print('write to:', filename, 'prefix:', prefix)
                                    
                # reset vars
                prefix = None
                filename = None 
        print('\n')

    elif int(now_hour_min_secs[2]) != 0 and flag_zero_seconds == True:
        # once we passed 00secs: reset flag_zero_seconds
        flag_zero_seconds = False
    # except Exception as e:
    #     if hasattr(e, 'message'):
    #         print(e.message)
    #         logger.error(msg=e.message)
    #     else:
    #         print(e)
    sleep(1)


# TODO:
# * monthly dir creation
# - [X] write to CSV 
#   - [X] Single Value Fields
#   - [X] F90
#   - [X] F91
#   - [X] F93
# - [x] CSV headers: 
    # - [x] numbers
    # - [x] parameter names
# - [X] set Station name
# - [X]	set Station number 

# use of classes to store 
# documentation on seperate CSVs

# F61: [['2023-02-20T12:33:00.694872', '00.362', '02.338']]
# sequence item 0: expected str instance, list found

# Error: list index out of range

