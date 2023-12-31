import json
from pathlib import Path
from  modules.util_functions import yaml2dict, create_logger
from pydantic.v1.utils import deep_update

wd = Path(__file__).parent 
config_dict = yaml2dict(path = wd / 'configs_netcdf' / 'config_general.yml')
config_dict_site = yaml2dict(path = wd / 'configs_netcdf' / 'config_007_CABAUW.yml')
config_dict = deep_update(config_dict, config_dict_site)

telegram_lines=[b'OK\r\n', 
                b'\n', 
                b'SVFS:0000.000;0000.00;00;00;   NP;   C;-9.999;20000;00059;12773;00000;012;450994;2.11.6;2.11.1;0.50;24.3;0;14:09:59;16.02.2023;;;0000.00;000;025;013;013;00.000;0000.0;0000.00;-9.99;0000.00;0000.00;00000007;\n', 
                b'F90:-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;\n', 
                b'F91:00.000;00.000;00.000;00.000;00.000;\n', 
                b'F93:000;000;000;000;000;000;\n', 
                b'F61:00.502;00.853\r\n', 
                b'00.606;02.026\r\n', 
                b'00.550;01.595\r\n', 
                b'00.521;01.237\r\n', 
                b'00.540;01.070\r\n', 
                b'00.559;01.710\r\n', 
                b'00.571;01.572\r\n', 
                b';']


def test_logger():
    logger = create_logger(
        log_dir=Path(config_dict['log_dir']),
        script_name=Path(__file__).name,
        parsivel_name=config_dict['global_attrs']['sensor_name']
    )
    logger.info(msg=f"Testing logger in {__file__}")
    assert logger.name == f"{Path(__file__).name}: {config_dict['global_attrs']['sensor_name']}"
    log_file = Path(config_dict['log_dir']) / f'log_{Path(__file__).name}.json'
    with open(log_file, 'r') as log_file_r:
        last_log_line = log_file_r.readlines()[-1]
        last_log_line = (json.loads(last_log_line))
        assert last_log_line['name'] == f"{Path(__file__).name}: {config_dict['global_attrs']['sensor_name']}"
        assert last_log_line['msg'] == f"Testing logger in {__file__}"


def test_config_dict():
    for key in ['dimensions', 'variables', 'telegram_fields', 'station_code', 'port', 'baud', 'script_name', 'data_dir', 'log_dir', 'global_attrs', 'variables']:   
        assert key in config_dict.keys()
    for variable_key in ['time', 'interval', 'timestamp', 'latitude', 'longitude', 'altitude']:
        assert variable_key in config_dict['variables'].keys()
    

#  'velocity_classes_center', 'velocity_upper_bounds', 'velocity_lower_bounds', 'velocity_spread',