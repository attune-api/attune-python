import unittest

from requests.exceptions import RetryError

from attune.client.client import Client
from tests.utils import Server


class TestRetries(unittest.TestCase):
    server = None

    @classmethod
    def setUpClass(cls):
        cls.server = Server()
        cls.server.run()
        cls.base_url = 'http://127.0.0.1:%s%%s' % cls.server.port

        cls.client = Client()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_ping_server(self):
        result = self.client.rest_client.GET(self.base_url % '/ping')

        self.assertIsNotNone(result)
        self.assertEqual(result.data, 'It works!')

    def test_500_error_retries(self):
        self.server.reset_errors_count()

        try:
            self.client.rest_client.GET(self.base_url % ('/error/%s' % range(500, 600)))
        except RetryError:
            self.assertEqual(self.client.config.http_max_retries + 1, self.server.errors_count)
