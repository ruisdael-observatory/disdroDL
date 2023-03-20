from pathlib import Path
from modules.util_functions import create_logger, yaml2dict, init_serial, parsivel_reset


print(__file__)
wd = Path(__file__).parent 
config_dict = yaml2dict(path = wd / 'config.yml')
logger = create_logger(log_dir=Path(config_dict['log_dir']), 
                       script_name=config_dict['script_name'], 
                       parsivel_name=config_dict['sensor_name'])
parsivel = init_serial(port=config_dict['port'], baud=config_dict['baud'], logger=logger)  # initiate serial connection
parsivel_reset(serialconnection=parsivel, logger=logger, factoryreset=False)
parsivel.close()
