from argparse import ArgumentParser
from datetime import datetime, date, timedelta, timezone
from pathlib import Path
from pydantic.v1.utils import deep_update
from modules.util_functions import yaml2dict, create_dir, create_logger
from modules.telegram import Telegram
from modules.netCDF import NetCDF
from modules.sqldb import query_db_rows_gen, connect_db
from netCDF4 import Dataset
import yaml


date_today = date.today()
date_yest = date_today - timedelta(days=1)

if __name__ == '__main__':
    # parser = ArgumentParser(
    #     description="Export 1 day of parsivel data from DB to NetCDF.\
    #         Run: python export_daily_netcdf.py -c configs_netcdf/config_007_CABAUW.yml\
    #             -d 2023-12-17 \
    #         Output netCDF: store in same directory as input file")
    # parser.add_argument(
    #     '-c',
    #     '--config',
    #     required=True,
    #     help='Path to site config file. ie. -c configs_netcdf/config_007_CABAUW.yml')
    # parser.add_argument(
    #     '-d',
    #     '--date',
    #     default=date_yest.strftime('%Y-%m-%d'),
    #     help='Date string for files to be captured. Format: YYYY-mm-dd')

    # args = parser.parse_args()
    date = "2024-05-14"
    date_dt = datetime.strptime(date, '%Y-%m-%d')
    wd = Path(__file__).parent
    with open('configs_netcdf/config_general_thies.yml',encoding="utf8") as f:
        dict = yaml.safe_load(f)
   #     print(dict)
    config_dict = dict
    config_dict_site = yaml2dict(path=wd / 'configs_netcdf' / 'config_008_GV_THIES.yml')
   # config_dict_site = yaml2dict(path=wd / args.config)
    config_dict = deep_update(config_dict, config_dict_site)
    site_name = "green_village"
    st_code = "006"
    sensor_name = "ThIES"
    fn_start = f"{date.replace('-', '')}_{site_name}-{st_code}_{sensor_name}"
    db_path = Path("C:/Users/jesse/disdrodl-thies.db")
    logger = create_logger(log_dir=Path('/var/log/disdroDL/'),
                           script_name='disdro_db2nc',
                           parsivel_name='THIES006')

    msg_conf = f"Starting {__file__} for THIES006"
    logger.info(msg=msg_conf)
    msg_date = f'Exporting data from {date_dt} to {date_dt.replace(hour=23, minute=59, second=59)}'
    logger.info(msg=msg_date)
    # -- Monthly Data dir
    data_dir = Path('sample_data/')
    created_data_dir = create_dir(path=data_dir)  # create if does not exist
    if created_data_dir:
        logger.info(msg=f'Created data directory: {data_dir}')
    # -- DB rows -> Telegram instances
    telegram_objs = []
    cur, con = connect_db(dbpath='sample_data/disdrodl-thies.db')
    for row in query_db_rows_gen(con, date_dt=date_dt, logger=logger):
        ts_dt = datetime.fromtimestamp(row.get('timestamp'), tz=timezone.utc)
        telegram_instance = Telegram(
            config_dict=config_dict,
            telegram_lines=row.get('telegram'),
            db_row_id=row.get('id'),
            timestamp=ts_dt,
            db_cursor=None,
            telegram_data={},
            logger=logger)
        telegram_instance.parse_telegram_row()
        # check if telegram_instance has data organized by keys(fields)
        if "90" in telegram_instance.telegram_data.keys():
            telegram_objs.append(telegram_instance)

    con.close()
    cur.close()
    # -- NetCDF creation
    nc = NetCDF(logger=logger,
                config_dict=config_dict,
                data_dir=data_dir,
                fn_start=fn_start,
                telegram_objs=telegram_objs,
                date=date_dt)
    nc.create_netCDF()
    nc.write_data_to_netCDF()
    nc.compress()
