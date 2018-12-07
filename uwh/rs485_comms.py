from . import messages_pb2
from .comms import UWHProtoHandler

from configparser import ConfigParser
import json
import logging
import threading
import time
import binascii
import serial
from time import sleep

def RS485ConfigParser():
    defaults = {
        'port': '/dev/tty.usbserial-',
        'baud': '11500',
        'clients': '[]',
    }
    parser = ConfigParser(defaults=defaults)
    parser.add_section('rs485')
    return parser

def port(cfg):
    return cfg.get('rs485', 'port')

def baud(cfg):
    return cfg.get('rs485', 'baud')


class RS485Client(UWHProtoHandler):
    def __init__(self, mgr, serial_port, baud):
        UWHProtoHandler.__init__(self, mgr)
        self.ser = serial.Serial(serial_port, baud, timeout=None)

    def send_raw(self, recipient, data):
        # TODO: chechsum? length?
        self.ser.write(binascii.hexlify(data) + b'\n')

    def listen_loop(self):
        recv = b''
        while True:
            try:
                recv += self.ser.read()
                if len(recv) > 0 and recv[-1] == b'\n'[0]:
                    self.recv_raw('', binascii.unhexlify(recv[:-1]))
                    recv = b''
            except Exception:
                recv = b''
                time.sleep(1)

    def listen_thread(self):
        thread = threading.Thread(target=self.listen_loop)
        thread.daemon = True
        thread.start()


class RS485Server(UWHProtoHandler):
    def __init__(self, mgr, serial_port, baud):
        UWHProtoHandler.__init__(self, mgr)
        self.ser = serial.Serial(serial_port, baud, timeout=0)

    def send_raw(self, recipient, data):
        self.ser.write(binascii.hexlify(data) + b'\n')

    def broadcast_loop(self):
        while True:
            try:
                while True:
                    (gkf_kind, gkf_msg) = self.get_GameKeyFrame()
                    (pen_kind, pen_msgs) = self.get_Penalties()
                    (gol_kind, gol_msgs) = self.get_Goals()

                    self.send_message('', gkf_kind, gkf_msg)

                    for msg in pen_msgs:
                        self.send_message('', pen_kind, msg)

                    for msg in gol_msgs:
                        self.send_message('', gol_kind, msg)

                    time.sleep(0.1)

            except Exception as e:
                import traceback
                print(e)
                traceback.print_tb(e.__traceback__)
                time.sleep(1)

    def broadcast_thread(self):
        thread = threading.Thread(target=self.broadcast_loop)
        thread.daemon = True
        thread.start()
