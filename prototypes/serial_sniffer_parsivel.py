import serial

baud_rate1 = 19200
com_port1 = '/dev/ttyUSB0'
listener = serial.Serial(port=com_port1, baudrate=baud_rate1)
print(listener)
while True:
    serial_out = listener.readline()
    print(serial_out)
