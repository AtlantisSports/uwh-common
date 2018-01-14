from uwh.comms import XBeeServer, XBeeClient
s = XBeeServer()
for (remote, ping) in s.ping_clients(100):
    print("[%s, %s] ping: %d" % (remote.get_node_id(),
                                 remote.get_64bit_addr(), ping))
