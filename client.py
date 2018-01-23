from uwh.xbee_comms import XBeeServer, XBeeClient
from uwh.gamemanager import GameManager

mgr = GameManager()
c = XBeeClient(mgr, '/dev/tty.usbserial-DN040E8Y', 9600)
c.listen_loop()
