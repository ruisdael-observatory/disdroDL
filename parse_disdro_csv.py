""""
This script exports .csv's to netCDF files. It parses the data read from the csv here with custom functions, 
as the functions from the telegram object didn't work on the string of data from the csv.
It then makes a telegram object with the parsed data already inserted, before it gets passed on to a NetCDF object.
"""
import csv
import math
from pathlib import Path
from typing import Dict
from datetime import datetime, timezone
from argparse import ArgumentParser
from pydantic.v1.utils import deep_update
from modules.telegram import ParsivelTelegram, ThiesTelegram
#from pprint import pprint
from modules.util_functions import yaml2dict, create_logger
from modules.netCDF import NetCDF

#Different dictionaries to select the necessary method/file needed, corresponding to the respective sensor
telegrams = {'THIES': ThiesTelegram, 'PAR': ParsivelTelegram}
config_files = {'THIES': 'config_general_thies.yml', 'PAR': 'config_general_parsivel.yml'}
field_type = {'i4': int, 'i2': int, 'S4': str, 'f4': float}


def choose_sensor(input: str) -> str:
    sensors = telegrams.keys()
    return next((sensor for sensor in sensors if (sensor in input)), None)



def telegram2dict(telegram: list[str], dt: datetime, ts: datetime, config_dict: Dict):
    '''
    Creates 1 dict from a dataframe row, with the telegram values
    '''
    default_telegram_indeces = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12',
    '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '30',
    '31', '32', '33', '34', '35', '60', '90', '91', '93']
    telegram_dict = {}
    x = 0
    for i, key in enumerate(default_telegram_indeces):
        if(key == '90' or key == '91'):
            shallow_copy = []
            telegram_value = [float(value) for value in telegram[i+x*32:i+32*(x+1)]] #field_type[config_dict[key]['dtype']](telegram_list[i:i+32])
            x +=1
            shallow_copy[:] = telegram_value
            telegram_dict[key] = shallow_copy
        elif(key == '93'):
            s = telegram[-1]
            raw_data = [int(s[i:i+3]) for i in range(0, len(s), 3)]
            telegram_dict[key] = raw_data
        else:
            telegram_value = field_type[config_dict[key]['dtype']](telegram[i])
            telegram_dict[key] = telegram_value
    
    telegram_dict['datetime'] = dt
    telegram_dict['timestamp'] = str(ts)
    return telegram_dict

def thies_telegram_to_dict(telegram: list[str], dt: datetime, ts: datetime, config_dict: Dict) -> Dict:
    '''
    Creates 1 dict from a dataframe row, with the telegram values
    '''
    telegram_indices = list(config_dict.keys())[1:]
    telegram_dict = {}
    print(telegram_indices)
    #telegram = telegram[1:]
    for index, field_n in enumerate(telegram_indices):
        print(field_n, config_dict[field_n]['dtype'], telegram[index])
        if(field_n == '81'):
            telegram_dict[field_n] = [int(x) for x in telegram[index:index+439]]
            print(telegram_dict[field_n])
        elif(field_n > '520'):
            telegram_dict[field_n] = field_type[config_dict[field_n]['dtype']](telegram[index+439])
        else:
            telegram_dict[field_n] = field_type[config_dict[field_n]['dtype']](telegram[index])
    telegram_dict['2'] = telegram_dict['2'].split(',')[-1]
    telegram_dict['datetime'] = dt
    
    telegram_dict['timestamp'] = str(ts)
    return telegram_dict

def process_row(telegram: list, sensor: str, config_dict: dict):

    if len(telegram) == 3:
        
        dt_str, ts_str, telegram_b = telegram
        timestamp = datetime.strptime(dt_str, "%Y%m%d-%H%M%S")
        date = datetime.fromtimestamp(float(ts_str), tz=timezone.utc)
        if sensor == 'PAR':
            telegram = telegram_b[2:-1].split(";")
            return telegram2dict(telegram, timestamp, date, config_dict), timestamp
        else: 
            telegram = telegram_b[4:-1].split(";")
            return thies_telegram_to_dict(telegram, date, timestamp, config_dict), timestamp
    else:
        if sensor == "THIES":
            dates = telegram[0].split(",")
            timestamp = datetime.strptime(dates[0], "%Y%m%d-%H%M%S")
            date = datetime.fromtimestamp(float(telegram[1]), tz=timezone.utc)
            return thies_telegram_to_dict(telegram, date, timestamp, config_dict), timestamp
        else:
            date = telegram[0]
            timestamp = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")
            return telegram2dict(telegram[1:], timestamp, timestamp, config_dict), timestamp

            

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

    sensor = choose_sensor(args.input)
    if sensor is None:
        raise ValueError("Sensor not recognized. Please check the input file name.")

    date_str = args.input.split("_")[:-2]
    print(date_str)
    date = datetime(2021, 12, 19)
    ## Config
    wd = Path(__file__).parent
    config_dict = yaml2dict(path=wd / 'configs_netcdf' / config_files[sensor])
    config_dict_site = yaml2dict(path=wd / args.config)
    config_dict = deep_update(config_dict, config_dict_site)
    conf_telegram_fields = config_dict['telegram_fields']  # multivalue fileds have > 1 dimension
    ## Logger
    # import pdb; pdb.set_trace()
    logger = create_logger(log_dir=Path(config_dict['log_dir']),
                           script_name=Path(__file__).name,
                           sensor_name=config_dict['global_attrs']['sensor_name'])
    # output file
    site_name = config_dict['global_attrs']['site_name']
    st_code = config_dict['station_code']
    sensor_name = config_dict['global_attrs']['sensor_name']
    output_fn = f"{input_path.stem}"
    output_path = input_path.parent / output_fn
    
    with open(input_path , newline='') as csvfile:  # pylint: disable=W1514
        reader = csv.reader(csvfile, delimiter=';')
        telegram_objs = []
        for row in reader:
            if(row[0] == 'Timestamp (UTC)'):
                continue
            telegram, timestamp = process_row(row, sensor, conf_telegram_fields)
            telegram_instance = telegrams[sensor](
                config_dict=config_dict,
                telegram_lines="",
                timestamp=timestamp,
                db_cursor=None,
                logger=logger,
                telegram_data=telegram,
            )

            telegram_objs.append(telegram_instance)

    nc = NetCDF(logger=logger,
                config_dict=config_dict,
                data_dir='sample_data/',
                fn_start=output_fn,
                full_version=True,
                telegram_objs=telegram_objs,
                date=date)
    
    nc.create_netCDF()
    nc.write_data_to_netCDF_parsivel() if sensor == 'PAR' else nc.write_data_to_netCDF_thies() 
    nc.compress()
