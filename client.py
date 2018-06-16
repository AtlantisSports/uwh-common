from uwh.xbee_comms import XBeeServer, XBeeClient
from uwh.gamemanager import GameManager

mgr = GameManager()
c = XBeeClient(mgr, '/dev/tty.usbserial-DN03ZX6M', 9600)
c.listen_thread()
