from .uwhscores_comms import UWHScores
from time import sleep

REPEAT_COUNT = 500
REPEAT_DELAY = 0.01

def test_get_tournament_list():
    uwhscores = UWHScores()
    uwhscores.get_tournament_list()

    repeats = 0
    while True:
        if not uwhscores.waiting_for_server:
            break
        elif repeats > REPEAT_COUNT:
            assert False
        repeats += 1
        sleep(REPEAT_DELAY)

    assert len(uwhscores.tournament_list) is 13
    assert uwhscores.tournament_list[14]['name'] == 'Battle@Altitude 2018'
    assert uwhscores.tournament_list[14]['location'] == 'Denver, CO'
    assert uwhscores.tournament_list[14]['is_active'] == False

def test_get_tournament():
    uwhscores = UWHScores()
    uwhscores.active_tid = 14
    uwhscores.get_tournament()

    repeats = 0
    while True:
        if not uwhscores.waiting_for_server:
            break
        elif repeats > REPEAT_COUNT:
            assert False
        repeats += 1
        sleep(REPEAT_DELAY)

    assert uwhscores.active_tournament['tid'] == 14
    assert uwhscores.active_tournament['name'] == 'Battle@Altitude 2018'
    assert uwhscores.active_tournament['location'] == 'Denver, CO'
    assert uwhscores.active_tournament['is_active'] == False


