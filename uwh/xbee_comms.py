from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice
from digi.xbee.exception import TimeoutException
from digi.xbee.models.address import XBee64BitAddress

from . import messages_pb2
from .comms import UWHProtoHandler

from configparser import ConfigParser
import json
import logging
import threading
import time

def XBeeConfigParser():
    defaults = {
        'port': '/dev/tty.usbserial-DN03ZRU8',
        'baud': '9600',
        'clients': '[]',
    }
    parser = ConfigParser(defaults=defaults)
    parser.add_section('xbee')
    return parser

def xbee_port(cfg):
    return cfg.get('xbee', 'port')

def xbee_baud(cfg):
    return cfg.getint('xbee', 'baud')

def xbee_clients(cfg):
    return json.loads(cfg.get('xbee', 'clients'))


class XBeeClient(UWHProtoHandler):
    def __init__(self, mgr, serial_port, baud):
        UWHProtoHandler.__init__(self, mgr)
        self._xbee = XBeeDevice(serial_port, baud)
        self._xbee.open()

    def send_raw(self, recipient, data):
        try:
            self._xbee.send_data(recipient, data)
        except TimeoutException:
            pass

    def listen_thread(self):
        def callback(xbee_msg):
            try:
                self.recv_raw(xbee_msg.remote_device, xbee_msg.data)
                #self._xbee.flush_queues()
            except ValueError:
                logging.exception("Problem parsing xbee packet")

        self._xbee.add_data_received_callback(callback)

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
            time.sleep(0.5)

    def recipient_from_address(self, address):
        return RemoteXBeeDevice(self._xbee,
                                XBee64BitAddress.from_hex_string(address))

    def send_raw(self, recipient, data):
        try:
            self._xbee.send_data(recipient, data)
        except TimeoutException:
            pass

    def time_ping(self, remote, val):
        ping_kind = messages_pb2.MessageType_Ping
        ping = self.message_for_msg_kind(ping_kind)
        ping.Data = val
        start = time.time()
        self.send_message(remote, ping_kind, ping)

        try:
            xbee_msg = self._xbee.read_data_from(remote, 2)
            end = time.time()
            data = self.expect_Pong(xbee_msg.remote_device, xbee_msg.data)
            if data != val:
                # Data mismatch
                return None
            return end - start
        except TimeoutException:
            return None

    def find_clients(self):
        clients = []
        def found_client(remote):
            clients.append(remote)

        self.client_discovery(found_client)
        return clients

    def multicast_GameKeyFrame(self, client_addrs):
        (kind, msg) = self.get_GameKeyFrame()
        for addr in client_addrs:
            client = self.recipient_from_address(addr)
            self.send_message(client, kind, msg)

    def multicast_Penalties(self, client_addrs):
        (kind, msgs) = self.get_Penalties()
        for addr in client_addrs:
            client = self.recipient_from_address(addr)
            for msg in msgs:
                self.send_message(client, kind, msg)

    def multicast_Goals(self, client_addrs):
        (kind, msgs) = self.get_Goals()
        for addr in client_addrs:
            client = self.recipient_from_address(addr)
            for msg in msgs:
                self.send_message(client, kind, msg)

    def multicast_GameTime(self, client_addrs):
        (kind, msg) = self.get_GameTime()
        for addr in client_addrs:
            client = self.recipient_from_address(addr)
            self.send_message(client, kind, msg)

    def broadcast_loop(self, client_addrs):
        while True:
            for i in range(0, 10):
                self.multicast_GameTime(client_addrs)
                time.sleep(0.1)
            self.multicast_GameKeyFrame(client_addrs)
            self.multicast_Penalties(client_addrs)
            self.multicast_Goals(client_addrs)
            time.sleep(0.1)

    def broadcast_thread(self, client_addrs):
        thread = threading.Thread(target=self.broadcast_loop,
                                  args=(client_addrs,))
        thread.daemon = True
        thread.start()
