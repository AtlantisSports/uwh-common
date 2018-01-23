from .comms import UWHProtoHandler
from . import messages_pb2
from .gamemanager import GameManager

def test_PingPong():
    class Client(UWHProtoHandler):
        def __init__(self, mgr, send_raw):
            UWHProtoHandler.__init__(self, mgr)
            self._send_raw = send_raw

        def send_raw(self, recipient, data):
            self._send_raw(self, data)

    class Server(UWHProtoHandler):
        def __init__(self, mgr):
            UWHProtoHandler.__init__(self, mgr)
            self.received = False

        def recv_message(self, sender, kind, msg):
            assert kind == messages_pb2.MessageType_Pong
            assert msg.Data == 42
            self.received = True

        def send_raw(self, recipient, data):
            self.client.recv_raw(self, data)

    s_mgr = GameManager()
    s = Server(s_mgr)
    c_mgr = GameManager()
    c = Client(c_mgr, lambda r, d: s.recv_raw(r, d))
    s.client = c

    msg = messages_pb2.Ping()
    msg.Data = 42
    s.send_message(c, messages_pb2.MessageType_Ping, msg)
    assert s.received

def test_GameKeyFrame():
    class Client(UWHProtoHandler):
        def __init__(self, mgr, send_raw):
            UWHProtoHandler.__init__(self, mgr)
            self._send_raw = send_raw

        def send_raw(self, recipient, data):
            self._send_raw(self, data)

    class Server(UWHProtoHandler):
        def __init__(self, mgr):
            UWHProtoHandler.__init__(self, mgr)
            self.received = False

        def send_raw(self, recipient, data):
            self.client.recv_raw(self, data)

    s_mgr = GameManager()
    s = Server(s_mgr)
    c_mgr = GameManager()
    c = Client(c_mgr, lambda r, d: s.recv_raw(r, d))
    s.client = c

    s_mgr.setGameClockRunning(False)
    s_mgr.setGameClock(42)
    s_mgr.setWhiteScore(15)
    s_mgr.setBlackScore(7)
    s_mgr.setGameStateFirstHalf()
    s_mgr.setTimeoutStateRef()

    s.send_GameKeyFrame(c)

    assert c_mgr.gameClockRunning() == False
    assert c_mgr.gameClock() == 42
    assert c_mgr.whiteScore() == 15
    assert c_mgr.blackScore() == 7
    assert c_mgr.gameStateFirstHalf()
    assert c_mgr.timeoutStateRef()
