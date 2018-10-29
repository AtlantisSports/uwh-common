from uwh.rs485_comms import RS485Server, RS485Client
from uwh.gamemanager import GameManager
import time

mgr = GameManager()
mgr.setTid(1)
mgr.setGid(1)
s = RS485Server(mgr, '/dev/tty.usbserial-DN2NFRGS', 115200)

s.broadcast_thread()

b = 0
while True:
    b = b + 1
    print(b)
    mgr.setBlackScore(b)
    time.sleep(0.1)
