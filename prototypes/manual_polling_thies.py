from time import sleep
from modules.now_time import NowTime
import serial

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