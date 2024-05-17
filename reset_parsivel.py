"""
TBC
"""
from pathlib import Path
from argparse import ArgumentParser
from pydantic.v1.utils import deep_update
from modules.util_functions import create_logger, yaml2dict  # pylint: disable=import-error
from modules.sensors import Parsivel

parser = ArgumentParser(description="Ruisdael: OTT Disdrometer reset. Run: python reset_parsivel.py -c config_*.yml")
parser.add_argument('-c', '--config', required=True, help='Observation site config file. ie. -c config_008_GV.yml')
args = parser.parse_args()

wd = Path(__file__).parent
config_dict = yaml2dict(path=wd / 'configs_netcdf' / 'config_general_parsivel.yml')
config_dict_site = yaml2dict(path=wd / args.config)  # TODO: come from cli
config_dict = deep_update(config_dict, config_dict_site)

logger = create_logger(log_dir=Path(config_dict['log_dir']),
                       script_name=config_dict['script_name'],
                       parsivel_name=config_dict['global_attrs']['sensor_name'])

parsivel = Parsivel()
parsivel.init_serial_connection(port=config_dict['port'], baud=config_dict['baud'], logger=logger)
parsivel.reset_sensor(logger=logger, factory_reset=False)
parsivel.serial_connection.close()
