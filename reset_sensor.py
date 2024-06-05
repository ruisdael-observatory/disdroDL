"""
Script to reset the serial connection for a given sensor.
"""
import sys
from argparse import ArgumentParser
from pathlib import Path

from modules.sensors import Parsivel, Thies
from modules.util_functions import yaml2dict, create_logger


def get_config_file():
    """
    Function that gets the correct config file
    :return: the config file's name
    """
    parser = ArgumentParser(
        description="Ruisdael: OTT Disdrometer reset. Run: python reset_sensor.py -c config_*.yml")
    parser.add_argument('-c', '--config', required=True, help='Observation site config file. ie. -c config_008_GV.yml')
    args = parser.parse_args()
    return args.config


def main(config_file):
    """
    config file's name
    :param config_file:
    """
    wd = Path(__file__).parent
    config_dict = yaml2dict(path=wd / 'configs_netcdf' / config_file)
    logger = create_logger(log_dir=Path(config_dict['log_dir']),
                           script_name=config_dict['script_name'],
                           sensor_name=config_dict['global_attrs']['sensor_name'])

    sensor_type = config_dict['global_attrs']['sensor_type']
    sensor = None
    if sensor_type == 'OTT Hydromet Parsivel2':
        sensor = Parsivel()
    elif sensor_type == 'Thies Clima':
        sensor = Thies()
    else:
        logger.error(msg=f"Sensor type {sensor_type} not recognized")
        sys.exit(1)

    sensor.init_serial_connection(port=config_dict['port'], baud=config_dict['baud'], logger=logger)
    sensor.reset_sensor(logger=logger, factory_reset=False)
    sensor.close_serial_connection()


if __name__ == '__main__':
    main(get_config_file())
