import pytest
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
    uwhscores.current_tid = 14
    uwhscores.get_tournament()

    repeats = 0
    while True:
        if not uwhscores.waiting_for_server:
            break
        elif repeats > REPEAT_COUNT:
            assert False
        repeats += 1
        sleep(REPEAT_DELAY)

    assert uwhscores.current_tournament['tid'] == 14
    assert uwhscores.current_tournament['name'] == 'Battle@Altitude 2018'
    assert uwhscores.current_tournament['location'] == 'Denver, CO'
    assert uwhscores.current_tournament['is_active'] == False

def test_get_game_list():
    uwhscores = UWHScores()
    uwhscores.current_tid = 14
    uwhscores.get_game_list()

    repeats = 0
    while True:
        if not uwhscores.waiting_for_server:
            break
        elif repeats > REPEAT_COUNT:
            assert False
        repeats += 1
        sleep(REPEAT_DELAY)

    assert uwhscores.game_list[1]['black'] == 'LA'
    assert uwhscores.game_list[1]['black_id'] == 1
    assert uwhscores.game_list[1]['pool'] == '1'
    assert uwhscores.game_list[4]['white'] == ' Seattle'
    assert uwhscores.game_list[4]['white_id'] == 6
    assert uwhscores.game_list[4]['start_time'] == '2018-01-27T09:02:00'
 
def test_get_game():
    uwhscores = UWHScores()
    uwhscores.current_tid = 14
    uwhscores.current_gid = 6
    uwhscores.get_game()

    repeats = 0
    while True:
        if not uwhscores.waiting_for_server:
            break
        elif repeats > REPEAT_COUNT:
            assert False
        repeats += 1
        sleep(REPEAT_DELAY)

    assert uwhscores.current_game['black'] == ' U19 Girls'
    assert uwhscores.current_game['black_id'] == 14
    assert uwhscores.current_game['day'] == 'Sat'
    assert uwhscores.current_game['start_time'] == '2018-01-27T09:34:00'
    assert uwhscores.current_game['white'] == ' US Elite Women'
    assert uwhscores.current_game['white_id'] == 17

def test_get_team_list():
    uwhscores = UWHScores()
    uwhscores.current_tid = 14
    uwhscores.get_team_list()

    repeats = 0
    while True:
        if not uwhscores.waiting_for_server:
            break
        elif repeats > REPEAT_COUNT:
            assert False
        repeats += 1
        sleep(REPEAT_DELAY)

    assert uwhscores.team_list[1]['name'] == 'LA'
    assert uwhscores.team_list[3]['name'] == ' Rainbow Raptors'
    assert uwhscores.team_list[7]['name'] == ' Cupcake Crocodiles'
    assert uwhscores.team_list[11]['name'] == ' Chicago'
    assert uwhscores.team_list[13]['name'] == ' Colorado B'
    assert uwhscores.team_list[17]['name'] == ' US Elite Women'

def test_throw_errors_without_ids():
    uwhscores = UWHScores()

    with pytest.raises(ValueError):
        uwhscores.get_tournament()
    with pytest.raises(ValueError):
        uwhscores.get_game_list()
    with pytest.raises(ValueError):
        uwhscores.get_game()
    with pytest.raises(ValueError):
        uwhscores.get_team_list()

    uwhscores.current_tid = 14
    with pytest.raises(ValueError):
        uwhscores.get_game()
