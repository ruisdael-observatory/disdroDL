import pandas as pd
from argparse import ArgumentParser
from datetime import datetime, date, timedelta
from pathlib import Path
from pydantic.v1.utils import deep_update
from modules.util_functions import yaml2dict, create_dir, create_logger
from modules.sqldb import create_db, connect_db


date_today = date.today()
date_yest = date_today - timedelta(days=1)


if __name__ == '__main__':
    parser = ArgumentParser(
        description="Export 1 day of parsivel data from DB to NetCDF.\
            Run: python export_daily_netcdf.py -c configs_netcdf/config_007_CABAUW.yml\
                -d 2023-12-17 \
            Output netCDF: store in same directory as input file"
        )
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

    wd = Path(__file__).parent
    config_dict = yaml2dict(path=wd / 'configs_netcdf' / 'config_general.yml')
    config_dict_site = yaml2dict(path=wd / args.config)
    config_dict = deep_update(config_dict, config_dict_site)
    db_path = Path(config_dict['data_dir']) / 'disdrodl.db'

    logger = create_logger(log_dir=Path(config_dict['log_dir']),
                        script_name=config_dict['script_name'],
                        parsivel_name=config_dict['global_attrs']['sensor_name'])
    logger.info(msg=f"Starting {__file__} for {config_dict['global_attrs']['sensor_name']}")

    con, cur = connect_db(dbpath=str(db_path))
    start_dt = datetime.strptime(args.date, '%Y-%m-%d').replace(hour=0, minute=0, second=10)
    start_ts = start_dt.timestamp()
    end_dt = datetime.strptime(args.date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    end_ts = end_dt.timestamp()
    sql_query = f"SELECT * FROM disdrodl WHERE timestamp >= {start_ts} AND timestamp < {end_ts}"
    logger.debug(sql_query)
    df_disdro_data = pd.read_sql_query(sql_query, con)
    #  TODO: parse telegram col
    #  TODO: Create netCDF
    print(df_disdro_data)
    cur.close()
    con.close()