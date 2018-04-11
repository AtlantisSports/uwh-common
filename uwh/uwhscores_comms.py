import requests
import threading

class Transaction():
    get_tournament_list = 0
    get_tournament = 1
    get_game_list = 2
    get_game = 3
    send_score = 4
    get_team_list = 5
    get_standings = 6
    login = 7
    logout = 8


class UWHScores(object):
    '''
    Class to communicate with UWHScores.com in the background. When
    initialized, sets all attributes to None. The get calls start a
    second thread which tries to reach the server and fetch get the
    requested information. When the get is complete, the information
    is stored in the associated attribute. If a second get is started
    before an ongoing one is complete, the original one will be aborted.
    waiting_for_server can be used to poll wether a get is complete.
    '''

    def __init__(self, base_address='https://uwhscores.com/api/v1/'):
        self._base_address = base_address
        self._thread = None
        self._reply = None
        self._transaction_type = None
        self.tournament_list = None
        self._current_tid = None
        self.current_tournament = None
        self.game_list = None
        self._current_gid = None
        self.current_game = None
        self.team_list = None
        self.standings = None
        self._user_token = None
        self._game_up_to_date = False

    def __getattribute__(self, attr):
        if object.__getattribute__(self, '_thread') is not None:
            if object.__getattribute__(self, '_reply') is not None:
                object.__getattribute__(self, '_process_reply')()
            elif not object.__getattribute__(self, '_thread').is_alive():
                object.__getattribute__(self, '_process_failure')()
        return object.__getattribute__(self, attr)

    def get_tournament_list(self):
        '''
        Start a GET of the tournament list from the server. When the
        GET is complete, the list will be stored as a dict in
        tournament_list, with the tids as keys, and dicts of the
        tournaments as values.
        '''
        self._transaction_type = Transaction.get_tournament_list
        self._thread = threading.Thread(target=self._get,
                                        args=(self._base_address + 'tournaments',))
        object.__getattribute__(self, '_thread').start()

    def get_tournament(self):
        '''
        Start a get of the tournament with current_tid from the server.
        When the GET is complete, the tournament will be stored as a dict
        in current_tournament.

        current_tid must be set before this funcion is called
        '''
        if self._current_tid is None:
            raise ValueError('current_tid must be set before get_tournament is called')
        self._transaction_type = Transaction.get_tournament
        self._thread = threading.Thread(
                target=self._get,
                args=(self._base_address + 'tournaments/' + str(self._current_tid),))
        object.__getattribute__(self, '_thread').start()

    def get_game_list(self):
        '''
        Start a get of the game list for the tournament with current_tid
        from the server. When the GET is complete, the list will be stored
        as a dict in game_list with the gids as keys and dicts of the games
        as values.

        current_tid must be set before this funcion is called
        '''
        if self._current_tid is None:
            raise ValueError('current_tid must be set before get_game_list is called')
        self._transaction_type = Transaction.get_game_list
        self._thread = threading.Thread(
                target=self._get,
                args=(self._base_address + 'tournaments/' + str(self._current_tid) + '/games',))
        object.__getattribute__(self, '_thread').start()

    def get_game(self):
        '''
        Start a get of the game with current_gid from the server. When the
        GET is complete, the game will be stored as a dict in current_game.

        current_tid and current_gid must be set before this funcion is called
        '''
        if self._current_tid is None:
            raise ValueError('current_tid must be set before get_game is called')
        if self._current_gid is None:
            raise ValueError('current_gid must be set before get_game is called')
        self._transaction_type = Transaction.get_game
        self._thread = threading.Thread(
                target=self._get,
                args=(self._base_address + 'tournaments/' + str(self._current_tid)
                      + '/games/' + str(self._current_gid),))
        object.__getattribute__(self, '_thread').start()

    def get_team_list(self):
        '''
        Start a get of the team list from the server. When the GET is complete,
        the list will be stored as a dict in team_list, with the team_ids as
        keys, and dicts of the teams as values.

        current_tid must be set before this funcion is called
        '''
        if self._current_tid is None:
            raise ValueError('current_tid must be set before get_team_list is called')
        self._transaction_type = Transaction.get_team_list
        self._thread = threading.Thread(
                target=self._get,
                args=(self._base_address + 'tournaments/' + str(self._current_tid) + '/teams',))
        object.__getattribute__(self, '_thread').start()

    def get_standings(self):
        '''
        Start a get of the standings from the server. When the GET is complete,
        the list will be stored as an array of dicts in standings.

        current_tid must be set before this funcion is called
        '''
        if self._current_tid is None:
            raise ValueError('current_tid must be set before get_standings is called')
        self._transaction_type = Transaction.get_standings
        self._thread = threading.Thread(
                target=self._get,
                args=(self._base_address + 'tournaments/' + str(self._current_tid)
                      + '/standings',))
        object.__getattribute__(self, '_thread').start()

    def login(self, uname, passwd):
        '''
        Login to the server. If login is sucessfull, the returned user token
        will be used for future send_score calls.
        '''
        self._transaction_type = Transaction.login
        self._thread = threading.Thread(target=self._get,
                                        args=((self._base_address + 'login', (uname, passwd))))
        object.__getattribute__(self, '_thread').start()

    def logout(self):
        '''
        logs the user out from the server.

        The user must be logged in before this method is called.
        '''
        if not self.is_loggedin:
            raise ValueError('user must be logged in before logout() is called')
        self._transaction_type = Transaction.logout
        self._thread = threading.Thread(target=self._get,
                                        args=((self._base_address + 'logout',
                                               (self._user_token, ''))))
        object.__getattribute__(self, '_thread').start()

    def send_score(self, white, black):
        '''
        Send given scores to the server for current tid and gid. after an
        update of current_tid or current_gid, get_game() must sucessfully
        complete before send_score() can be called. login() must sucessfully
        complete before send_score() can be called.

        current_tid and current_gid must be set before this function is called
        '''
        if self._current_tid is None:
            raise ValueError('current_tid must be set before send_score is called')
        if self._current_gid is None:
            raise ValueError('current_gid must be set before send_score is called')
        if not self.is_loggedin:
            raise ValueError('user must be logged in before send_score is called')
        if not self._game_up_to_date:
            raise ValueError('get_game must be caleed before send_score is called')

        info = {'tid': self._current_tid, 'gid': self._current_gid, 'score_w': white,
                'score_b': black, 'white_id': self.current_game['white_id'],
                'black_id': self.current_game['black_id']}

        self._transaction_type = Transaction.send_score
        self._thread = threading.Thread(
                target=self._post,
                args=(self._base_address + 'tournaments/' + str(self._current_tid)
                          + '/games/' + str(self._current_gid),
                      info))
        object.__getattribute__(self, '_thread').start()

    def _get(self, loc, authorization=None):
        try:
            if authorization is None:
                self._reply = requests.get(loc)
            else:
                self._reply = requests.get(loc, auth=authorization)
        except requests.exceptions.ConnectionError:
            self._reply = None

    def _post(self, loc, payload):
        self._reply = requests.post(loc, json=payload, auth=(self._user_token, ''))

    def _process_reply(self):
        transaction_type = object.__getattribute__(self, '_transaction_type')
        try:
            json = object.__getattribute__(self, '_reply').json()
        except ValueError:
            object.__getattribute__(self, '_process_failure')()
            return
        if transaction_type is Transaction.get_tournament_list:
            self.tournament_list = {json['tournaments'][i]['tid']: json['tournaments'][i]
                                        for i in range(len(json['tournaments']))}
        elif transaction_type is Transaction.get_tournament:
            self.current_tournament = json['tournament']
        elif transaction_type is Transaction.get_game_list:
            self.game_list = {json['games'][i]['gid']: json['games'][i]
                                  for i in range(len(json['games']))}
        elif transaction_type is Transaction.get_game:
            self.current_game = json['game']
            self._game_up_to_date = True
        elif transaction_type is Transaction.get_team_list:
            self.team_list = {json['teams'][i]['team_id']: json['teams'][i]
                                  for i in range(len(json['teams']))}
        elif transaction_type is Transaction.get_standings:
            self.standings = json['standings']
        elif transaction_type is Transaction.login:
            self._user_token = json['token']
        elif transaction_type is Transaction.logout:
            self._user_token = None
        self._thread = None
        self._transaction_type = None
        self._reply = None

    def _process_failure(self):
        transaction_type = object.__getattribute__(self, '_transaction_type')
        if transaction_type is Transaction.get_tournament_list:
            self.tournament_list = None
        elif transaction_type is Transaction.get_tournament:
            self.current_tournament = None
        elif transaction_type is Transaction.get_game_list:
            self.game_list = None
        elif transaction_type is Transaction.get_game:
            self.current_game = None
            self._game_up_to_date = False
        elif transaction_type is Transaction.get_team_list:
            self.team_list = None
        elif transaction_type is Transaction.get_standings:
            self.standings = None
        elif transaction_type is Transaction.login:
            self._user_token = None
        elif transaction_type is Transaction.logout:
            pass
        self._thread = None
        self._transaction_type = None
        self._reply = None


    @property
    def waiting_for_server(self):
        return self._thread is not None and self._reply is None

    @property
    def is_loggedin(self):
        return self._user_token is not None

    @property
    def current_tid(self):
        return self._current_tid

    @current_tid.setter
    def current_tid(self, val):
        self._game_up_to_date = False
        self._current_tid = val

    @property
    def current_gid(self):
        return self._current_gid

    @current_gid.setter
    def current_gid(self, val):
        self._game_up_to_date = False
        self._current_gid = val
