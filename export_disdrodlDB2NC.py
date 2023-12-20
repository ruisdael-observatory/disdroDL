from argparse import ArgumentParser
from datetime import datetime, date, timedelta
from pathlib import Path
from pydantic.v1.utils import deep_update
from modules.util_functions import yaml2dict, create_dir, create_logger
from modules.classes import Telegram, NetCDF
from modules.sqldb import create_db, connect_db, sql_query_gen


date_today = date.today()
date_yest = date_today - timedelta(days=1)

if __name__ == '__main__':
    parser = ArgumentParser(
        description="Export 1 day of parsivel data from DB to NetCDF.\
            Run: python export_daily_netcdf.py -c configs_netcdf/config_007_CABAUW.yml\
                -d 2023-12-17 \
            Output netCDF: store in same directory as input file")
    parser.add_argument(
        '-c',
        '--config',
        required=True,
        help='Path to site config file. ie. -c configs_netcdf/config_007_CABAUW.yml')
    parser.add_argument(
        '-d',
        '--date',
        default=date_yest.strftime('%Y-%m-%d'),
        help='Date string for files to be captured. Format: YYYY-mm-dd')

    args = parser.parse_args()
    date_dt = datetime.strptime(args.date, '%Y-%m-%d')
    # NOTE:  since date_dt is a datetime instance
    #        but not time data is provided
    #        it gets set 00:00:00 midnight
    wd = Path(__file__).parent
    config_dict = yaml2dict(path=wd / 'configs_netcdf' / 'config_general.yml')
    config_dict_site = yaml2dict(path=wd / args.config)
    config_dict = deep_update(config_dict, config_dict_site)
    site_name = config_dict['global_attrs']['site_name']
    st_code = config_dict['station_code']
    sensor_name = config_dict['global_attrs']['sensor_name']
    fn_start = f"{args.date.replace('-', '')}_{site_name}-{st_code}_{sensor_name}"
    db_path = Path(config_dict['data_dir']) / 'disdrodl.db'
    logger = create_logger(log_dir=Path(config_dict['log_dir']),
                           script_name=config_dict['script_name'],
                           parsivel_name=config_dict['global_attrs']['sensor_name'])

    msg_conf = f"Starting {__file__} for {config_dict['global_attrs']['sensor_name']}"
    logger.info(msg=msg_conf)
    print(msg_conf)
    msg_date = f'Exporting data from {date_dt} to {date_dt.replace(hour=23, minute=59, second=59)}' 
    logger.info(msg=msg_date)
    print(msg_date)

    # Monthly Data dir
    data_dir = Path(config_dict['data_dir']) / date_dt.strftime('%Y%m')
    created_data_dir = create_dir(path=data_dir)  # create if does not exist
    if created_data_dir:
        logger.info(msg=f'Created data directory: {data_dir}')
    # DB query
    con, cur = connect_db(dbpath=str(db_path))
    start_dt = date_dt.replace(hour=0, minute=0, second=0)  # redundant replace
    start_ts = start_dt.timestamp()
    end_dt = date_dt.replace(hour=23, minute=59, second=59)
    end_ts = end_dt.timestamp()
    query_str = f"SELECT * FROM disdrodl WHERE timestamp >= {start_ts} AND timestamp < {end_ts}"
    logger.debug(query_str)
    # Append each SQL response row as Telegram instance to telegram_objs var 
    telegram_objs = []
    for row in sql_query_gen(con=con, query=query_str):
        row_telegram = Telegram(
            config_dict=config_dict,
            telegram_lines=row.get('telegram'),
            timestamp=row.get('timestamp'),
            db_cursor=None,
            logger=logger,
            telegram_data={})
        row_telegram.parse_telegram_row()
        row_telegram.str2list(field='90', separator=',')
        row_telegram.str2list(field='91', separator=',')
        row_telegram.str2list(field='93', separator=',')
        telegram_objs.append(row_telegram)
    cur.close()
    con.close()
    # print('len telegram_objs:', len(telegram_objs))
    # print(telegram_objs[0].telegram_data)
    
    # TODO: what happens if telegram_objs is empty?
    nc = NetCDF(logger=logger,
                config_dict=config_dict,
                data_dir=data_dir,
                fn_start=fn_start,
                telegram_objs=telegram_objs,
                date=date_dt)
    nc.create_netCDF()
    #  TODO: Create netCDF

'''
{'id': 63, 
'timestamp': 1702893180.045758, '
'datetime': '2023-12-18T09:53:00.045758', 
'parsivel_id': 'PAR008', 
'telegram': 'VERSION:2.11.6; BUILD:2112151; 01:0000.000; 02:0000.00; 03:00; 04:00; 05:NP; 06:C; 07:-9.999; 08:20000; 09:00059; 10:11423; 11:00000; 12:008; 13:450994; 14:2.11.6; 15:2.11.1; 16:2.00; 17:24.2; 18:0; 19:None; 20:09; 21:18.12.2023; 22:GV; 23:None; 24:0000.00; 25:000; 26:021; 27:010; 28:010; 29:000.014; 30:00.000; 31:0000.0; 32:0000.00; 34:0000.00; 35:0000.00; 40:20000; 41:20000; 50:00000000; 51:000140; 90:-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999; 91:00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000; 93:000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000; 94:0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000; 95:0.00,0.00,0.00,0.00,0.00,0.00,0.00; 96:0000000,0000000,0000000,0000000,0000000,0000000,0000000'}
'''