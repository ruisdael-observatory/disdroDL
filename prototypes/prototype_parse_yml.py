from pathlib import Path
from pprint import pprint
from  util_functions import yaml2dict

wd = Path(__file__).parent 
config_dict = yaml2dict(path = wd / 'config.yml')
pprint(config_dict)

pprint(config_dict['telegram_fields']['01'])