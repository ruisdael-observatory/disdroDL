"""
This module contains a class for getting the current time.

Functions:
- date_strings: Sets the string fields of the class to the respective string representations of the current time.
"""

from datetime import datetime, timezone

class NowTime:
    '''
    Class dedicated to represent current date and time in different formats
    Attributes:
        utc : datetime object representing class instance time of instantiation
        time_list : list of hour,minutes,seconds of time of instantiation time
    '''

    def __init__(self):
        self.utc = datetime.now(timezone.utc)
        self.time_list = (self.utc.strftime("%H:%M:%S")).split(":")  # used to be: now_hour_min_secs
        # now_hour_min_secs = now_hour_min_secs.split(":")
        self.__date_strings()
        self.last_minute_of_day = self.utc.replace(hour=23, minute=59, second=0, microsecond=0)

    def __date_strings(self):
        '''
        def Converts instantiation time to different format class attributes
            iso: instantiation time in ISO 8601 format string
            ym: instantiation time YearMonth (YYYYmm) format string
            ymd: instantiation time YearMonthDay (YYYYmmdd) format string
        '''
        self.iso = self.utc.isoformat()
        self.ym = self.utc.strftime("%Y%m")
        self.ymd = self.utc.strftime("%Y%m%d")
