import requests
import threading
from PIL import Image
from functools import wraps, lru_cache

class UWHScores(object):
    def __init__(self, base_address='https://uwhscores.com/api/v1/', mock=False):
        self._base_address = base_address
        self._mock = mock
        self._fail_handler = lambda x : print(x)

    def get_tournament_list(self, callback):
        def success(reply):
            json = reply.json()
            return callback(json['tournaments'])

        self._async_request('get', self._base_address + 'tournaments',
                            callback=success)

    def get_tournament(self, tid, callback):
        if tid is None:
            return

        def success(reply):
            json = reply.json()
            return callback(json['tournament'])

        self._async_request('get', self._base_address + 'tournaments/' + str(tid),
                            callback=success)

    def get_game_list(self, tid, callback):
        if tid is None:
            return

        def success(reply):
            json = reply.json()
            return callback(json['games'])

        self._async_request('get', self._base_address + 'tournaments/' + str(tid) + '/games',
                            callback=success)

    def get_game(self, tid, gid, callback):
        if tid is None or gid is None:
            return

        def success(reply):
            json = reply.json()
            return callback(json['game'])

        self._async_request('get', self._base_address + 'tournaments/' + str(tid) + '/games/' + str(gid),
                            callback=success)

    def get_team_list(self, tid, callback):
        if tid is None:
            return

        def success(reply):
            json = reply.json()
            return callback(json['teams'])

        self._async_request('get', self._base_address + 'tournaments/' + str(tid) + '/teams',
                            callback=success)

    def get_team(self, tid, team_id, callback):
        if tid is None or team_id is None:
            return

        def success(reply):
            json = reply.json()
            return callback(json['team'])

        self._async_request('get', self._base_address + 'tournaments/' + str(tid) + '/teams/' + str(team_id),
                            callback=success)

    def get_team_flag(self, tid, team_id, callback):
        if tid is None or team_id is None:
            return

        def success(team):
            flag_url = team['flag_url']

            if not flag_url:
                callback(None)
                return

            @lru_cache(maxsize=16)
            def fetch_flag(url):
                callback(Image.open(requests.get(url, stream=True).raw))

            fetch_flag(flag_url)

        self.get_team(tid, team_id, success)

    #def get_standings(self, tid, callback):
    #    def success(reply):
    #        json = reply.json()
    #        return callback(json['standings'])
    #
    #    self._async_request('get', self._base_address + 'tournaments/' + str(tid) + '/standings',
    #                        callback=success)

    def get_roster(self, tid, team_id, callback):
        if tid is None or team_id is None:
            return

        def success(reply):
            json = reply.json()
            callback(json['team']['roster'])

        self._async_request('get', self._base_address + 'tournaments/' + str(tid) + '/teams/' + str(team_id),
                            callback=success)

    def _mock_data(self):
        return { 'api' : { 'v1' : {
            'tournaments' : {
                0 : { 'tid' : 0 },
                1 : { 'tid' : 1 },
                2 : { 'tid' : 2 },
                3 : { 'tid' : 3 },
                4 : { 'tid' : 4 },
                5 : { 'tid' : 5 },
                6 : { 'tid' : 6 },
                7 : { 'tid' : 7 },
                8 : { 'tid' : 8 },
                9 : { 'tid' : 9 },
                10 : { 'tid' : 10 },
                11 : { 'tid' : 11 },
                12 : {
                    'mock_name' : 'tournament',
                    'tid' : 12,
                    'standings' : {
                        0 : {
                            'team' : 'Team Sexy',
                            'team_id' : 2,
                            'stats' : {
                                'points' : 27
                            },
                        },
                        2 : {
                            'team' : 'UF',
                        },
                        4 : {
                            'team' : 'Hampton'
                        },
                        6 : {
                            'team' : 'Swordfish'
                        },
                        7 : {
                            'team' : 'George Mason'
                        }
                    }
                },
                13 : { 'tid' : 13 },
                14 : {
                    'mock_name' : 'tournament',
                    'tid' : 14,
                    'name' : 'Battle@Altitude 2018',
                    'location' : 'Denver, CO',
                    'is_active' : False,
                    'games' : {
                        1 : {
                            'black' : 'LA',
                            'black_id' : 1,
                            'pool' : '1',
                        },
                        4 : {
                            'white' : 'Seattle',
                            'white_id' : 6,
                            'start_time' : '2018-01-27T09:02:00',
                        },
                        6 : {
                            'black' : 'U19 Girls',
                            'black_id' : 14,
                            'day' : 'Sat',
                            'start_time' : '2018-01-27T09:34:00',
                            'white' : 'US Elite Women',
                            'white_id' : 17,
                        }
                    },
                    'teams' : {
                        1 : { 'name' : 'LA' },
                        3 : { 'name' : 'Rainbow Raptors' },
                        7 : { 'name' : 'Cupcake Crocodiles' },
                        11 : { 'name' : 'Chicago' },
                        13 : { 'name' : 'Colorado B' },
                        17 : { 'name' : 'US Elite Women' },
                    }
                },
                15 : {
                    'mock_name' : 'tournament',
                    'tid' : 15,
                    'name' : '2018 Worlds Mockup',
                    'location' : 'Quebec City, Canada',
                    'is_active' : True,
                    'games' : {
                        1 : {
                            'mock_name' : 'game',
                            'black' : 'Argentina',
                            'black_id' : 1,
                            'pool' : 1,
                            'white' : 'Australia',
                            'white_id' : 2,
                            'start_time' : '2018-07-18T07:40:00'
                        },
                        2 : {
                            'mock_name' : 'game',
                            'black' : 'USA',
                            'black_id' : 3,
                            'pool' : 2,
                            'white' : 'Columbia',
                            'white_id' : 4,
                            'start_time' : '2018-07-18T07:40:00'
                        }
                    },
                    'teams' : {
                        1 : {
                            'mock_name' : 'team',
                            'name' : 'Argentina Masters Men',
                            'team_id' : 1,
                            'roster' : {
                                1 : {
                                    'player_id' : 1,
                                    'name' : 'Schmoe, Joe',
                                },
                                2 : {
                                    'player_id' : 2,
                                    'name' : 'Doe, John'
                                },
                                3 : {
                                    'player_id' : 3,
                                    'name' : 'Bobby, Ricky'
                                },
                                4 : {
                                    'player_id' : 4,
                                    'name' : 'Georgeson, George'
                                },
                                5 : {
                                    'player_id' : 5,
                                    'name' : 'Steveson, Steve'
                                },
                                6 : {
                                    'player_id' : 6,
                                    'name' : 'Justinson, Justin'
                                },
                                7 : {
                                    'player_id' : 7,
                                    'name' : 'Pauly, Paul'
                                },
                                8 : {
                                    'player_id' : 8,
                                    'name' : 'Everett, Earnest'
                                },
                                9 : {
                                    'player_id' : 9,
                                    'name' : 'Clumboldt, Cletus'
                                },
                                10 : {
                                    'player_id' : 10,
                                    'name' : 'Miller, Milhouse'
                                },
                                11 : {
                                    'player_id' : 11,
                                    'name' : 'Thompson, Tucker'
                                },
                                12 : {
                                    'player_id' : 12,
                                    'name' : 'Richardson, Rich'
                                }
                            }
                        },
                        2 : {
                            'mock_name' : 'team',
                            'name' : 'Australia Masters Men',
                            'team_id' : 2,
                            'roster' : {
                                1 : {
                                    'player_id' : 1,
                                    'name' : 'Speedwagon, Mario',
                                },
                                2 : {
                                    'player_id' : 2,
                                    'name' : 'Romer, Robby'
                                },
                                3 : {
                                    'player_id' : 3,
                                    'name' : 'Riker, Randolph'
                                },
                                4 : {
                                    'player_id' : 4,
                                    'name' : 'Tomlin, Teddy'
                                },
                                5 : {
                                    'player_id' : 5,
                                    'name' : 'Wolf, Warren'
                                },
                                6 : {
                                    'player_id' : 6,
                                    'name' : 'Pollard, Phillip'
                                },
                                7 : {
                                    'player_id' : 7,
                                    'name' : 'Bavaro, Buster'
                                },
                                8 : {
                                    'player_id' : 8,
                                    'name' : 'James, Joshua'
                                },
                                9 : {
                                    'player_id' : 9,
                                    'name' : 'Shin, Stewart'
                                },
                                10 : {
                                    'player_id' : 10,
                                    'name' : 'Hume, Huey'
                                },
                                11 : {
                                    'player_id' : 11,
                                    'name' : 'Vos, Valentine'
                                },
                                12 : {
                                    'player_id' : 12,
                                    'name' : 'Newburn, Noel'
                                }
                            }
                        },
                        3 : { 'name' : 'USA Masters Men', 'team_id' : 3 },
                        4 : { 'name' : 'Columbia Masters Men', 'team_id' : 4 },
                    }
                }
            }
        }}}

    def _mock_api(self, endpoint, cb_success, cb_fail):
        import urllib.parse
        import posixpath

        def path_parse(path_string):
            result = []
            tmp = posixpath.normpath(path_string)
            while tmp != "/":
                (tmp, item) = posixpath.split(tmp)
                result.insert(0, item)
            return result

        url_parsed = urllib.parse.urlparse( endpoint )
        path_parsed = path_parse(urllib.parse.unquote(url_parsed.path))

        try:
            mock = self._mock_data()

            for idx, item in enumerate(path_parsed):
                try:
                    item = int(item)
                except ValueError:
                    pass
                mock = mock[item]

            class Wrap(object):
                def __init__(self, wrap):
                    self._wrap = wrap

                def json(self):
                    return { self._wrap['mock_name'] : self._wrap }

            cb_success(Wrap(mock))
        except KeyError as e:
            print('mock lookup fail for: ' + endpoint)
            cb_fail(e)

    def set_fail_handler(self, callback):
        self._fail_handler = callback

    def _async_request(self, method, *args, callback,
                       callback_fail=None,
                       timeout=5, **kwargs):
        method = {
            'get' : requests.get,
            'post' : requests.post,
            'put' : requests.put,
            'patch' : requests.patch,
            'delete' : requests.delete,
            'options' : requests.options,
            'head' : requests.head
        }[method.lower()]

        callback_fail = callback_fail or self._fail_handler

        def wrap_method(*args, **kwargs):
            try:
                method(*args, **kwargs)
            except requests.exceptions.ConnectionError as e:
                callback_fail(e)
            except Exception as e:
                callback_fail(e)

        parent_args = args
        if callback:
            def callback_with_args(response, *args, **kwargs):
                try:
                    callback(response)
                except Exception as e:
                    callback_fail((parent_args[0], e))
            kwargs['hooks'] = {'response': callback_with_args}
        kwargs['timeout'] = timeout

        if self._mock:
            self._mock_api(args[0], callback, callback_fail)
        else:
            thread = threading.Thread(target=wrap_method, args=args, kwargs=kwargs)
            thread.start()
