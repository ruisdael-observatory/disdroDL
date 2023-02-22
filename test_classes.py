from datetime import datetime
from modules.classes import NowTime


def test_NowTime():
    now = NowTime()
    test_time_list = datetime.utcnow().strftime("%H:%M:%S").split(":") 
    assert type(now.time_list) == list
    assert now.time_list[0] == test_time_list[0] and now.time_list[1] == test_time_list[1] and now.time_list[2] == test_time_list[2]
    # assert: the following attributes are only created after method: date_strings()
    assert 'iso' not in now.__dict__.keys() and 'ym' not in now.__dict__.keys() and 'ymd' not in now.__dict__.keys() 
    now.date_strings()
    assert 'iso' in now.__dict__.keys() and 'ym' in now.__dict__.keys() and 'ymd' in now.__dict__.keys() 
    assert type(now.iso) == str and type(now.ym) == str and type(now.ymd) == str  
