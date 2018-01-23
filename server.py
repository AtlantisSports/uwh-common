from uwh.xbee_comms import XBeeServer, XBeeClient
from uwh.gamemanager import GameManager

mgr = GameManager()
s = XBeeServer(mgr, '/dev/tty.usbserial-DN03ZRU8', 9600)
for (remote, ping) in s.ping_clients(100):
    print("[%s, %s] ping: %d" % (remote.get_node_id(),
                                 remote.get_64bit_addr(), ping))
