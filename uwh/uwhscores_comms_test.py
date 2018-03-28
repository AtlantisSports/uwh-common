import pytest
from .uwhscores_comms import UWHScores
from time import sleep

REPEAT_COUNT = 500
REPEAT_DELAY = 0.01

# Select either the local server or remote server below
USE_LOCAL_SERVER = True

if USE_LOCAL_SERVER:
    SERVER_ADDRESS = 'http://127.0.0.1:5000/api/v1/'
else:
    SERVER_ADDRESS = 'https://uwhscores.com/api/v1/'

def wait_for_server(uwhscores):
    for i in range(REPEAT_COUNT):
        if not uwhscores.waiting_for_server:
            return
        sleep(REPEAT_DELAY)
    assert False

def test_get_tournament_list():
    uwhscores = UWHScores(SERVER_ADDRESS)
    uwhscores.get_tournament_list()
    wait_for_server(uwhscores)

    assert len(uwhscores.tournament_list) is 13
    assert uwhscores.tournament_list[14]['name'] == 'Battle@Altitude 2018'
    assert uwhscores.tournament_list[14]['location'] == 'Denver, CO'
    assert uwhscores.tournament_list[14]['is_active'] == (True if USE_LOCAL_SERVER else False)

def test_get_tournament():
    uwhscores = UWHScores(SERVER_ADDRESS)
    uwhscores.current_tid = 14
    uwhscores.get_tournament()
    wait_for_server(uwhscores)

    assert uwhscores.current_tournament['tid'] == 14
    assert uwhscores.current_tournament['name'] == 'Battle@Altitude 2018'
    assert uwhscores.current_tournament['location'] == 'Denver, CO'
    assert uwhscores.current_tournament['is_active'] == (True if USE_LOCAL_SERVER else False)

def test_get_game_list():
    uwhscores = UWHScores(SERVER_ADDRESS)
    uwhscores.current_tid = 14
    uwhscores.get_game_list()
    wait_for_server(uwhscores)

    assert uwhscores.game_list[1]['black'] == 'LA'
    assert uwhscores.game_list[1]['black_id'] == 1
    assert uwhscores.game_list[1]['pool'] == '1'
    assert uwhscores.game_list[4]['white'] == ' Seattle'
    assert uwhscores.game_list[4]['white_id'] == 6
    assert uwhscores.game_list[4]['start_time'] == '2018-01-27T09:02:00'
 
def test_get_game():
    uwhscores = UWHScores(SERVER_ADDRESS)
    uwhscores.current_tid = 14
    uwhscores.current_gid = 6
    uwhscores.get_game()
    wait_for_server(uwhscores)

    assert uwhscores.current_game['black'] == ' U19 Girls'
    assert uwhscores.current_game['black_id'] == 14
    assert uwhscores.current_game['day'] == 'Sat'
    assert uwhscores.current_game['start_time'] == '2018-01-27T09:34:00'
    assert uwhscores.current_game['white'] == ' US Elite Women'
    assert uwhscores.current_game['white_id'] == 17

def test_get_team_list():
    uwhscores = UWHScores(SERVER_ADDRESS)
    uwhscores.current_tid = 14
    uwhscores.get_team_list()
    wait_for_server(uwhscores) 

    assert uwhscores.team_list[1]['name'] == 'LA'
    assert uwhscores.team_list[3]['name'] == ' Rainbow Raptors'
    assert uwhscores.team_list[7]['name'] == ' Cupcake Crocodiles'
    assert uwhscores.team_list[11]['name'] == ' Chicago'
    assert uwhscores.team_list[13]['name'] == ' Colorado B'
    assert uwhscores.team_list[17]['name'] == ' US Elite Women'

def test_get_standings():
    uwhscores = UWHScores(SERVER_ADDRESS)
    uwhscores.current_tid = 12
    uwhscores.get_standings()
    wait_for_server(uwhscores)

    assert uwhscores.standings[0]['team'] == 'Team Sexy'
    assert uwhscores.standings[0]['team_id'] == 2
    assert uwhscores.standings[0]['stats']['points'] == 21
    assert uwhscores.standings[2]['team'] == 'UF'
    assert uwhscores.standings[4]['team'] == 'Orlando'
    assert uwhscores.standings[6]['team'] == 'Swordfish'
    assert uwhscores.standings[7]['team'] == 'George Mason'

def test_throw_errors_without_ids():
    uwhscores = UWHScores(SERVER_ADDRESS)

    with pytest.raises(ValueError):
        uwhscores.get_tournament()
    with pytest.raises(ValueError):
        uwhscores.get_game_list()
    with pytest.raises(ValueError):
        uwhscores.get_game()
    with pytest.raises(ValueError):
        uwhscores.get_team_list()
    with pytest.raises(ValueError):
        uwhscores.get_standings()

    uwhscores.current_tid = 14
    with pytest.raises(ValueError):
        uwhscores.get_game()
