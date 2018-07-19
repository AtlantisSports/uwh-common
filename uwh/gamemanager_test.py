from .gamemanager import GameManager, GameState, TimeoutState, Penalty, TeamColor, PoolLayout

import time

_observers = [GameManager()]

def test_gameClock():
    mgr = GameManager(_observers)
    assert mgr.gameClock() == 0

    mgr.setGameClock(1)
    assert mgr.gameClock() == 1


def test_whiteScore():
    mgr = GameManager(_observers)
    assert mgr.whiteScore() == 0

    mgr.setWhiteScore(1)
    assert mgr.whiteScore() == 1


def test_whiteGoal():
    mgr = GameManager(_observers)
    assert mgr.whiteScore() == 0

    mgr.setGameClock(42)
    mgr.addWhiteGoal(5)
    assert mgr.whiteScore() == 1
    assert len(mgr.goals()) == 1
    assert mgr.goals()[0].goal_no() == 1
    assert mgr.goals()[0].player() == 5
    assert mgr.goals()[0].state() == GameState.first_half
    assert mgr.goals()[0].team() == TeamColor.white
    assert mgr.goals()[0].time() == 42

def test_blackScore():
    mgr = GameManager(_observers)
    assert mgr.blackScore() == 0

    mgr.setBlackScore(1)
    assert mgr.blackScore() == 1


def test_blackGoal():
    mgr = GameManager(_observers)
    assert mgr.blackScore() == 0

    mgr.setGameClock(42)
    mgr.addBlackGoal(4)
    assert mgr.blackScore() == 1
    assert len(mgr.goals()) == 1
    assert mgr.goals()[0].goal_no() == 1
    assert mgr.goals()[0].player() == 4
    assert mgr.goals()[0].state() == GameState.first_half
    assert mgr.goals()[0].team() == TeamColor.black
    assert mgr.goals()[0].time() == 42

def test_gameClockRunning():
    mgr = GameManager(_observers)
    assert mgr.gameClockRunning() is False
    assert mgr._time_at_start is None

    mgr.setGameClockRunning(True)
    assert mgr.gameClockRunning() is True

    time.sleep(1)

    before = mgr._time_at_start
    mgr.setGameClockRunning(True)
    assert mgr.gameClockRunning() is True
    assert before == mgr._time_at_start

    mgr.setGameClock(1)
    assert mgr._time_at_start


def test_passive():
    mgr = GameManager(_observers)
    mgr.setPassive()

    assert mgr.passive()
    assert not _observers[0].passive()

    mgr.setGameClockRunning(True)
    mgr.setGameClock(42)

    time.sleep(1)

    assert mgr.gameClock() == 42


def test_gameState():
    mgr = GameManager(_observers)
    mgr.setGameState(GameState.first_half)
    assert mgr.gameState() == GameState.first_half


def test_timeoutState():
    mgr = GameManager(_observers)
    mgr.setTimeoutState(TimeoutState.ref)
    assert mgr.timeoutState() == TimeoutState.ref


def test_penalty_servedCompletely():
    mgr = GameManager(_observers)
    p = Penalty(24, TeamColor.white, 5 * 60, 10 * 60)

    assert p.servedCompletely(mgr)


def test_penalty_dismissed():
    p = Penalty(24, TeamColor.white, -1, 10 * 60)

    assert p.dismissed()


def test_penalty_getters():
    p = Penalty(24, TeamColor.white, 5 * 60, 10 * 60)

    assert p.player() == 24
    assert p.team() == TeamColor.white
    assert p.startTime() == 10 * 60
    assert p.duration() == 5 * 60


def test_addPenalty():
    p = Penalty(24, TeamColor.white, 5 * 60)
    mgr = GameManager(_observers)

    mgr.addPenalty(p, mgr.gameClock())
    assert len(mgr.penalties(TeamColor.white)) == 1
    assert len(mgr.penalties(TeamColor.black)) == 0

    mgr.delPenalty(p)
    assert len(mgr.penalties(TeamColor.white)) == 0
    assert len(mgr.penalties(TeamColor.black)) == 0


def test_penaltyStateChange():
    mgr = GameManager(_observers)
    p = Penalty(24, TeamColor.white, 5 * 60)
    mgr.addPenalty(p, mgr.gameClock())

    mgr.pauseOutstandingPenalties()
    mgr.setGameState(GameState.half_time)
    assert len(mgr.penalties(TeamColor.white)) == 1

    mgr.setGameState(GameState.second_half)
    mgr.restartOutstandingPenalties()
    assert len(mgr.penalties(TeamColor.white)) == 1

    mgr.setGameState(GameState.game_over)
    mgr.deleteAllPenalties()
    assert len(mgr.penalties(TeamColor.white)) == 0


def test_penalty_start():
    p = Penalty(24, TeamColor.white, 5 * 60)
    mgr = GameManager(_observers)

    mgr.setGameClock(10 * 60)

    mgr.addPenalty(p, mgr.gameClock())
    mgr.setGameClockRunning(True)
    mgr.setGameClockRunning(False)

def test_penalty_setPlayer():
    p = Penalty(24, TeamColor.white, 5 * 60)

    assert p.player() == 24
    p.setPlayer(42)
    assert p.player() == 42


def test_penalty_duration():
    p = Penalty(24, TeamColor.white, 5 * 60)

    assert p.duration() == 5 * 60
    p.setDuration(4 * 60)
    assert p.duration() == 4 * 60


def test_penalty_addWhileRunning():
    mgr = GameManager(_observers)
    mgr.setGameClock(5*60)
    mgr.setGameClockRunning(True)
    p = Penalty(24, TeamColor.white, 5 * 60)
    mgr.addPenalty(p, mgr.gameClock())


def test_penalty_halftime():
    mgr = GameManager()
    p = Penalty(24, TeamColor.white, 5 * 60)
    mgr.addPenalty(p, mgr.gameClock())

    mgr.setGameClock(1 * 60)
    mgr.setGameClockRunning(True)
    mgr.setGameClockRunning(False)
    mgr.setGameClock(0)

    mgr.pauseOutstandingPenalties()
    mgr.setGameState(GameState.half_time)

    mgr.setGameState(GameState.second_half)
    mgr.setGameClock(10 * 60)
    mgr.restartOutstandingPenalties()


def test_layout():
    mgr = GameManager()
    assert mgr.layout() == PoolLayout.white_on_right

    mgr.setLayout(PoolLayout.white_on_left)
    assert mgr.layout() == PoolLayout.white_on_left


def test_tid():
    mgr = GameManager()
    assert mgr.tid() is None

    mgr.setTid(14)
    assert mgr.tid() == 14


def test_gid():
    mgr = GameManager()
    assert mgr.gid() is None

    mgr.setGid(6)
    assert mgr.gid() == 6

