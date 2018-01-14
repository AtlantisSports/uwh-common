from . import messages_pb2

class UWHProtoHandler(object):
    def __init__(self):
        pass

    def send_message(self, recipient, msg_kind, msg):
        self.send_raw(recipient, self.pack_message(msg_kind, msg))

    def send_raw(self, recipient, data):
        """ To be implemented by the deriving class """
        raise NotImplementedError("Not Yet Implemented")

    def recv_message(self, sender, kind, msg):
        if kind == messages_pb2.MessageType_Ping:
            self.handle_Ping(sender, msg)

    def recv_raw(self, sender, data):
        (kind, msg) = self.unpack_message(data)
        self.recv_message(sender, kind, msg)

    def message_for_msg_kind(self, msg_kind):
        return { messages_pb2.MessageType_Ping : messages_pb2.Ping,
                 messages_pb2.MessageType_Pong : messages_pb2.Pong
               }[msg_kind]()

    def pack_message(self, msg_kind, msg):
        length = msg.ByteSize()
        assert length < 255 # XBee can't handle huge messages
        assert msg_kind < 255 # Only reserved two hex digits for it
        data = msg.SerializeToString()
        return bytearray([int(msg_kind), int(length)]) + data

    def unpack_message(self, data):
        msg_kind = data[0]
        msg_len = data[1]
        assert msg_len + 2 == len(data)
        msg = self.message_for_msg_kind(msg_kind)
        msg.ParseFromString(data[2:])
        return (msg_kind, msg)

    def handle_Ping(self, sender, msg):
        pong_kind = messages_pb2.MessageType_Pong
        pong = self.message_for_msg_kind(pong_kind)
        pong.Data = msg.Data
        self.send_message(sender, pong_kind, pong)
