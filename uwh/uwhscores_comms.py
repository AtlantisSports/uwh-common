import requests
import threading

class Transaction():
    get_tournament_list = 0
    get_tournament = 1
    get_game_list = 2
    get_game = 3
    send_game_score = 4
    get_team_list = 5
    get_standings = 6
    get_user_token = 7
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
        self.current_tid = None
        self.current_tournament = None
        self.game_list = None
        self.current_gid = None
        self.current_game = None
        self.team_list = None

    def __getattribute__(self, attr):
        if ((object.__getattribute__(self, '_thread') is not None)
                and (object.__getattribute__(self, '_reply') is not None)):
            object.__getattribute__(self, '_process_reply')()
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
        self._thread.start()

    def get_tournament(self):
        '''
        Start a get of the tournament with current_tid from the server.
        When the GET is complete, the tournament will be stored as a dict
        in current_tournament.

        current_tid must be set before this funcion is called
        '''
        if self.current_tid is None:
            raise ValueError('current_tid must be set before get_tournament is called')
        self._transaction_type = Transaction.get_tournament
        self._thread = threading.Thread(
                target=self._get,
                args=(self._base_address + 'tournaments/' + str(self.current_tid),))
        self._thread.start()

    def get_game_list(self):
        '''
        Start a get of the game list for the tournament with current_tid
        from the server. When the GET is complete, the list will be stored
        as a dict in game_list with the gids as keys and dicts of the games
        as values.

        current_tid must be set before this funcion is called
        '''
        if self.current_tid is None:
            raise ValueError('current_tid must be set before get_game_list is called')
        self._transaction_type = Transaction.get_game_list
        self._thread = threading.Thread(
                target=self._get,
                args=(self._base_address + 'tournaments/' + str(self.current_tid) + '/games',))
        self._thread.start()

    def get_game(self):
        '''
        Start a get of the game with current_gid from the server. When the
        GET is complete, the game will be stored as a dict in current_game.

        current_tid and current_gid must be set before this funcion is called
        '''
        if self.current_tid is None:
            raise ValueError('current_tid must be set before get_game is called')
        if self.current_gid is None:
            raise ValueError('current_gid must be set before get_game is called')
        self._transaction_type = Transaction.get_game
        self._thread = threading.Thread(
                target=self._get,
                args=(self._base_address + 'tournaments/' + str(self.current_tid)
                      + '/games/' + str(self.current_gid),))
        self._thread.start()

    def get_team_list(self):
        '''
        Start a get of the team list from the server. When the GET is complete,
        the list will be stored as a dict in team_list, with the team_ids as
        keys, and dicts of the teams as values.

        current_tid must be set before this funcion is called
        '''
        if self.current_tid is None:
            raise ValueError('current_tid must be set before get_team_list is called')
        self._transaction_type = Transaction.get_team_list
        self._thread = threading.Thread(
                target=self._get,
                args=(self._base_address + 'tournaments/' + str(self.current_tid) + '/teams',))
        self._thread.start()

    def get_standings(self):
        '''
        Start a get of the standings from the server. When the GET is complete,
        the list will be stored as an array of dicts in standings.

        current_tid must be set before this funcion is called
        '''
        if self.current_tid is None:
            raise ValueError('current_tid must be set before get_standings is called')
        self._transaction_type = Transaction.get_standings
        self._thread = threading.Thread(
                target=self._get,
                args=(self._base_address + 'tournaments/' + str(self.current_tid)
                      + '/standings',))
        self._thread.start()

    def _get(self, loc):
        self._reply = requests.get(loc)

    def _process_reply(self):
        json = object.__getattribute__(self, '_reply').json()
        transaction_type = object.__getattribute__(self, '_transaction_type')
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
        elif transaction_type is Transaction.get_team_list:
            self.team_list = {json['teams'][i]['team_id']: json['teams'][i]
                                  for i in range(len(json['teams']))}
        elif transaction_type is Transaction.get_standings:
            self.standings = json['standings']
        self._thread = None
        self._transaction_type = None
        self._reply = None

    @property
    def waiting_for_server(self):
        return self._thread is not None and self._reply is None
