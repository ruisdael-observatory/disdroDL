from pathlib import Path
from time import sleep
from argparse import ArgumentParser
from modules.util_functions import yaml2dict, create_dir, init_serial, create_logger, parsivel_start_sequence
from modules.classes import NowTime, Telegram
from modules.sqldb import create_db, connect_db
from pydantic.v1.utils import deep_update

######################## BOILER PLATE ##################

### Parser ###
parser = ArgumentParser(
    description="Ruisdael: OTT Disdrometer data logger. Run: python capture_disdrometer_data.py -c config_*.yml")
parser.add_argument(
    '-c',
    '--config',
    required=True,
    help='Path to site config file. ie. -c configs_netcdf/config_008_GV.yml')
args = parser.parse_args()

### Config files ###
wd = Path(__file__).parent
config_dict = yaml2dict(path=wd / 'configs_netcdf' / 'config_general.yml')
config_dict_site = yaml2dict(path=wd / args.config)
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

### DB ###
db_path = Path(config_dict['data_dir']) / 'disdrodl.db'
create_db(dbpath=str(db_path))

#########################################################

# flag_zero_seconds = False
# flag_compressed = False
# while True:
#     now_utc = NowTime()
#     if int(now_utc.time_list[2]) == 0 and flag_zero_seconds is False:
#         con, cur = connect_db(dbpath=str(db_path))
#         flag_zero_seconds = True
#         logger.debug(msg=f'writing Telegram to DB on: {now_utc.time_list}, {now_utc.utc}')

#         parsivel.write('CS/PA\r\n'.encode('ascii'))  # Output all telegram measurement values
#         parsivel_lines = parsivel.readlines()
#         try:
#             parsivel_lines[0]
#         except IndexError:
#             logger.error(msg="parsivel_lines is EMPTY")
#         # logger.debug(msg=f"parsivel_lines: {parsivel_lines}")
#         # insert telegram to db
#         telegram = Telegram(config_dict=config_dict,
#                             telegram_lines=parsivel_lines,
#                             timestamp=now_utc.utc,
#                             db_cursor=cur,
#                             telegram_data={},
#                             logger=logger)
#         # logger.debug(msg=f'telegram_lines:{telegram.telegram_lines}')
#         telegram.capture_prefixes_and_data()
#         telegram.prep_telegram_data4db()
#         telegram.insert2db()
#         con.commit()
#         cur.close()
#         con.close()
#     elif int(now_utc.time_list[2]) != 0 and flag_zero_seconds is True:
#         # once we passed 00secs: reset flag_zero_seconds
#         flag_zero_seconds = False
#     sleep(1)

while True:
    now_utc = NowTime()

    # continue if the seconds are not 0 and sleep for 1 second
    if int(now_utc.time_list[2]) != 0:
        sleep(1)
        continue

    # only log data if the seconds are 0, resulting in data getting logged once a minute
    con, cur = connect_db(dbpath=str(db_path))
    logger.debug(msg=f'writing Telegram to DB on: {now_utc.time_list}, {now_utc.utc}')

    parsivel.write('CS/PA\r\n'.encode('ascii'))  # Output all telegram measurement values
    parsivel_lines = parsivel.readlines()

    # throw error if parsivel_lines is empty
    try:
        parsivel_lines[0]
    except IndexError:
        logger.error(msg="parsivel_lines is EMPTY")
        
    # logger.debug(msg=f"parsivel_lines: {parsivel_lines}")

    # insert telegram to db
    telegram = Telegram(config_dict=config_dict,
                        telegram_lines=parsivel_lines,
                        timestamp=now_utc.utc,
                        db_cursor=cur,
                        telegram_data={},
                        logger=logger)

    # logger.debug(msg=f'telegram_lines:{telegram.telegram_lines}')
    
    telegram.capture_prefixes_and_data()
    telegram.prep_telegram_data4db()
    telegram.insert2db()
    con.commit()
    cur.close()
    con.close()

    # sleep for 2 seconds to guarantee you don't log the same data twice
    # this causes issues with a computation time of 58 seconds
    sleep(2)
    