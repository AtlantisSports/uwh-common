from uwh.comms import XBeeServer, XBeeClient

c = XBeeClient()
c.listen_loop()
