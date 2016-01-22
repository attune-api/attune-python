import unittest

from requests.exceptions import ConnectTimeout, ConnectionError


class TestApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from attune.client.client import Client
        from attune.client.configuration import Configuration

        cls.config = Configuration()
        cls.config.host = 'https://api-test.attune.co/'

        cls.client = Client(cls.config)

        cls.auth_token_args = ('veu2n74k01', '4ed3df60fc9d11e3a3ac0800200c9a66')

    def pool_close(self):
        def wrapper(func, *args, **kwargs):
            func(*args, **kwargs)

            self.client.rest_client.pool_manager.close()

        return wrapper

    def test_connect_timeout(self):
        old = self.config.http_timeout_connect
        self.config.http_timeout_connect = 0.001
        # self.config.http_timeout_read = 0.001

        # self.client.get_auth_token(*self.auth_token_args)

        with self.assertRaises(ConnectTimeout):
            self.client.get_auth_token(*self.auth_token_args)

        self.config.http_timeout_connect = old

    def test_read_timeout(self):
        old = self.config.http_timeout_read

        self.config.http_timeout_read = 0.0001
        with self.assertRaises(ConnectionError):
            self.client.get_auth_token(*self.auth_token_args)

        self.config.http_timeout_read = old

    def test_user_agent(self):
        self.client.get_auth_token(*self.auth_token_args)
        self.assertEqual(self.client.last_response.urllib3_response.request.headers['User-Agent'],
                         self.client.user_agent)

    @self.pool_close
    def test_compression(self):
        self.client.get_auth_token(*self.auth_token_args)

        self.pool_close()
