import unittest
from datetime import datetime

from attune.client.model import Customer, RankingParams, ScopeEntry


class TestApi(unittest.TestCase):
    with_default_id_list = ['1001', '1002', '1003', '1004']

    @classmethod
    def setUpClass(cls):
        from attune.client.client import Client
        from attune.client.configuration import Configuration

        cls.config = Configuration()
        cls.config.host = 'https://api-test.attune.co/'

        cls.oauth_token = "a12a4e7a-b359-4c4f-aced-582673f2a6d9"

        cls.client = Client(cls.config)

    def on_async_callback(self, result, callback=None):
        self.assertIsNotNone(result)

        if callback:
            callback(result)

    def test_api_initialized(self):
        """
        Check for non error initialization of config and client
        """

        self.assertIsNotNone(self.config)
        self.assertIsNotNone(self.client)

    def test_auth_get_token(self):
        """
        Get auth token
        """

        token = self.client.get_auth_token('veu2n74k01', '4ed3df60fc9d11e3a3ac0800200c9a66')

        self.assertIsNotNone(token)
        self.assertIn('access_token', token)

    def test_auth_get_token_async(self):
        """
        Get auth token (async)
        """

        # force wait for end of async call
        self.client.get_auth_token(
                'veu2n74k01', '4ed3df60fc9d11e3a3ac0800200c9a66',
                callback=lambda x: self.on_async_callback(x, lambda z: self.assertIn('access_token', z))
        ).join()

    def test_create_anonymous(self):
        """
        Test a anonymous get request
        """

        self.assertIsNotNone(self.client.create_anonymous(oauth_token=self.oauth_token))

    def test_create_anonymous_async(self):
        """
        Test a anonymous get request (async)
        """

        self.client.create_anonymous(oauth_token=self.oauth_token, callback=self.on_async_callback).join()

    def test_bind(self):
        """
        Test a binding call request
        """

        anonymous = self.client.create_anonymous(oauth_token=self.oauth_token)
        self.assertIsNotNone(anonymous)

        customer = Customer()
        customer.customer = 'py-unittest-customer-%s' % datetime.now()

        self.assertIsNotNone(self.client.bind(anonymous, customer.customer, oauth_token=self.oauth_token))

    def test_bind_async(self):
        """
        Test a binding call request (async)
        """

        def on_anon(anonymous):
            self.assertIsNotNone(anonymous)

            customer = Customer()
            customer.customer = 'py-unittest-customer-%s' % datetime.now()

            self.client.bind(anonymous, customer.customer, oauth_token=self.oauth_token,
                             callback=self.on_async_callback).join()

        self.client.create_anonymous(oauth_token=self.oauth_token, callback=on_anon).join()

    def test_get_bound_customer(self):
        """
        Get customer id bound to an anonymous id
        """

        token = self.client.get_auth_token("attune", "a433de60fe2311e3a3ac0800200c9a66")
        self.assertIsNotNone(token)

        token = token['access_token']

        anonymous = self.client.create_anonymous(oauth_token=token)
        self.assertIsNotNone(anonymous)

        customer = self.client.get_bound_customer(anonymous.id, oauth_token=token)
        self.assertIsNotNone(customer)

    def test_get_bound_customer_async(self):
        """
        Get customer id bound to an anonymous id (async)
        """

        def on_token(token):
            self.assertIsNotNone(token)

            token = token['access_token']

            def on_anon(anonymous):
                self.assertIsNotNone(anonymous)

                self.client.get_bound_customer(anonymous.id, oauth_token=token, callback=self.on_async_callback).join()

            self.client.create_anonymous(oauth_token=token, callback=on_anon).join()

        self.client.get_auth_token("attune", "a433de60fe2311e3a3ac0800200c9a66", callback=on_token).join()

    def test_bound_to_correct_customer(self):
        """
        Verify that the bind happened correctly between anonymousId and customer
        """

        customer = Customer()
        customer.customer = 'pytest-customer'
        self.client.bind('12345', customer.customer, oauth_token=self.oauth_token)

        result_customer = self.client.get_bound_customer('12345', oauth_token=self.oauth_token)
        self.assertIsNotNone(result_customer)

        self.assertEqual(customer.customer, result_customer.customer)

    def test_bound_to_correct_customer_async(self):
        """
        Verify that the bind happened correctly between anonymousId and customer (async)
        """

        def on_bind(result):
            def on_get(result_customer):
                self.assertIsNotNone(result_customer)

                self.assertEqual(customer.customer, result_customer.customer)

            self.client.get_bound_customer('12345', oauth_token=self.oauth_token, callback=on_get).join()

        customer = Customer()
        customer.customer = 'pytest-customer'
        self.client.bind('12345', customer.customer, oauth_token=self.oauth_token, callback=on_bind).join()

    def test_get_rankings(self):
        """
        Verify that the rankings returned on a get call happened correctly and the size of the
        list matches the list supplied in the params
        """

        anonymous = self.client.create_anonymous(oauth_token=self.oauth_token)
        self.assertIsNotNone(anonymous)

        params = RankingParams()
        params.anonymous = "an-anon-id"
        params.view = "b/mens-pants"
        params.entity_type = "products"
        params.ids = self.with_default_id_list

        rankings = self.client.get_rankings(params, oauth_token=self.oauth_token)

        self.assertEqual(len(rankings.ranking), len(params.ids))

        # client.updateFallBackToDefault(true);
        # RankedEntities defaultList = client.getRankings(rankingParams, authToken);
        #
        # assertTrue(idList.get(0).equals(defaultList.getRanking().get(0)));
        # System.out.println("PASS: first entry of default (fallback mode on) results matches to those received in the request");

    def test_get_rankings_async(self):
        # TODO: implement
        pass

    def test_scope_get_rankings_404(self):
        self.make_scope_ranking_call('1007', self.with_default_id_list)

    def test_scope_get_rankings_ok(self):
        self.assertIsNotNone(self.make_scope_ranking_call('59784', self.with_default_id_list))

    def make_scope_ranking_call(self, sale_id, id_list):
        rankingParams = RankingParams()
        rankingParams.anonymous = 'some-anon-id'
        rankingParams.view = "/sales/" + sale_id
        rankingParams.entity_source = "scope"

        def entry(name, value):
            item = ScopeEntry()
            item.name = name
            item.value = value

            return item

        rankingParams.scope = [
            entry('sale', sale_id),
            entry('color', 'red'),
            entry('size', 'M')
        ]

        rankingParams.entity_type = "products"
        rankingParams.application = "mobile_event_page"
        rankingParams.ids = []

        return self.client.get_rankings(rankingParams, oauth_token=self.oauth_token)
