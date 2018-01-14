from .comms import UWHProtoHandler
from . import messages_pb2

def test_PingPong():
    class Client(UWHProtoHandler):
        def __init__(self, send_raw):
            UWHProtoHandler.__init__(self)
            self._send_raw = send_raw

        def send_raw(self, recipient, data):
            self._send_raw(self, data)

    class Server(UWHProtoHandler):
        def __init__(self):
            UWHProtoHandler.__init__(self)
            self.received = False

        def recv_message(self, sender, kind, msg):
            assert kind == messages_pb2.MessageType_Pong
            assert msg.Data == 42
            self.received = True

        def send_raw(self, recipient, data):
            self.client.recv_raw(self, data)

    s = Server()
    c = Client(lambda r, d: s.recv_raw(r, d))
    s.client = c

    msg = messages_pb2.Ping()
    msg.Data = 42
    s.send_message(c, messages_pb2.MessageType_Ping, msg)
    assert s.received
