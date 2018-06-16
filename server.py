from uwh.xbee_comms import XBeeServer, XBeeClient
from uwh.gamemanager import GameManager
import matplotlib.pyplot as plt

mgr = GameManager()
s = XBeeServer(mgr, '/dev/tty.usbserial-AH03B45X', 9600)

print("Node discovery...")
clients = s.find_clients()
for client in clients:
    print("Found {}".format(client.get_64bit_addr()))

reps = 60 * 60
for c in clients:
    attempts = []
    durations = []
    plt.axis([0, reps, 0, 2])
    plt.title("Ping for '{}'".format(c.get_64bit_addr()))
    plt.xlabel("attempt #")
    plt.ylabel("latency (s)")
    for x in range(0, reps):
        duration = s.time_ping(c, x)
        plt.scatter(x, duration or 0, marker = '.' if duration else 'x', c=0.01)
        plt.pause(1);
    plt.show()
