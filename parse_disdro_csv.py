""""comment"""
import csv
from pathlib import Path
from typing import Dict
from datetime import datetime, timezone
from argparse import ArgumentParser
from pydantic.v1.utils import deep_update
from modules.telegram import ParsivelTelegram, ThiesTelegram
#from pprint import pprint
from modules.util_functions import yaml2dict, create_logger

def str2list_by_ndigits(input: str, ndigits: int) -> list[str]:  # pylint: disable=W0622
    '''
    converts str (sequence of characters) into a list,
    with each item being ndigits long.
    Used only for F93 values, when they are in  '00000000000' (Ruisdael CSVs)
    '''
    range_obj = range(0, len(input), ndigits)
    list_val = [input[i:i + ndigits] for i in range_obj]
    return list_val


def telegram_list2dict(telegram_indeces: list, telegram: list) -> Dict:
    '''
    Converts the parsivel telegram list to a dictionary.
    The dictionary keys are the iter numbers of the telegram string
    The telegram list input: ['0000.102', '0100.87', '57', '58', '-RADZ', ' RL-'
    Telegram has the following sequence: 01,02,03...35,60,90,91,93
    '''
    telegram_dict = {key: None for key in telegram_indeces} # pylint: disable=W0621
    # print(telegram[:-3])
    for index, field_n in enumerate(telegram_indeces[:-3]):  # ignore fields 90,91,93
        telegram_dict[field_n] = telegram[index]
    telegram_dict['90'] = (",").join(telegram[-65:-33])
    telegram_dict['91'] = (",").join(telegram[-33:-1])
    telegram_dict['93'] = telegram[-1]
    return telegram_dict


def telegram2dict(telegram: str, dt: datetime, ts: float, ):
    '''
    Creates 1 dict from a dataframe row, with the telegram values
    '''
    telegram_str = '%01;%02;%03;%04;%05;%06;%07;%08;%09;%10;%11;%12;%13;%14;%15;%16;%17;%18;' \
                   '%19;%20;%21;%22;%23;%24;%25;%26;%27;%28;%30;%31;%32;%33;%34;%35;%60;%90;%91;%93' # pylint: disable=W0621
    telegram_indeces = telegram_str.replace('%', '').split(';')  # 38 fields
    # why am I using telegram_str to create telegram_indeces?
    # Couldnt I use, the following?
    # default_telegram_indeces = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12',
    # '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '30',
    # '31', '32', '33', '34', '35', '60', '90', '91', '93']
    telegram_dict = telegram_list2dict(telegram_indeces=telegram_indeces,  # pylint: disable=W0621
                                       telegram=telegram.split(';'))
    telegram_dict['datetime'] = dt
    telegram_dict['timestamp'] = ts
    return telegram_dict

def thies_telegram_to_dict(telegram: str, dt: datetime, ts: float, ):
    '''
    Creates 1 dict from a dataframe row, with the telegram values
    '''
    telegram_indices = [str(i) for i in range(1, 528)]
    telegram_list = telegram.split(';')
    telegram_dict = {key: None for key in telegram_indices}  # pylint: disable=W0621
    for index, field_n in enumerate(telegram_indices):
        telegram_dict[field_n] = telegram_list[index]
    telegram_dict['datetime'] = dt
    telegram_dict['timestamp'] = ts
    return telegram_dict


if __name__ == '__main__':
    ## Parser
    parser = ArgumentParser(
        description="Parser for historical Ruisdael's OTT Parsivel CSVs. Converts CSV to netCDF. \
            Run: python parse_disdro_csv.py -c configs_netcdf/config_007_CABAUW.yml\
                -i sample_data/20231106_PAR007_CabauwTower.csv \
            Output netCDF: store in same directory as input file"
        )
    parser.add_argument(
        '-c',
        '--config',
        required=True,
        help='Path to site config file. ie. -c configs_netcdf/config_007_CABAUW.yml')
    parser.add_argument(
        '-i',
        '--input',
        required=True,
        help='Path to input CSV file. ie. -i sample_data/20231106_PAR007_CabauwTower.csv')
    args = parser.parse_args()
    input_path = Path(args.input)

    ## Config
    wd = Path(__file__).parent
    config_dict = yaml2dict(path=wd / 'configs_netcdf' / 'config_general_parsivel.yml')
    config_dict_site = yaml2dict(path=wd / args.config)
    config_dict = deep_update(config_dict, config_dict_site)
    conf_telegram_fields = config_dict['telegram_fields']  # multivalue fileds have > 1 dimension
    # print(conf_telegram_fields)
    ## Logger
    # import pdb; pdb.set_trace()
    logger = create_logger(log_dir=Path(config_dict['log_dir']),
                           script_name=Path(__file__).name,
                           parsivel_name=config_dict['global_attrs']['sensor_name'])
    # output file
    site_name = config_dict['global_attrs']['site_name']
    st_code = config_dict['station_code']
    sensor_name = config_dict['global_attrs']['sensor_name']
    output_fn = f"{input_path.stem}_{site_name}-{st_code}_{sensor_name}.nc"
    output_path = input_path.parent / output_fn
    with open(input_path , newline='') as csvfile:  # pylint: disable=W1514
        reader = csv.reader(csvfile, delimiter=';')
        telegram_objs = []
        for row in reader:
            dt_str, ts_str, telegram_b = row
            telegram_str = telegram_b[2:-1]  # use only string between "b "
            telegram_dict = telegram2dict(telegram=telegram_str,
                                          dt=datetime.strptime(dt_str, '%Y%m%d-%H%M%S'),
                                          ts=float(ts_str))
            ts_dt = datetime.fromtimestamp(float(ts_str), tz=timezone.utc)
            row_telegram = ParsivelTelegram(
                config_dict=config_dict,
                telegram_lines=None,
                timestamp=ts_dt,
                db_cursor=None,
                telegram_data=telegram_dict,
                logger=logger)
            # row_telegram.parse_telegram_row()  # no need to parse_telegram_row
            telegram_objs.append(row_telegram)
            telegram_data_ts = datetime.fromtimestamp(row_telegram.telegram_data['timestamp'], tz=timezone.utc)
            print('Compare:',
                  'ts_dt:', ts_dt,
                  'Telegram.timestamp:', row_telegram.timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
                  'telegram_data[datetime]:', row_telegram.telegram_data['datetime'].strftime('%Y-%m-%dT%H:%M:%S'),
                  'telegram_data[timestamp]:', telegram_data_ts.strftime('%Y-%m-%dT%H:%M:%S')
                  )
            # assert row_telegram.timestamp.strftime('%Y-%m-%dT%H:%M:%S') ==
            # row_telegram.telegram_data['datetime'].strftime('%Y-%m-%dT%H:%M:%S')
            # '''
            # Error: there is 1hour difference betweem row_telegram.timestamp and row_telegram.telegram_data
            # Compare: ts_dt 2023-11-06 22:58:51.979260+00:00 Telegram.timestamp: 2023-11-06T22:58:51
            # telegram_data[datetime]: 2023-11-06T23:58:51 telegram_data[timestamp]: 2023-11-06T22:58:51
            # while discussing it with Rob, Rob thinks that the Parsivel Pi and script might have been running on
            # local time and not UTC
            # '''


#     # CSV processing
#     df = csv2df(csv_path=str(input_path))
#     for index, csv_row in df.iterrows():
#         telegram_dict = telegram2dict(telegram=csv_row['telegram'],
#                                       dt=csv_row['datetime'],
#                                       ts=csv_row['timestamp'], )
#         telegram = ParsivelTelegram(config_dict=config_dict,
#                             telegram_lines=None,
#                             telegram_data=telegram_dict,
#                             timestamp=telegram_dict['datetime'],
#                             db_cursor=None,
#                             logger=logger
#                             )
#         telegram.str2list(field='90', separator=',')
#         telegram.str2list(field='91', separator=',')
#         telegram.telegram_data['93'] = str2list_by_ndigits(input=telegram.telegram_data['93'], ndigits=3)
#         telegram.write_data_to_netCDF()

# '''

# * field 93 error handling: what happens when x is present
# * time: unit - start see: `def test_nc_time`
