"""
Script to export the DB data from a specific date to a netCDF file based on the given site config file.
"""

from argparse import ArgumentParser
from datetime import datetime, date, timedelta, timezone
from pathlib import Path
from pydantic.v1.utils import deep_update
from modules.util_functions import yaml2dict, get_general_config, create_dir, create_logger
from modules.telegram import ParsivelTelegram, ThiesTelegram
from modules.netCDF import NetCDF
from modules.sqldb import query_db_rows_gen, connect_db


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
    parser.add_argument(
        '-v',
        '--version',
        default='full',
        help="Bool for what version netCDF to export, a full or light version. Format: 'full' or 'light'")

    args = parser.parse_args()
    date_dt = datetime.strptime(args.date, '%Y-%m-%d')
    wd = Path(__file__).parent

    if args.version == 'full':
        full_version = True
    elif args.version == 'light':
        full_version = False
    else:
        raise Exception("version was not 'full' or 'light'")

    config_dict_site = yaml2dict(path=wd / args.config)
    sensor_type = config_dict_site['global_attrs']['sensor_type']

    # Use the general config file which corresponds to the sensor type
    config_dict = get_general_config(wd, sensor_type)

    # Combine the site specific config file and the sensor type specific config file into one
    config_dict = deep_update(config_dict, config_dict_site)

    # Combine the site name, station code and sensor name into the start of the file name
    site_name = config_dict['global_attrs']['site_name']
    st_code = config_dict['station_code']
    sensor_name = config_dict['global_attrs']['sensor_name']
    fn_start = f"{args.date.replace('-', '')}_{site_name}-{st_code}_{sensor_name}"

    # Use the database with data from the Thies in sample_data if the provided site config file is from the Thies
    if sensor_type == 'Thies Clima':
        db_path = Path("sample_data/disdrodl-thies.db")
    else:
        db_path = Path(config_dict['data_dir']) / 'disdrodl.db'

    # Add "_light" to the end of the file name when exporting a light version
    if full_version is False:
        fn_start = f"{fn_start}_light"

    logger = create_logger(log_dir=Path(config_dict['log_dir']),
                           script_name='disdro_db2nc',
                           sensor_name=config_dict['global_attrs']['sensor_name'])

    msg_conf = f"Starting {__file__} for {config_dict['global_attrs']['sensor_name']}"
    logger.info(msg=msg_conf)
    msg_date = f'Exporting data from {date_dt} to {date_dt.replace(hour=23, minute=59, second=59)}'
    logger.info(msg=msg_date)

    # Query the relevant data rows and create Telegram instances out of those
    telegram_objs = []
    cur, con = connect_db(dbpath=str(db_path))
    for row in query_db_rows_gen(con, date_dt=date_dt, logger=logger):
        ts_dt = datetime.fromtimestamp(row.get('timestamp'), tz=timezone.utc)

        #TODO needs to be removed once the data is written to database as " key:value" # pylint: disable=fixme
        if sensor_type == 'Thies Clima':
            telegram_list = row.get('telegram').split(';')
            telegram_list.insert(0,'')
            list_len = len(telegram_list)
            formatted_telegrams = []
            for index, value in enumerate(telegram_list[:-1]):
                if index == 80:
                    formatted_telegrams.append(f" {81}:{value},")
                elif 81 <= index <= 518:
                    formatted_telegrams.append(f"{value},")
                elif index == 519:
                    formatted_telegrams.append(f"{value};")
                elif index == list_len-1:
                    formatted_telegrams.append(f" {index + 1}:{value}")
                else:
                    formatted_telegrams.append(f" {index + 1}:{value};")
            telegram_str = ''.join(formatted_telegrams)

            telegram_instance = ThiesTelegram(
                config_dict=config_dict,
                telegram_lines=telegram_str,
                db_row_id=row.get('id'),
                timestamp=ts_dt,
                db_cursor=None,
                telegram_data={},
                logger=logger)
        else:
            telegram_instance = ParsivelTelegram(
                config_dict=config_dict,
                telegram_lines=row.get('telegram'),
                db_row_id=row.get('id'),
                timestamp=ts_dt,
                db_cursor=None,
                telegram_data={},
                logger=logger)

        telegram_instance.parse_telegram_row()

        # Append telegram_instance if it has data organized by keys(fields)
        if (("11" in telegram_instance.telegram_data.keys() and sensor_type == 'Thies Clima') or
            ("90" in telegram_instance.telegram_data.keys() and sensor_type == 'OTT Hydromet Parsivel2')):
            telegram_objs.append(telegram_instance)

    con.close()
    cur.close()

    # Directory to put the netCDF file in
    # Put the netCDF in sample_data if the provided site config file is from the Thies
    if sensor_type == 'Thies Clima':
        data_dir = Path('sample_data/')
    else:
        data_dir = Path(config_dict['data_dir']) / date_dt.strftime('%Y%m')

    # Create data directory if it does not exist yet
    created_data_dir = create_dir(path=data_dir)
    if created_data_dir:
        logger.info(msg=f'Created data directory: {data_dir}')

    # Create the netCDF object
    nc = NetCDF(logger=logger,
                config_dict=config_dict,
                data_dir=data_dir,
                fn_start=fn_start,
                full_version=full_version,
                telegram_objs=telegram_objs,
                date=date_dt)

    nc.create_netCDF()

    if sensor_type == 'Thies Clima':
        nc.write_data_to_netCDF_thies()
    else:
        nc.write_data_to_netCDF_parsivel()

    nc.compress()
