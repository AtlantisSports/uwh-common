from uwh.rs485_comms import RS485Server, RS485Client
from uwh.gamemanager import GameManager
import time

mgr = GameManager()
c = RS485Client(mgr, '/dev/tty.usbserial-DN2N4O2G', 115200)

c.listen_thread()

while True:
    print(mgr.blackScore())
    time.sleep(0.1)
