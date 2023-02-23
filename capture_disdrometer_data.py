from pathlib import Path
from time import sleep
from modules.util_functions import yaml2dict, create_dir, init_serial, interruptHandler, create_logger, parsivel_start_sequence

from modules.classes import NowTime, Telegram
# from modules.log import log 

wd = Path(__file__).parent 
config_dict = yaml2dict(path = wd / 'config.yml')

logger = create_logger(log_dir=Path(config_dict['log_dir']), 
                       script_name=config_dict['script_name'], 
                       parsivel_name=config_dict['Parsivel_name'])
logger.info(msg=f"Starting {__file__} for {config_dict['Parsivel_name']}")
print(f"{__file__} running\nLogs written to {config_dict['log_dir']}")

# Telegram request string:
# although requested in the same telegram string (user_telegram_str)
#   single value fields(svfs) and multi value fields are appended to user_telegram_str
#   so that svfs numbers can be used in CSV headers 
prefixes_list = ['SVFS', 'F61', 'F90', 'F91', 'F93']
svfs = '%01;%02;%03;%04;%05;%06;%07;%08;%09;%10;%11;%12;%13;%14;%15;%16;%17;%18;%20;%21;%22;%23;%24;%25;%26;%27;%28;%30;%31;%32;%33;%34;%35;%60;'
user_telegram_str = f'CS/M/S/{prefixes_list[0]}:' 
user_telegram_str = (user_telegram_str + svfs + '\nF90:%90;\nF91:%91;\nF93:%93;\nF61:%61;\r').encode('utf-8')

# Serial connection
parsivel = init_serial(port=config_dict['port'], baud=config_dict['baud'], logger=logger)  # initiate serial connection
parsivel_start_sequence(serialconnection=parsivel, config_dict=config_dict, logger=logger)

flag_zero_seconds = False
# try:
while True:
    now_utc = NowTime()
    if int(now_utc.time_list[2]) == 0 and flag_zero_seconds == False:
        flag_zero_seconds = True
        now_utc.date_strings()
        print('time to write:', now_utc.time_list, now_utc.utc)
        # create dir
        data_dir = Path(config_dict['data_dir']) / now_utc.ym # create monthly data dir
        created_data_dir = create_dir(data_dir)
        if created_data_dir:
            logger.info(msg=f'Created data directory: {data_dir}')

        # Request telegram:
        parsivel.write(user_telegram_str)  # string format
        sleep(1)
        parsivel.write('CS/P\r\n'.encode('utf-8')) # poll

        # Handle telegram 
        fn_start = filename = f"{now_utc.ymd}_{config_dict['station_site']}-{config_dict['station_name']}_{config_dict['Parsivel_name']}"
        telegram = Telegram(telegram_lines=parsivel.readlines(), 
                            timestamp=now_utc.iso, 
                            data_dir=data_dir,
                            data_fn_start=fn_start)    
        telegram.create_csv_headers(sfvs_telegram_resquest=svfs, config_dict=config_dict)
        telegram.capture_prefixes_and_data()
        for prefix in prefixes_list:
            telegram.append_data_to_csv(prefix=prefix)

    elif int(now_utc.time_list[2]) != 0 and flag_zero_seconds == True:
        # once we passed 00secs: reset flag_zero_seconds
        flag_zero_seconds = False
    sleep(1)
# except (Exception, KeyboardInterrupt) as e:
#     interruptHandler(serial_connection=parsivel, logger=logger)
#     if hasattr(e, 'message'):
#         print(e.message)
#         logger.error(msg=e.message)



# TODO:
# - [X] F61 CSV headers
# - [X] re-enable exception
# - [X] refactor
#   - [X] use of classes data and methods 
# - [ ] documentation 
#     - [ ] program logic
#     - [ ] on seperate CSVs

# issues:
# re enable try