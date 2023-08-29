from pathlib import Path
from time import sleep
from argparse import ArgumentParser
from modules.util_functions import yaml2dict, create_dir, init_serial, create_logger, parsivel_start_sequence
from modules.classes import NowTime, Telegram
from pydantic.utils import deep_update

######################## BOILER PLATE ##################
### Parser ###
parser = ArgumentParser(description="Ruisdael: OTT Disdrometer data logger. Run: python capture_disdrometer_data.py -c config_*.yml")
parser.add_argument('-c', '--config', required=True, help='Observation site config file. ie. -c config_008_GV.yml')
args = parser.parse_args()
### Config files ###
wd = Path(__file__).parent 
config_dict = yaml2dict(path = wd / 'config_general.yml')
config_dict_site = yaml2dict(path = wd / args.config)  # TODO: come from cli
config_dict = deep_update(config_dict, config_dict_site)
### Log ###
logger = create_logger(log_dir=Path(config_dict['log_dir']), 
                       script_name=config_dict['script_name'], 
                       parsivel_name=config_dict['global_attrs']['sensor_name'])
logger.info(msg=f"Starting {__file__} for {config_dict['global_attrs']['sensor_name']}")
print(f"{__file__} running\nLogs written to {config_dict['log_dir']}")
### Serial connection ###
parsivel = init_serial(port=config_dict['port'], baud=config_dict['baud'], logger=logger)  # initiate serial connection
parsivel_start_sequence(serialconnection=parsivel, config_dict=config_dict, logger=logger)
sleep(2)
#########################################################

flag_zero_seconds = False
flag_compressed = False
# try:
while True:
    now_utc = NowTime()
    if int(now_utc.time_list[2]) == 0 and flag_zero_seconds == False:
        flag_zero_seconds = True
        print('time to write:', now_utc.time_list, now_utc.utc)

        # (monthly) data dir
        data_dir = Path(config_dict['data_dir']) / now_utc.ym 
        created_data_dir = create_dir(data_dir) # create if does not exist
        if created_data_dir:
            logger.info(msg=f'Created data directory: {data_dir}')

        # returned telegram lines  
        fn_start = f"{now_utc.ymd}_{config_dict['global_attrs']['site_name']}-{config_dict['station_code']}_{config_dict['global_attrs']['sensor_name']}"
        parsivel.write('CS/PA\r\n'.encode('ascii')) # Output all telegram measurement values
        parsivel_lines = parsivel.readlines()
        logger.info(msg=f"parsivel_lines: {parsivel_lines}")

        # process telegram into netCDF
        telegram = Telegram(config_dict=config_dict,
                            telegram_lines=parsivel_lines, 
                            timestamp=now_utc.utc, 
                            data_dir=data_dir,
                            data_fn_start=fn_start,
                            logger=logger)    
        logger.debug(msg=f'telegram_lines:{telegram.telegram_lines}')
        telegram.capture_prefixes_and_data()
        telegram.append_data_to_netCDF()
        
        if ((now_utc.utc - now_utc.last_minute_of_day).total_seconds()/60.0) <= 0.0 and flag_compressed == False:
            # if now is 23:59 - compress todays netCDF  
            logger.debug(msg=f'compression time - last_minute_of_day: {now_utc.last_minute_of_day}. Seconds diff {((now_utc.utc - now_utc.last_minute_of_day).total_seconds()/60.0)}')
            flag_compressed = True
            telegram.compress_netcdf()
            pass
        else:
            flag_compressed = False 

    elif int(now_utc.time_list[2]) != 0 and flag_zero_seconds == True:
        # once we passed 00secs: reset flag_zero_seconds
        flag_zero_seconds = False
    sleep(1)
# except (Exception, KeyboardInterrupt) as e:
#     interruptHandler(serial_connection=parsivel, logger=logger)
#     if hasattr(e, 'message'):
#         print(e.message)
#         logger.error(msg=e.message)

