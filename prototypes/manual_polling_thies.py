from time import sleep
import serial
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

thies_port = '/dev/ttyACM0'
thies_baud = 9600
thies_id = '06'
thies = serial.Serial(port=thies_port, baudrate=thies_baud)
thies.reset_input_buffer()
print(thies)

thies.write(('\r' + thies_id + 'KY1\r').encode('utf-8')) # place in config mode
sleep(1)

thies.write(('\r' + thies_id + 'TM0\r').encode('utf-8')) # turn of automatic mode
sleep(1)

thies.write(('\r' + thies_id + 'KY0\r').encode('utf-8')) # place out of config mode
sleep(1)

while True:
    now_time = NowTime()

    if int(now_time.time_list[2]) != 0:
        sleep(1)
        continue

    thies.write(('\r' + thies_id + 'TR5\r').encode('utf-8'))
    output = thies.readline()
    decoded_bytes = str(output[0:len(output)-2].decode("utf-8"))
    print(decoded_bytes)
    sleep(2)
