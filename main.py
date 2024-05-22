"""
This module contains the main loop to log data once every minute.

After setting up the logger and the connection with the database,
the code enters a permanent while loop where each time the seconds are 0,
data gets logged to the database.
"""
import sys
from pathlib import Path
from time import sleep
from argparse import ArgumentParser
from pydantic.v1.utils import deep_update

from modules.sensors import Parsivel, Thies
from modules.util_functions import yaml2dict, create_logger
from modules.telegram import ParsivelTelegram, ThiesTelegram
from modules.now_time import NowTime
from modules.sqldb import create_db, connect_db

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

config_dict_site = yaml2dict(path=wd / args.config)

### Log ###
logger = create_logger(log_dir=Path(config_dict_site['log_dir']),
                       script_name=config_dict_site['script_name'],
                       sensor_name=config_dict_site['global_attrs']['sensor_name'])
logger.info(msg=f"Starting {__file__} for {config_dict_site['global_attrs']['sensor_name']}")
print(f"{__file__} running\nLogs written to {config_dict_site['log_dir']}")

config_dict = None

sensor_type = config_dict_site['global_attrs']['sensor_type']
if sensor_type == 'OTT Hydromet Parsivel2':
    config_dict = yaml2dict(path=wd / 'configs_netcdf' / 'config_general_parsivel.yml')
elif sensor_type == 'Thies clima':
    config_dict = yaml2dict(path=wd / 'configs_netcdf' / 'config_general_thies.yml')
else:
    logger.error(msg=f"Sensor type {sensor_type} not recognized")
    sys.exit(1)

config_dict = deep_update(config_dict, config_dict_site)



### Serial connection ###

sensor = None
if sensor_type == 'OTT Hydromet Parsivel2':
    sensor = Parsivel()
elif sensor_type == 'Thies clima':
    sensor = Thies()
else:
    logger.error(msg=f"Sensor type {sensor_type} not recognized")
    sys.exit(1)

sensor.init_serial_connection(port=config_dict['port'], baud=config_dict['baud'], logger=logger)
sensor.sensor_start_sequence(config_dict=config_dict, logger=logger)
sleep(2)

### DB ###
db_path = Path(config_dict['data_dir']) / 'disdrodl-test1.db'  # change the db name
create_db(dbpath=str(db_path))

#########################################################

while True:
    now_utc = NowTime()

    # if the seconds are not 0, sleep for 1 second and then continue
    if int(now_utc.time_list[2]) != 0:
        sleep(1)
        continue

    # only log data if the seconds are 0, resulting in data getting logged once a minute
    con, cur = connect_db(dbpath=str(db_path))
    logger.debug(msg=f'writing Telegram to DB on: {now_utc.time_list}, {now_utc.utc}')

    # Read telegram from the sensor
    telegram_lines = sensor.read(logger=logger)

    # throw error if telegram_lines is empty
    try:
        telegram_lines[0]
    except IndexError:
        logger.error(msg="sensor_lines is EMPTY")

    # logger.debug(msg=f"parsivel_lines: {parsivel_lines}")

    telegram = None

    if sensor_type == 'OTT Hydromet Parsivel2':
        telegram = ParsivelTelegram(config_dict=config_dict,
                                    telegram_lines=telegram_lines,
                                    timestamp=now_utc.utc,
                                    db_cursor=cur,
                                    telegram_data={},
                                    logger=logger)
    elif sensor_type == 'Thies clima':
        telegram = ThiesTelegram(config_dict=config_dict,
                                 telegram_lines=telegram_lines,
                                 timestamp=now_utc.utc,
                                 db_cursor=cur,
                                 telegram_data={},
                                 logger=logger)
    else:
        logger.error(msg=f"Sensor type {sensor_type} not recognized")
        sys.exit(1)

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
