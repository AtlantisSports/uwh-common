import serial
import sys
from time import sleep


if len(sys.argv) != 2:
    print("Please provide the tty device as the only argument!")
    exit()

device = sys.argv[1]

# Setup the serial device, defaults to 8N0. second argument is baud rate.
# See https://pyserial.readthedocs.io/en/latest/pyserial_api.html for
# description of timeout modes
ser = serial.Serial(device, 115200, timeout=0)

ser.write(b'y')
print("Sent: y")

while True:
    recv = ser.read()
    if len(recv) != 0:
        print("Recieved: {}".format(recv))
        break
    sleep(0.1)

ser.close()
