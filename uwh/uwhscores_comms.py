import requests
import threading

class UWHScores(object):
    def __init__(self, base_address='https://uwhscores.com/api/v1/', mock=False):
        self._base_address = base_address
        self._mock = mock

    def get_tournament_list(self, callback):
        def success(reply):
            json = reply.json()
            return callback({json[i]['tid']: json[i]
                             for i in range(len(json))})

        self._async_request('get', self._base_address + 'tournaments',
                            callback=success)

    def get_tournament(self, tid, callback):
        def success(reply):
            json = reply.json()
            return callback(json)

        self._async_request('get', self._base_address + 'tournaments/' + str(tid),
                            callback=success)

    def get_game_list(self, tid, callback):
        def success(reply):
            json = reply.json()
            return callback(json)

        self._async_request('get', self._base_address + 'tournaments/' + str(tid) + '/games',
                            callback=success)

    def get_game(self, tid, gid, callback):
        def success(reply):
            json = reply.json()
            return callback(json)

        self._async_request('get', self._base_address + 'tournaments/' + str(tid) + '/games/' + str(gid),
                            callback=success)

    def get_team_list(self, tid, callback):
        def success(reply):
            json = reply.json()
            return callback(json)

        self._async_request('get', self._base_address + 'tournaments/' + str(tid) + '/teams',
                            callback=success)

    def get_standings(self, tid, callback):
        def success(reply):
            json = reply.json()
            from pprint import pprint
            pprint(json)
            return callback(json)

        self._async_request('get', self._base_address + 'tournaments/' + str(tid) + '/standings',
                            callback=success)

    def _mock_api(self, endpoint, cb_success, cb_fail):
        mock = { 'api' : { 'v1' : {
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
                    'tid' : 15,
                    'name' : '2018 Worlds Mockup',
                    'location' : 'Quebec',
                    'is_active' : True,
                    'games' : {
                        1 : {
                            'black' : 'Argentina Masters Men',
                            'black_id' : 1,
                            'pool' : 1,
                            'white' : 'Australia Masters Men',
                            'white_id' : 2,
                            'start_time' : '2018-07-18T07:40:00'
                        },
                        2 : {
                            'black' : 'USA Masters Men',
                            'black_id' : 3,
                            'pool' : 2,
                            'white' : 'Columbia Masters Men',
                            'white_id' : 4,
                            'start_time' : '2018-07-18T07:40:00'
                        }
                    },
                    'teams' : {
                        1 : { 'name' : 'Argentina Masters Men', 'team_id' : 1 },
                        2 : { 'name' : 'Australia Masters Men', 'team_id' : 2 },
                        3 : { 'name' : 'USA Masters Men', 'team_id' : 3 },
                        4 : { 'name' : 'Columbia Masters Men', 'team_id' : 4 },
                    }
                }
            }
        }}}

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
                return self._wrap

        cb_success(Wrap(mock))

    def _async_request(self, method, *args, callback,
                       callback_fail=lambda _ : None,
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

        def wrap_method(*args, **kwargs):
            try:
                method(*args, **kwargs)
            except requests.exceptions.ConnectionError as e:
                callback_fail(e)

        if callback:
            def callback_with_args(response, *args, **kwargs):
                callback(response)
            kwargs['hooks'] = {'response': callback_with_args}
        kwargs['timeout'] = timeout

        if self._mock:
            self._mock_api(args[0], callback, callback_fail)
        else:
            thread = threading.Thread(target=wrap_method, args=args, kwargs=kwargs)
            thread.start()
