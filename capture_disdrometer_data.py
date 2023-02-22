from datetime import datetime
from pathlib import Path
from time import sleep
from modules.util_functions import yaml2dict, create_dir, create_new_csv, init_serial, capture_telegram_prfx_vars, append_csv_row, string2row, join_f61_items, csv_headers, interruptHandler, create_logger
from modules.parsivel_cmds import *
from modules.classes import NowTime
from modules.log import log 

wd = Path(__file__).parent 
config_dict = yaml2dict(path = wd / 'config.yml')

logger = create_logger(log_dir=Path(config_dict['log_dir']), 
                       script_name=config_dict['script_name'], 
                       parsivel_name=config_dict['Parsivel_name'])
logger.info(msg=f"Starting {__file__} for {config_dict['Parsivel_name']}")
print(f"{__file__} running\nLogs written to {config_dict['log_dir']}")


parsivel = init_serial(port=config_dict['port'], baud=config_dict['baud'], logger=logger)  # initiate serial connection
parsivel.reset_input_buffer()  # Flushes input buffer
parsivel.write(parsivel_set_station_name)
sleep(1)
parsivel.write(parsivel_set_ID)
sleep(2)
parsivel.write(parsivel_restart)  # resets rain amount
sleep(10)
parsivel.write(parsivel_user_telegram) 

flag_zero_seconds = False
try:
    while True:
        now_utc = NowTime()
        if int(now_utc.time_list[2]) == 0 and flag_zero_seconds == False:
            now_utc.date_strings()
            print('time to write:', now_utc.time_list, now_utc.ymd, datetime.utcnow().strftime("%H:%M:%S"))
            flag_zero_seconds = True
            # create dir
            data_dir = Path(config_dict['data_dir']) / now_utc.ym # create monthly data dir
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
                filename = f"{now_utc.ymd}_{config_dict['station_site']}-{config_dict['station_name']}_{config_dict['Parsivel_name']}_{suffix}.csv"
                csvs_suffixes[suffix] = filename
                if suffix == 'SVFS':
                    headers = csv_headers(sfvs_telegram_resquest=svfs, config_dict=config_dict)
                    print('headers:', headers)
                elif suffix == 'F61':
                    headers = ['timestamp', 
                               f"{config_dict['telegram_fields']['61size']['name']} ({config_dict['telegram_fields']['61size']['unit']})", 
                               f"{config_dict['telegram_fields']['61speed']['name']} ({config_dict['telegram_fields']['61speed']['unit']})"]                    
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
                if prefix and len(values) > 1 and prefix == 'F61':  # len(values) > 1 since ";" can be captured without values
                    f61_rows =[]
                    f61_values_items = join_f61_items(telegram_list=telegram_lines)
                    for f61_item in f61_values_items:
                        f61row = string2row(timestamp=now_utc.iso, valuestr=f61_item, delimiter=';', prefix=prefix)
                        f61_rows.append(f61row)
                    print('F61:', f61_rows)
                    append_csv_row(data_dir=data_dir, filename=csvs_suffixes[prefix], delimiter=';', data_list=f61_rows)
                    filename=csvs_suffixes[prefix]                    
                    print('write to:', filename, 'prefix:', prefix)

                elif prefix and values and prefix != 'F61':
                    values_list = string2row(timestamp=now_utc.iso, valuestr=values, delimiter=';', prefix=prefix)
                    append_csv_row(data_dir=data_dir, filename=csvs_suffixes[prefix], delimiter=';', data_list=values_list)
                    filename=csvs_suffixes[prefix]                    
                    print('write to:', filename, 'prefix:', prefix)
                                        
                    # reset vars
                    prefix = None
                    filename = None 
            print('\n')

        elif int(now_utc.time_list[2]) != 0 and flag_zero_seconds == True:
            # once we passed 00secs: reset flag_zero_seconds
            flag_zero_seconds = False
        sleep(1)
except (Exception, KeyboardInterrupt) as e:
    interruptHandler(serial_connection=parsivel, logger=logger)
    if hasattr(e, 'message'):
        print(e.message)
        logger.error(msg=e.message)



# TODO:
# - [X] F61 CSV headers
# - [X] re-enable exception
# - [ ] refactor
#   - [ ] use of classes data and methods 
# - [ ] documentation 
#     - [ ] program logic
#     - [ ] on seperate CSVs
