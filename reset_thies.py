"""
Quick version of the reset function for the Thies Clima sensor.
Adapted reset_parsivel.py to work with the thies.
Maybe we can merge the two scripts into one in the future.
"""
from pathlib import Path
from argparse import ArgumentParser
from pydantic.v1.utils import deep_update
from modules.util_functions import create_logger, yaml2dict  # pylint: disable=import-error
from modules.sensors import Thies

parser = ArgumentParser(description="Ruisdael: OTT Disdrometer reset. Run: python reset_thies.py -c config_*.yml")
parser.add_argument('-c', '--config', required=True, help='Observation site config file. ie. -c config_008_GV_THIES.yml')
args = parser.parse_args()

wd = Path(__file__).parent
config_dict = yaml2dict(path=wd / 'configs_netcdf' / 'config_general_thies.yml')
config_dict_site = yaml2dict(path=wd / args.config)  # TODO: come from cli # pylint: disable=fixme
config_dict = deep_update(config_dict, config_dict_site)

logger = create_logger(log_dir=Path(config_dict['log_dir']),
                       script_name=config_dict['script_name'],
                       sensor_name=config_dict['global_attrs']['sensor_name'])

thies = Thies()
thies.init_serial_connection(port=config_dict['port'], baud=config_dict['baud'], logger=logger)
thies.reset_sensor(logger=logger, factory_reset=False)
thies.close_serial_connection()
