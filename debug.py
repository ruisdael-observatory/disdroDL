from pathlib import Path
from time import sleep
from modules.util_functions import yaml2dict, create_dir, init_serial, parsivel_start_sequence, create_logger
from modules.classes import NowTime
wd = Path(__file__).parent 
config_dict = yaml2dict(path = wd / 'config.yml')


logger = create_logger(log_dir=Path(config_dict['log_dir']), 
                       script_name=config_dict['script_name'], 
                       parsivel_name=config_dict['Parsivel_name'])
logger.info(msg=f"Starting {__file__} for {config_dict['Parsivel_name']}")

svfs = '%01;%02;%03;%04;%05;%06;%07;%08;%09;%10;%11;%12;%13;%14;%15;%16;%17;%18;%20;%21;%22;%23;%24;%25;%26;%27;%28;%30;%31;%32;%33;%34;%35;%60;'
user_telegram_str = f'CS/M/S/SVFS:' 
user_telegram_str = (user_telegram_str + svfs + '\r').encode('utf-8')

# Serial connection
parsivel = init_serial(port=config_dict['port'], baud=config_dict['baud'], logger=logger)  # initiate serial connection
parsivel_start_sequence(serialconnection=parsivel, config_dict=config_dict, logger=logger)

flag_zero_seconds = False
while True:
    now_utc = NowTime()
    if int(now_utc.time_list[2]) == 0 and flag_zero_seconds == False:
        flag_zero_seconds = True
        now_utc.date_strings()
        print('time to write:', now_utc.time_list, now_utc.utc)

        # Request telegram:
        parsivel.write(user_telegram_str)  # string format
        sleep(1)
        parsivel.write('CS/P\r\n'.encode('utf-8')) # poll
        lines = parsivel.readlines()
        print(f'Lines: {lines}')
    elif int(now_utc.time_list[2]) != 0 and flag_zero_seconds == True:
        # once we passed 00secs: reset flag_zero_seconds
        flag_zero_seconds = False
    sleep(1)
