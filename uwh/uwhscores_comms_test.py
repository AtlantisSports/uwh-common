import pytest
from .uwhscores_comms import UWHScores
from time import sleep

REPEAT_COUNT = 500
REPEAT_DELAY = 0.01

# Select either the local server or remote server below
USE_LOCAL_SERVER = True

if USE_LOCAL_SERVER:
    SERVER_ADDRESS = 'http://127.0.0.1:5000/api/v1/'
    USERNAME = 'test@jimlester.net'
    PASSWORD = 'temp123!@#'
else:
    SERVER_ADDRESS = 'https://uwhscores.com/api/v1/'

IMPOSSIBLE_SERVER_ADDRESS = 'http://127.0.0.1:83492'

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
    assert uwhscores.team_list[11 ]['name'] == ' Chicago'
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

if USE_LOCAL_SERVER:
    def test_login_and_send_score():
        uwhscores = UWHScores(SERVER_ADDRESS)
        uwhscores.login(USERNAME, PASSWORD)
        wait_for_server(uwhscores)

        assert uwhscores.is_loggedin

        uwhscores.current_tid = 14
        uwhscores.current_gid = 6
        uwhscores.get_game()
        wait_for_server(uwhscores)
        uwhscores.send_score(white=2, black=3)
        wait_for_server(uwhscores)
        uwhscores.get_game()
        wait_for_server(uwhscores)

        assert uwhscores.current_game['black'] == ' U19 Girls'
        assert uwhscores.current_game['black_id'] == 14
        assert uwhscores.current_game['white'] == ' US Elite Women'
        assert uwhscores.current_game['white_id'] == 17
        assert uwhscores.current_game['score_w'] == 2
        assert uwhscores.current_game['score_b'] == 3
        
        uwhscores.send_score(white=20, black=4)
        wait_for_server(uwhscores)
        uwhscores.get_game()
        wait_for_server(uwhscores)

        assert uwhscores.current_game['score_w'] == 20
        assert uwhscores.current_game['score_b'] == 4

    def test_login_and_update_required_before_send_score():
        uwhscores = UWHScores(SERVER_ADDRESS)
        uwhscores.current_tid = 14
        uwhscores.current_gid = 6

        with pytest.raises(ValueError):
            uwhscores.send_score(white=14, black=8)

        uwhscores.login(USERNAME, PASSWORD)
        wait_for_server(uwhscores)
        assert uwhscores.is_loggedin

        with pytest.raises(ValueError):
            uwhscores.send_score(white=15, black=9)

    def test_logout():
        uwhscores = UWHScores(SERVER_ADDRESS)

        assert not uwhscores.is_loggedin
        uwhscores.login(USERNAME, PASSWORD)
        wait_for_server(uwhscores)
        assert uwhscores.is_loggedin

        uwhscores._base_address = IMPOSSIBLE_SERVER_ADDRESS
        uwhscores.logout()
        wait_for_server(uwhscores)
        assert uwhscores.is_loggedin

        uwhscores._base_address = SERVER_ADDRESS
        token = uwhscores._user_token
        uwhscores._user_token = 'jddsf'
        uwhscores.logout()
        wait_for_server(uwhscores)
        assert uwhscores.is_loggedin

        uwhscores._user_token = token
        uwhscores.logout()
        wait_for_server(uwhscores)
        assert not uwhscores.is_loggedin

def test_not_waiting_when_failed():
    uwhscores = UWHScores(IMPOSSIBLE_SERVER_ADDRESS)
    uwhscores.current_tid = 14
    uwhscores.current_gid = 6

    assert uwhscores.tournament_list is None
    uwhscores.get_tournament_list()
    wait_for_server(uwhscores)
    assert uwhscores.tournament_list is None

    assert uwhscores.current_tournament is None
    uwhscores.get_tournament()
    wait_for_server(uwhscores)
    assert uwhscores.current_tournament is None

    assert uwhscores.game_list is None
    uwhscores.get_game()
    wait_for_server(uwhscores)
    assert uwhscores.game_list is None

    assert uwhscores.current_game is None
    uwhscores.get_game()
    wait_for_server(uwhscores)
    assert uwhscores.current_game is None
    
    assert uwhscores.team_list is None
    uwhscores.get_team_list()
    wait_for_server(uwhscores)
    assert uwhscores.team_list is None

    assert uwhscores.standings is None
    uwhscores.get_standings()
    wait_for_server(uwhscores)
    assert uwhscores.standings is None
    
    assert not uwhscores.is_loggedin
    uwhscores.login(USERNAME, PASSWORD)
    wait_for_server(uwhscores)
    assert not uwhscores.is_loggedin

def test_throw_errors_without_ids_or_login():
    uwhscores = UWHScores(SERVER_ADDRESS)

    with pytest.raises(ValueError):
        uwhscores.logout()

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
    with pytest.raises(ValueError):
        uwhscores.send_score(white=16, black=10)

    uwhscores.current_tid = 14
    with pytest.raises(ValueError):
        uwhscores.get_game()
    with pytest.raises(ValueError):
        uwhscores.send_score(white=17, black=11)

