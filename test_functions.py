
from pathlib import Path
from  modules.util_functions import yaml2dict

def foo():
    assert 'foo' != 'bar'

def test_yaml():
    wd = Path(__file__).parent 
    config_dict = yaml2dict(path = wd / 'config.yml')
    print(config_dict)
    assert len(config_dict.keys()) > 1