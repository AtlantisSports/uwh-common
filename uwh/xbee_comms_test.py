from .xbee_comms import XBeeConfigParser, xbee_port, xbee_baud, xbee_clients

def test_XBeeConfigParser_defaults():
    cfg = XBeeConfigParser()

    assert xbee_port(cfg) == '/dev/tty.usbserial-DN03ZRU8'
    assert xbee_baud(cfg) == 9600
    assert xbee_clients(cfg) == []
