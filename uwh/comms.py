from . import messages_pb2
from .gamemanager import GameState, TimeoutState, TeamColor, Goal, Penalty, PoolLayout

def gs_from_proto_enum(proto_enum):
    return { messages_pb2.GameState_GameOver        : GameState.game_over,
             messages_pb2.GameState_PreGame         : GameState.pre_game,
             messages_pb2.GameState_FirstHalf       : GameState.first_half,
             messages_pb2.GameState_HalfTime        : GameState.half_time,
             messages_pb2.GameState_SecondHalf      : GameState.second_half,
             messages_pb2.GameState_WallClock       : GameState.game_over, # bold-faced lie
             messages_pb2.GameState_OTFirst         : GameState.ot_first,
             messages_pb2.GameState_OTHalf          : GameState.ot_half,
             messages_pb2.GameState_OTSecond        : GameState.ot_second,
             messages_pb2.GameState_SuddenDeath     : GameState.sudden_death,
             messages_pb2.GameState_PreOT           : GameState.pre_ot,
             messages_pb2.GameState_PreSuddenDeath  : GameState.pre_sudden_death,
           }[proto_enum]

def ts_from_proto_enum(proto_enum):
    return {
             messages_pb2.TimeoutState_None         : TimeoutState.none,
             messages_pb2.TimeoutState_RefTimeout   : TimeoutState.ref,
             messages_pb2.TimeoutState_WhiteTimeout : TimeoutState.white,
             messages_pb2.TimeoutState_BlackTimeout : TimeoutState.black,
             messages_pb2.TimeoutState_PenaltyShot  : TimeoutState.penalty_shot,
           }[proto_enum]

def l_from_proto_enum(proto_enum):
    return {
             messages_pb2.WhiteOnRight : PoolLayout.white_on_right,
             messages_pb2.WhiteOnLeft  : PoolLayout.white_on_left
           }[proto_enum]

def gs_to_proto_enum(gamemanager_enum):
    return { GameState.game_over        : messages_pb2.GameState_GameOver,
             GameState.pre_game         : messages_pb2.GameState_PreGame,
             GameState.first_half       : messages_pb2.GameState_FirstHalf,
             GameState.half_time        : messages_pb2.GameState_HalfTime,
             GameState.second_half      : messages_pb2.GameState_SecondHalf,
             GameState.ot_first         : messages_pb2.GameState_OTFirst,
             GameState.ot_half          : messages_pb2.GameState_OTHalf,
             GameState.ot_second        : messages_pb2.GameState_OTSecond,
             GameState.sudden_death     : messages_pb2.GameState_SuddenDeath,
             GameState.pre_ot           : messages_pb2.GameState_PreOT,
             GameState.pre_sudden_death : messages_pb2.GameState_PreSuddenDeath,
           }[gamemanager_enum]

def ts_to_proto_enum(gamemanager_enum):
    return { TimeoutState.none         : messages_pb2.TimeoutState_None,
             TimeoutState.ref          : messages_pb2.TimeoutState_RefTimeout,
             TimeoutState.white        : messages_pb2.TimeoutState_WhiteTimeout,
             TimeoutState.black        : messages_pb2.TimeoutState_BlackTimeout,
             TimeoutState.penalty_shot : messages_pb2.TimeoutState_PenaltyShot,
           }[gamemanager_enum]

def l_to_proto_enum(gamemanager_enum):
    return { PoolLayout.white_on_right : messages_pb2.WhiteOnRight,
             PoolLayout.white_on_left  : messages_pb2.WhiteOnLeft
           }[gamemanager_enum]


class UWHProtoHandler(object):
    def __init__(self, mgr):
        self._mgr = mgr

    def send_message(self, recipient, msg_kind, msg):
        self.send_raw(recipient, self.pack_message(msg_kind, msg))

    def send_raw(self, recipient, data):
        """ To be implemented by the deriving class """
        raise NotImplementedError("Not Yet Implemented")

    def recv_message(self, sender, kind, msg):
        if kind == messages_pb2.MessageType_Ping:
            self.handle_Ping(sender, msg)
        elif kind == messages_pb2.MessageType_GameKeyFrame:
            self.handle_GameKeyFrame(sender, msg)
        elif kind == messages_pb2.MessageType_Penalty:
            self.handle_Penalty(sender, msg)
        elif kind == messages_pb2.MessageType_Goal:
            self.handle_Goal(sender, msg)
        elif kind == messages_pb2.MessageType_GameTime:
            self.handle_GameTime(sender, msg)

    def recv_raw(self, sender, data):
        (kind, msg) = self.unpack_message(data)
        self.recv_message(sender, kind, msg)

    def expect_Pong(self, sender, data):
        (kind, msg) = self.unpack_message(data)
        if kind != messages_pb2.MessageType_Pong:
            raise ValueError("Message received wasn't pong")
        return msg.Data

    def message_for_msg_kind(self, msg_kind):
        return { messages_pb2.MessageType_Ping : messages_pb2.Ping,
                 messages_pb2.MessageType_Pong : messages_pb2.Pong,
                 messages_pb2.MessageType_GameKeyFrame : messages_pb2.GameKeyFrame,
                 messages_pb2.MessageType_Penalty : messages_pb2.Penalty,
                 messages_pb2.MessageType_Goal : messages_pb2.Goal,
                 messages_pb2.MessageType_GameTime : messages_pb2.GameTime,
               }[msg_kind]()

    def pack_message(self, msg_kind, msg):
        if 255 < msg_kind:
            raise ValueError("Message kind doesn't fit in one byte")
        length = msg.ByteSize()
        if 255 < length:
            raise ValueError("Message is too long to send over the wire")
        data = msg.SerializeToString()
        return bytearray([int(msg_kind), int(length)]) + data

    def unpack_message(self, data):
        msg_kind = data[0]
        msg_len = data[1]
        if msg_len + 2 != len(data):
            raise ValueError("Malformed message: lengths do not match")
        msg = self.message_for_msg_kind(msg_kind)
        msg.ParseFromString(data[2:])
        return (msg_kind, msg)

    def handle_Ping(self, sender, msg):
        kind = messages_pb2.MessageType_Pong
        pong = self.message_for_msg_kind(kind)
        pong.Data = msg.Data
        self.send_message(sender, kind, pong)

    def handle_GameKeyFrame(self, sender, msg):
        if msg.HasField('ClockRunning'):
            self._mgr.setGameClockRunning(msg.ClockRunning)

        if msg.HasField('TimeLeft'):
            self._mgr.setGameClock(msg.TimeLeft)

        if msg.HasField('BlackScore'):
            self._mgr.setBlackScore(msg.BlackScore)

        if msg.HasField('WhiteScore'):
            self._mgr.setWhiteScore(msg.WhiteScore)

        if msg.HasField('Period'):
            period = gs_from_proto_enum(msg.Period)
            if period == GameState.pre_game:
                self._mgr.deleteAllPenalties()
                self._mgr.delAllGoals()
            self._mgr.setGameState(period)

        if msg.HasField('Timeout'):
            self._mgr.setTimeoutState(ts_from_proto_enum(msg.Timeout))

        if msg.HasField('Layout'):
            self._mgr.setLayout(l_from_proto_enum(msg.Layout))

        if msg.HasField('tid'):
            self._mgr.setTid(msg.tid)

        if msg.HasField('gid'):
            self._mgr.setGid(msg.gid)

        if msg.HasField('TimeAtPause'):
            self._mgr.setGameClockAtPause(msg.TimeAtPause)

    def handle_Penalty(self, sender, msg):
        if (msg.HasField('PlayerNo') and
            msg.HasField('Duration') and
            msg.HasField('StartTime')):
            team = TeamColor.white if msg.IsWhite else TeamColor.black
            player_no = self.as_int(msg.PlayerNo)
            pp = Penalty(player_no, team,
                         msg.Duration, start_time=msg.StartTime or None,
                         duration_remaining=msg.DurationRemaining)
            self._mgr.delPenaltyByPlayer(player_no, team)
            self._mgr.addPenalty(pp)

    def handle_Goal(self, sender, msg):
        if (msg.HasField('GoalNo') and
            msg.HasField('PlayerNo') and
            msg.HasField('IsWhite') and
            msg.HasField('TimeLeft') and
            msg.HasField('Period')):
            team = TeamColor.white if msg.IsWhite else TeamColor.black
            player_no = self.as_int(msg.PlayerNo)
            gg = Goal(msg.GoalNo, player_no, team,
                      msg.TimeLeft, gs_from_proto_enum(msg.Period))
            self._mgr.delGoalByNo(msg.GoalNo, team)
            self._mgr.addGoal(gg)

    def handle_GameTime(self, sender, msg):
        self._mgr.setGameClock(msg.TimeLeft)

    def as_int(self, n):
        try:
            return int(n)
        except ValueError:
            return -1

    def get_GameKeyFrame(self):
        kind = messages_pb2.MessageType_GameKeyFrame
        msg = self.message_for_msg_kind(kind)
        msg.ClockRunning = self._mgr.gameClockRunning()
        msg.TimeLeft = self._mgr.gameClock()
        msg.BlackScore = self._mgr.blackScore()
        msg.WhiteScore = self._mgr.whiteScore()
        msg.Period = gs_to_proto_enum(self._mgr.gameState())
        msg.Timeout = ts_to_proto_enum(self._mgr.timeoutState())
        msg.Layout = l_to_proto_enum(self._mgr.layout())
        msg.tid = self._mgr.tid()
        msg.gid = self._mgr.gid()
        msg.TimeAtPause = self._mgr.gameClockAtPause()

        return (kind, msg)

    def get_Penalties(self):
        kind = messages_pb2.MessageType_Penalty
        msgs = []

        for p in self._mgr.penalties(TeamColor.black):
            msg = self.message_for_msg_kind(kind)
            msg.PlayerNo = self.as_int(p.player())
            msg.Duration = p.duration()
            msg.StartTime = p.startTime() or 0
            msg.DurationRemaining = p.durationRemaining()
            msg.IsWhite = False
            msgs += [msg]

        for p in self._mgr.penalties(TeamColor.white):
            msg = self.message_for_msg_kind(kind)
            msg.PlayerNo = self.as_int(p.player())
            msg.Duration = p.duration()
            msg.StartTime = p.startTime() or 0
            msg.DurationRemaining = p.durationRemaining()
            msg.IsWhite = True
            msgs += [msg]

        return (kind, msgs)

    def get_Goals(self):
        kind = messages_pb2.MessageType_Goal
        msgs = []

        for g in self._mgr.goals():
            msg = self.message_for_msg_kind(kind)
            msg.GoalNo = g.goal_no()
            msg.PlayerNo = self.as_int(g.player())
            msg.IsWhite = g.team() == TeamColor.white
            msg.TimeLeft = g.time()
            msg.Period = g.state()
            msgs += [msg]

        return (kind, msgs)

    def get_GameTime(self):
        kind = messages_pb2.MessageType_GameTime
        msg = self.message_for_msg_kind(kind)
        msg.TimeLeft = self._mgr.gameClock()

        return (kind, msg)
