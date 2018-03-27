import requests
import threading

class Transaction():
    get_tournament_list = 0
    get_tournament = 1
    get_game_list = 2
    get_game = 3
    send_game_score = 4
    get_teams = 5
    get_standings = 6
    get_user_token = 7
    logout = 8


class UWHScores(object):

    def __init__(self, base_address='https://uwhscores.com/api/v1/'):
        self._base_address = base_address
        self._thread = None
        self._reply = None
        self._transaction_type = None
        self.tournament_list = None
        self.current_tid = None
        self.current_tournament = None
        self.game_list = None

    def __getattribute__(self, attr):
        if ((object.__getattribute__(self, '_thread') is not None)
                and (object.__getattribute__(self, '_reply') is not None)):
            object.__getattribute__(self, '_process_reply')()
        return object.__getattribute__(self, attr)

    def get_tournament_list(self):
        self._transaction_type = Transaction.get_tournament_list
        self._thread = threading.Thread(target=self._get,
                                        args=(self._base_address + 'tournaments',))
        self._thread.start()

    def get_tournament(self):
        self._transaction_type = Transaction.get_tournament
        self._thread = threading.Thread(
                target=self._get,
                args=(self._base_address + 'tournaments/' + str(self.current_tid),))
        self._thread.start()

    def get_game_list(self):
        self._transaction_type = Transaction.get_game_list
        self._thread = threading.Thread(
                target=self._get,
                args=(self._base_address + 'tournaments/' + str(self.current_tid) + '/games',))
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
        object.__setattr__(self, '_thread', None)
        object.__setattr__(self, '_transaction_type', None)
        object.__setattr__(self, '_reply', None)

    @property
    def waiting_for_server(self):
        return self._thread is not None and self._reply is None
