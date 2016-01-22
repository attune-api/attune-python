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
        """
        Close pool to test connect timeout and read timeout settings.
        """
        self.client.rest_client.pool_manager.close()

    def test_connect_timeout(self):
        old = self.config.http_timeout_connect

        self.config.http_timeout_connect = 0.001
        with self.assertRaises(ConnectTimeout):
            self.client.get_auth_token(*self.auth_token_args)

        self.config.http_timeout_connect = old

        self.pool_close()

    def test_read_timeout(self):
        old = self.config.http_timeout_read

        self.config.http_timeout_read = 0.0001
        with self.assertRaises(ConnectionError):
            self.client.get_auth_token(*self.auth_token_args)

        self.config.http_timeout_read = old

        self.pool_close()

    def test_user_agent(self):
        if not hasattr(self.client, 'last_response'):
            self.client.get_auth_token(*self.auth_token_args)

        self.assertEqual(self.client.last_response.urllib3_response.request.headers['User-Agent'],
                         self.client.user_agent)

        self.pool_close()

    def test_compression(self):
        if not hasattr(self.client, 'last_response'):
            self.client.get_auth_token(*self.auth_token_args)

        resp = self.client.last_response.urllib3_response

        self.assertIn('gzip', (resp.request.headers['Accept-Encoding'] or "").lower())
        self.assertIn('gzip', (resp.headers['Content-Encoding'] or "").lower())

        self.pool_close()
