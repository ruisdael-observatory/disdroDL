import serial

com_port2 = '/dev/ttyACM0'
baud_rate2 = 9600
listener = serial.Serial(port=com_port2, baudrate=baud_rate2)
print(listener)
while True:
    serial_out = listener.readlines()
    print(serial_out)


