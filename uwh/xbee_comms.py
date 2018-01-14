from digi.xbee.devices import XBeeDevice
from digi.xbee.exception import TimeoutException

from . import messages_pb2
from .comms import UWHProtoHandler

import time

class XBeeClient(UWHProtoHandler):
    def __init__(self):
        UWHProtoHandler.__init__(self)
        self._xbee = XBeeDevice('/dev/tty.usbserial-DN040E8Y', 9600)
        self._xbee.open()

    def send_raw(self, recipient, data):
        self._xbee.send_data_async(recipient, data)

    def listen_loop(self):
        while True:
            xbee_msg = self._xbee.read_data()
            if xbee_msg:
                self.recv_raw(xbee_msg.remote_device, xbee_msg.data)
                time.sleep(0.1)

class XBeeServer(UWHProtoHandler):
    def __init__(self):
        UWHProtoHandler.__init__(self)
        self._xbee = XBeeDevice('/dev/tty.usbserial-DN03ZRU8', 9600)
        self._xbee.open()

    def client_discovery(self, cb_found_client):
        xnet = self._xbee.get_network()
        xnet.clear()

        xnet.set_discovery_timeout(5) # seconds

        xnet.add_device_discovered_callback(cb_found_client)

        xnet.start_discovery_process()

        while xnet.is_discovery_running():
            time.sleep(0.1)

    def send_raw(self, recipient, data):
        self._xbee.send_data_async(recipient, data)

    def unicast_send_raw(self, remote, data):
        self.send_raw(remote, data)

    def multicast_send_raw(self, remotes, data):
        for remote in remotes:
            self.send_raw(remote, data)

    def time_ping(self, remote, val):
        ping_kind = messages_pb2.MessageType_Ping
        ping = self.message_for_msg_kind(ping_kind)
        ping.Data = val
        self.send_message(remote, ping_kind, ping)

        try:
            self._xbee.read_data_from(remote, 5)
        except TimeoutException:
            return -1

    def ping_clients(self, repetitions):
        clients = []
        def found_client(remote):
            clients.append(remote)

        self.client_discovery(found_client)

        results = []
        for c in clients:
            start = time.time()
            for x in range(0, repetitions):
                self.time_ping(c, x)
            end = time.time()
            results.append((c, (end - start) / repetitions))

        return results
