from base64 import urlsafe_b64encode
from binascii import unhexlify
from .crypto import decrypt_response_data, encrypt_request_data
from requests import post
from .steam import steam_login

class Strive(object):
    def __init__(self, steam_id=None, token=None):
        self.steam_id = steam_id
        self.token = token
        self.steam_hex = None

        if steam_id:
            self.steam_hex = hex(steam_id)[:2]

        self.game_tokens = []

    def login(self, user, password, auth=None, padding=0):
        if not auth:
            auth = steam_login(user, password)

        self.steam_id = auth['id']
        self.steam_hex = hex(self.steam_id)[:2]
        print(auth)

        msg = [
            [
                "",
                "",
                2,
                "0.1.7",
                3
            ],
            [
                1,
                self.steam_id,
                self.steam_hex,
                256,
                auth['token']
            ]
        ]

        encrypted = encrypt_request_data(msg)

        r = post(
            r'https://ggst-game.guiltygear.com/api/user/login',
            headers={
                'Cache-Control': r'no-store',
                'Content-Type': r'application/x-www-form-urlencoded',
                'User-Agent': r'GGST/Steam',
                'x-client-version': r'1',
                'authority': 'ggst-game.guiltygear.com'
            },
            data={
                'data': encrypted if padding >= 0 else encrypted[:padding]
            },
        )

        try:
            login_response = decrypt_response_data(r.content.hex())
            print(login_response)
        except:
            return self.login(user, password, auth, padding - 2)

        self.token = login_response[0][0]
        print(f"Strive token obtained for user: {self.steam_id} - {self.token}")

    def get_replays(self):
        data_header = [
            "210611080230642425",
            self.token,
            2,
            "0.1.7",
            3
        ]
        data_params = [
            1,
            0,
            10,
            [
                -1,
                0,
                1,
                99,
                [],
                -1,
                -1,
                0,
                0,
                1
            ],
            6  # all platforms? (3 = PC?)
        ]
        msg = [data_header, data_params]
        return self._post_api("catalog/get_replay", msg)

    def _post_api(self, endpoint, msg):
        r = post(
            f'https://ggst-game.guiltygear.com/api/{endpoint}',
            headers={
                'Cache-Control': r'no-store',
                'Content-Type': r'application/x-www-form-urlencoded',
                'User-Agent': r'GGST/Steam',
                'x-client-version': r'1',
            },
            data={
                'data': encrypt_request_data(msg)
            },
        )

        content = r.content
        return decrypt_response_data(content.hex())