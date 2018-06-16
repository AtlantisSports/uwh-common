import time
import math

class GameState(object):
    game_over = 0
    first_half = 1
    half_time = 2
    second_half = 3
    pre_game = 4


class TimeoutState(object):
    none = 0
    ref = 1
    white = 2
    black = 3
    penalty_shot = 4


class TeamColor(object):
    black = 0
    white = 1


class PoolLayout(object):
    white_on_right = 0
    white_on_left = 1


def now():
    return math.floor(time.time())

def observed(function):
    def wrapper(self, *args, **kwargs):
        function(self, *args, **kwargs)
        for mgr in self._observers:
            function(mgr, *args, **kwargs)
    return wrapper

class GameManager(object):

    def __init__(self, observers=None):
        self._white_score = 0
        self._black_score = 0
        self._duration = 0
        self._time_at_start = None
        self._game_state = GameState.first_half
        self._timeout_state = TimeoutState.none
        self._penalties = [[],[]]
        self._observers = observers or []
        self._is_passive = False
        self._layout = PoolLayout.white_on_right
        self._tid = None
        self._gid = None

    def gameClock(self):
        if not self.gameClockRunning() or self._is_passive:
            return self._duration

        game_clock = self._duration - (now() - self._time_at_start)
        return game_clock

    @observed
    def setGameClock(self, n):
        self._duration = n

        if self.gameClockRunning():
            self._time_at_start = now()

    def whiteScore(self):
        return self._white_score

    @observed
    def setWhiteScore(self, n):
        self._white_score = n

    def blackScore(self):
        return self._black_score

    @observed
    def setBlackScore(self, n):
        self._black_score = n

    def gameClockRunning(self):
        return bool(self._time_at_start)

    def setGameClockRunning(self, b):
        if b == self.gameClockRunning():
            return

        if b:
            self._time_at_start = now()
            if (not self.gameStateHalfTime() and
                not self.timeoutStateWhite() and
                not self.timeoutStateBlack()):
                self._start_unstarted_penalties(self.gameClock())
        else:
            self._duration -= now() - self._time_at_start
            self._time_at_start = None

    def gameState(self):
        return self._game_state

    @observed
    def setGameState(self, state):
        self._game_state = state

    def timeoutState(self):
        return self._timeout_state

    @observed
    def setTimeoutState(self, state):
        self._timeout_state = state

    def gameStatePreGame(self):
        return self._game_state == GameState.pre_game

    @observed
    def setGameStatePreGame(self):
        self.setGameState(GameState.pre_game)

    def gameStateFirstHalf(self):
        return self._game_state == GameState.first_half

    @observed
    def setGameStateFirstHalf(self):
        self.setGameState(GameState.first_half)

    def gameStateHalfTime(self):
        return self._game_state == GameState.half_time

    @observed
    def setGameStateHalfTime(self):
        self.setGameState(GameState.half_time)

    def gameStateSecondHalf(self):
        return self._game_state == GameState.second_half

    @observed
    def setGameStateSecondHalf(self):
        self.setGameState(GameState.second_half)

    def gameStateGameOver(self):
        return self._game_state == GameState.game_over

    @observed
    def setGameStateGameOver(self):
        self.setGameState(GameState.game_over)

    def timeoutStateNone(self):
        return self._timeout_state == TimeoutState.none

    @observed
    def setTimeoutStateNone(self):
        self._timeout_state = TimeoutState.none

    def timeoutStateRef(self):
        return self._timeout_state == TimeoutState.ref

    @observed
    def setTimeoutStateRef(self):
        self._timeout_state = TimeoutState.ref

    def timeoutStatePenaltyShot(self):
        return self._timeout_state == TimeoutState.penalty_shot

    @observed
    def setTimeoutStatePenaltyShot(self):
        self._timeout_state = TimeoutState.penalty_shot

    def timeoutStateWhite(self):
        return self._timeout_state == TimeoutState.white

    @observed
    def setTimeoutStateWhite(self):
        self._timeout_state = TimeoutState.white

    def timeoutStateBlack(self):
        return self._timeout_state == TimeoutState.black

    def setTimeoutStateBlack(self):
        self._timeout_state = TimeoutState.black

    @observed
    def addPenalty(self, p):
        self._penalties[p.team()].append(p)
        if (self.gameClockRunning() and not self.passive()
            and not self.gameStatePreGame()
            and not self.gameStateHalfTime()
            and not self.gameStateGameOver()):
            p.setStartTime(self.gameClock())

    @observed
    def delPenalty(self, p):
        if p in self._penalties[p.team()]:
            self._penalties[p.team()].remove(p)

    @observed
    def delPenaltyByPlayer(self, player_no, team_color):
        self._penalties[team_color] = [p for p in self._penalties[team_color] if p.player() != player_no]

    def penalties(self, team_color):
        return self._penalties[team_color]

    @observed
    def deleteAllPenalties(self):
        self._penalties = [[],[]]

    def _start_unstarted_penalties(self, game_clock):
        for p in self._penalties[TeamColor.white] + self._penalties[TeamColor.black]:
            if not p.startTime():
                p.setStartTime(game_clock)

    @observed
    def pauseOutstandingPenalties(self):
        for p in self._penalties[TeamColor.white] + self._penalties[TeamColor.black]:
            if not p.servedCompletely(self):
                p.pause(self)

    @observed
    def restartOutstandingPenalties(self):
        for p in self._penalties[TeamColor.white] + self._penalties[TeamColor.black]:
            if not p.servedCompletely(self):
                p.restart(self)

    @observed
    def deleteServedPenalties(self):
        self._penalties[TeamColor.white] = [p for p in self._penalties[TeamColor.white] if not p.servedCompletely(self)]
        self._penalties[TeamColor.black] = [p for p in self._penalties[TeamColor.black] if not p.servedCompletely(self)]

    def setPassive(self):
        self._is_passive = True

    def passive(self):
        return self._is_passive

    @observed
    def setLayout(self, layout):
        self._layout = layout

    def layout(self):
        return self._layout

    @observed
    def setTid(self, tid):
        self._tid = tid

    def tid(self):
        return self._tid

    @observed
    def setGid(self, gid):
        self._gid = gid

    def gid(self):
        return self._gid

class Penalty(object):

    def __init__(self, player, team, duration, start_time=None,
                 duration_remaining=None):
        self._player = player
        self._team = team

        # Game time when the penalty started
        self._start_time = start_time

        # Total time of the penalty
        self._duration = duration

        # Amount left to be served (might be less than duration if partially
        # served in the first half)
        self._duration_remaining = duration_remaining or duration

    def __repr__(self):
        return "Player(player={}, team={}, duration={}, start_time={}, duration_remaining={})".format(
                       self._player, self._team, self._duration, self._start_time, self._duration_remaining)

    def setStartTime(self, start_time):
        self._start_time = start_time

    def startTime(self):
        return self._start_time

    def timeRemaining(self, mgr):
        if self._start_time is None:
            return self._duration_remaining
        game_clock = mgr.gameClock()
        remaining = self._duration_remaining - (self._start_time - game_clock)
        return max(remaining, 0)

    def servedCompletely(self, mgr):
        if self._duration == -1:
            return False
        return self.timeRemaining(mgr) <= 0

    def player(self):
        return self._player

    def setPlayer(self, player):
        self._player = player

    def team(self):
        return self._team

    def duration(self):
        return self._duration

    def setDuration(self, duration):
        self._duration = duration
        self._duration_remaining = self._duration_remaining or duration

    def durationRemaining(self):
        return self._duration_remaining

    def setDurationRemaining(self, duration):
        self._duration_remaining = duration

    def dismissed(self):
        return self._duration == -1

    def pause(self, mgr):
        if self._start_time is not None:
            self._duration_remaining = self.timeRemaining(mgr)
            self._start_time = None

    def restart(self, mgr):
        if self._start_time is None:
            self._start_time = mgr.gameClock()

