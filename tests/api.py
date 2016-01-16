import unittest


class TestApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.auth_token = 'a12a4e7a-b359-4c4f-aced-582673f2a6d9'

        from attune.client.client import Client
        from attune.client.configuration import Configuration

        cls.config = Configuration()
        cls.config.host = 'https://api-test.attune.co/'

        cls.client = Client()

    def test_api_initialized(self):
        self.assertIsNotNone(self.config)
        self.assertIsNotNone(self.client)

    def test_auth_get_token_async(self):
        def test(token):
            self.assertIsNotNone(token)
            self.assertIn('access_token', token)

        token = self.client.get_auth_token('veu2n74k01', '4ed3df60fc9d11e3a3ac0800200c9a66', callback=test)

        # force wait for end of async call
        token.join()

    def test_auth_get_token(self):
        token = self.client.get_auth_token('veu2n74k01', '4ed3df60fc9d11e3a3ac0800200c9a66')

        self.assertIsNotNone(token)
        self.assertIn('access_token', token)

        self.client.config.access_token = token['access_token']

    def test_create_anonymous(self):
        self.assertIsNotNone(self.client.api.create())
