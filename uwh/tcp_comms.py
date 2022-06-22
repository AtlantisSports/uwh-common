from configparser import ConfigParser
import json
import socket
import threading
from splitstream import splitfile
from .gamemanager import GameState, TimeoutState, TeamColor, Goal, Penalty, PoolLayout


def TcpConfigParser():
    defaults = {
        'ip': '127.0.0.1',
        'port': 8000,
    }
    parser = ConfigParser(defaults=defaults)
    parser.add_section('tcp')
    return parser


def ip(cfg):
    return cfg.get('tcp', 'ip')


def port(cfg):
    return int(cfg.get('tcp', 'port'))


class TcpClient():
    def __init__(self, mgr, ip, port):
        self._mgr = mgr
        self._ip = ip
        self._port = port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        self.sock = sock

    def listen_loop(self):
        buf = b''
        while True:
            try:
                ret = self.sock.recv(2048)
                if not ret:
                    print("Scoket disconnected, reconnecting...")
                    while True:
                        try:
                            sock = socket.socket(
                                socket.AF_INET, socket.SOCK_STREAM)
                            sock.connect((self._ip, self._port))
                            self.sock = sock
                            break
                        except ConnectionRefusedError:
                            pass

                buf += ret
                loc = buf.find(b'\n')
                if loc:
                    json_str = buf[:loc]
                    buf = buf[loc+1:]
                    json_obj = json.loads(json_str)
                    self.handle_recv(json_obj)
            except Exception as e:
                buf = b''
                print(f"Error in tcp listen loop: {e}")

    def listen_thread(self):
        thread = threading.Thread(target=self.listen_loop)
        thread.daemon = True
        thread.start()

    def handle_recv(self, json_msg):
        try:
            self._mgr.setBlackScore(json_msg["b_score"])
            self._mgr.setWhiteScore(json_msg["w_score"])

            if json_msg["timeout"] == "None":
                self._mgr.setGameClock(json_msg["secs_in_period"])
            else:
                self._mgr.setGameClockAtPause(json_msg["secs_in_period"])
                if "Black" in json_msg["timeout"]:
                    self._mgr.setTimeoutState(TimeoutState.black)
                    self._mgr.setGameClock(json_msg["timeout"]["Black"])
                elif "White" in json_msg["timeout"]:
                    self._mgr.setTimeoutState(TimeoutState.white)
                    self._mgr.setGameClock(json_msg["timeout"]["White"])
                elif "Ref" in json_msg["timeout"]:
                    self._mgr.setTimeoutState(TimeoutState.ref)
                    self._mgr.setGameClock(json_msg["timeout"]["Ref"])
                elif "PenaltyShot" in json_msg["timeout"]:
                    self._mgr.setTimeoutState(TimeoutState.penalty_shot)
                    self._mgr.setGameClock(json_msg["timeout"]["PenaltyShot"])
                else:
                    print(
                        f"Error: invalid timeout value in tcp json: {json_msg['timeout']}")

            self._mgr.setGameState({
                "BetweenGames": GameState.game_over if json_msg["is_old_game"] else GameState.pre_game,
                "FirstHalf": GameState.first_half,
                "HalfTime": GameState.half_time,
                "SecondHalf": GameState.second_half,
                "PreOvertime": GameState.pre_ot,
                "OvertimeFirstHalf": GameState.ot_first,
                "OvertimeHalfTime": GameState.ot_half,
                "OvertimeSecondHalf": GameState.ot_second,
                "PreSuddenDeath": GameState.pre_sudden_death,
                "SuddenDeath": GameState.sudden_death,
            }[json_msg["current_period"]])

            if json_msg["tournament_id"] != 0:
                self._mgr.setTid(json_msg["tournament_id"])

            if json_msg["current_period"] == "BetweenGames" and not json_msg["is_old_game"]:
                self._mgr.setGid(json_msg["next_game_number"])
            else:
                self._mgr.setGid(json_msg["game_number"])

            self._mgr.deleteAllPenalties()

            for json_pen in json_msg["b_penalties"]:
                if json_pen["time"] == "TotalDismissal":
                    remaining = -1
                else:
                    remaining = json_pen["time"]["Seconds"]

                pp = Penalty(json_pen["player_number"], TeamColor.black,
                             0, start_time=None,
                             duration_remaining=remaining)
                self._mgr.addPenalty(pp)

            for json_pen in json_msg["w_penalties"]:
                if json_pen["time"] == "TotalDismissal":
                    duration = -1
                    remaining = 1800
                else:
                    duration = 0
                    remaining = json_pen["time"]["Seconds"]

                pp = Penalty(json_pen["player_number"], TeamColor.white,
                             duration, start_time=None,
                             duration_remaining=remaining)
                self._mgr.addPenalty(pp)

        except KeyError as e:
            print(f"Error: Missing expected key in JSON message: {e}")
