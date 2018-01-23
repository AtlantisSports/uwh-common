from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice
from digi.xbee.exception import TimeoutException
from digi.xbee.models.address import XBee64BitAddress

from . import messages_pb2
from .comms import UWHProtoHandler

import logging
from functools import partial
import threading
import time

class XBeeClient(UWHProtoHandler):
    def __init__(self, mgr, serial_port, baud):
        UWHProtoHandler.__init__(self, mgr)
        self._xbee = XBeeDevice(serial_port, baud)
        self._xbee.open()

    def send_raw(self, recipient, data):
        self._xbee.send_data_async(recipient, data)

    def listen_loop(self):
        while True:
            xbee_msg = self._xbee.read_data()
            if xbee_msg:
                try:
                    self.recv_raw(xbee_msg.remote_device, xbee_msg.data)
                except ValueError:
                    logging.exception("Problem parsing xbee packet")
                time.sleep(0.1)

    def listen_thread(self):
        thread = threading.Thread(target=self.listen_loop, args=())
        thread.daemon = True
        thread.start()

class XBeeServer(UWHProtoHandler):
    def __init__(self, mgr, serial_port, baud):
        UWHProtoHandler.__init__(self, mgr)
        self._xbee = XBeeDevice(serial_port, baud)
        self._xbee.open()

    def client_discovery(self, cb_found_client):
        xnet = self._xbee.get_network()
        xnet.clear()

        xnet.set_discovery_timeout(5) # seconds

        xnet.add_device_discovered_callback(cb_found_client)

        xnet.start_discovery_process()

        while xnet.is_discovery_running():
            time.sleep(0.1)

    def recipient_from_address(self, address):
        return RemoteXBeeDevice(self._xbee,
                                XBee64BitAddress.from_hex_string(address))

    def send_raw(self, recipient, data):
        self._xbee.send_data_async(recipient, data)

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

    def multicast_GameKeyFrame(self, client_addrs):
        for addr in client_addrs:
            client = self.recipient_from_address(addr)
            self.send_GameKeyFrame(client)

    def broadcast_loop(self, client_addrs):
        while True:
            self.multicast_GameKeyFrame(client_addrs)
            time.sleep(0.1)

    def broadcast_thread(self, client_addrs):
        thread = threading.Thread(target=self.broadcast_loop,
                                  args=(client_addrs))
        thread.daemon = True
        thread.start()
