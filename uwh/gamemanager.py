import time
import math

class GameState(object):
    game_over = 0
    first_half = 1
    half_time = 2
    second_half = 3
    pre_game = 4
    ot_first = 6
    ot_half = 7
    ot_second = 8
    sudden_death = 9
    pre_ot = 10
    pre_sudden_death = 11

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
        self._goals = []
        self._duration = 0
        self._time_at_start = None
        self._game_state = GameState.first_half
        self._timeout_state = TimeoutState.none
        self._penalties = []
        self._observers = observers or []
        self._is_passive = False
        self._layout = PoolLayout.white_on_right
        self._tid = None
        self._gid = None
        self._clock_at_pause = 0

    def gameClock(self):
        if not self.gameClockRunning() or self._is_passive:
            return self._duration

        game_clock = self._duration - (now() - self._time_at_start)
        return int(game_clock)

    @observed
    def setGameClock(self, n):
        self._duration = int(n)

        if self.gameClockRunning():
            self._time_at_start = now()

    def gameClockAtPause(self):
        if (self._game_state == GameState.half_time or
            self._game_state == GameState.ot_half or
            self._game_state == GameState.pre_ot or
            self._game_state == GameState.pre_sudden_death):
            return self.gameClock()
        elif (self._timeout_state == TimeoutState.ref or
                 self._timeout_state == TimeoutState.black or
                 self._timeout_state == TimeoutState.white):
            return self._clock_at_pause
        else:
            return self.gameClock()

    @observed
    def setGameClockAtPause(self, val):
        self._clock_at_pause = int(val)

    def whiteScore(self):
        return self._white_score

    @observed
    def setWhiteScore(self, n):
        self._white_score = n

    @observed
    def addWhiteGoal(self, player_no):
        self._white_score += 1
        self._goals += [Goal(self._white_score + self._black_score,
                             player_no, TeamColor.white,
                             self.gameClockAtPause(), self._game_state)]

    def blackScore(self):
        return self._black_score

    @observed
    def setBlackScore(self, n):
        self._black_score = n

    @observed
    def addBlackGoal(self, player_no):
        self._black_score += 1
        self._goals += [Goal(self._white_score + self._black_score,
                             player_no, TeamColor.black,
                             self.gameClockAtPause(), self._game_state)]

    def goals(self):
        return self._goals

    @observed
    def addGoal(self, goal):
        self._goals += [goal]

    @observed
    def delGoalByNo(self, goal_no, team):
        self._goals = [g for g in self._goals if (g.goal_no() != goal_no or g.team() != team)]

    @observed
    def delAllGoals(self):
        self._goals = []

    def gameClockRunning(self):
        return bool(self._time_at_start)

    @observed
    def setGameClockRunning(self, b):
        if b == self.gameClockRunning():
            return

        if b:
            self._time_at_start = now()
            if (not self.gameState() == GameState.half_time and
                not self.timeoutState() == TimeoutState.white and
                not self.timeoutState() == TimeoutState.black):
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

    @observed
    def addPenalty(self, p):
        self._penalties.append(p)
        if (self.gameClockRunning() and not self.passive()
            and not self.gameState() == GameState.pre_game
            and not self.gameState() == GameState.half_time
            and not self.gameState() == GameState.game_over):
            p.setStartTime(self.gameClockAtPause())

    @observed
    def delPenalty(self, p):
        if p in self._penalties:
            self._penalties.remove(p)

    @observed
    def delPenaltyByPlayer(self, player_no, team_color):
        self._penalties = [p for p in self._penalties if p.team() != team_color or p.player() != player_no]

    def penalties(self, team_color):
        return [p for p in self._penalties if p.team() == team_color]

    @observed
    def deleteAllPenalties(self):
        self._penalties = []

    def _start_unstarted_penalties(self, game_clock):
        for p in self._penalties:
            if not p.startTime():
                p.setStartTime(game_clock)

    @observed
    def pauseOutstandingPenalties(self):
        for p in self._penalties:
            if not p.servedCompletely(self):
                p.pause(self)

    @observed
    def restartOutstandingPenalties(self):
        for p in self._penalties:
            if not p.servedCompletely(self):
                p.restart(self)

    @observed
    def deleteServedPenalties(self):
        self._penalties = [p for p in self._penalties if not p.servedCompletely(self)]

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
        self._start_time = None if start_time is None else int(start_time)

        # Total time of the penalty
        self._duration = int(duration)

        # Amount left to be served (might be less than duration if partially
        # served in the first half)
        self._duration_remaining = int(duration_remaining or duration)

    def __eq__(self, other):
        return self._player == other._player and self._team == other._team

    def __repr__(self):
        return "Player(player={}, team={}, duration={}, start_time={}, duration_remaining={})".format(
                       self._player, self._team, self._duration, self._start_time, self._duration_remaining)

    def setStartTime(self, start_time):
        self._start_time = None if start_time is None else int(start_time)

    def startTime(self):
        return self._start_time

    def timeRemaining(self, mgr):
        if self._start_time is None:
            return self._duration_remaining
        game_clock = mgr.gameClockAtPause()
        remaining = self._duration_remaining - (self._start_time - game_clock)
        return int(max(remaining, 0))

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

    def setTeam(self, team):
        self._team = team

    def duration(self):
        return self._duration

    def setDuration(self, duration):
        self._duration = int(duration)
        self._duration_remaining = int(self._duration_remaining or duration)

    def durationRemaining(self):
        return self._duration_remaining

    def setDurationRemaining(self, duration):
        self._duration_remaining = duration

    def dismissed(self):
        return self._duration == -1

    def pause(self, mgr):
        if self._start_time is not None:
            self._duration_remaining = int(self.timeRemaining(mgr))
            self._start_time = None

    def restart(self, mgr):
        if self._start_time is None:
            self._start_time = mgr.gameClock()


class Goal(object):

    def __init__(self, goal_no, player, team, time, state):
        self._goal_no = goal_no
        self._player = player
        self._team = team
        self._time = int(time)
        self._state = state

    def __repr__(self):
        return "Goal(goal_no={}, player={}, team={}, time={}, state={})".format(
                     self._goal_no, self._player, self._team, self._time, self._state)

    def goal_no(self):
        return self._goal_no

    def player(self):
        return self._player

    def team(self):
        return self._team

    def time(self):
        return self._time

    def state(self):
        return self._state

