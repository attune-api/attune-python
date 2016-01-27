import unittest
from datetime import datetime
from time import sleep

from pybreaker import CircuitBreakerError

from attune.client.commands import BaseCommand
from attune.client.model import Customer, RankingParams, ScopeEntry
from attune.client.rest import ApiException


class TestApi(unittest.TestCase):
    with_default_id_list = ['1001', '1002', '1003', '1004']

    @classmethod
    def setUpClass(cls):
        from attune.client.client import Client
        from attune.client.configuration import Configuration

        cls.config = Configuration()
        cls.config.debug = False
        cls.config.host = 'https://api-test.attune.co/'

        cls.oauth_token = "a12a4e7a-b359-4c4f-aced-582673f2a6d9"

        cls.client = Client(cls.config)

    def on_async_callback(self, result, callback=None):
        self.assertIsNotNone(result)

        if callback:
            callback(result)

    def wait_running_future(self, future):
        while future.running():
            sleep(0.05)

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
        self.client.update_fallback_to_default(True)
        future = self.client.get_auth_token(
                'veu2n74k01', '4ed3df60fc9d11e3a3ac0800200c9a66',
                callback=lambda x: self.on_async_callback(x, lambda z: self.assertIn('access_token', z))
        )
        self.wait_running_future(future)

    def test_create_anonymous(self):
        """
        Test a anonymous get request
        """

        self.assertIsNotNone(self.client.create_anonymous(oauth_token=self.oauth_token))

    def test_create_anonymous_async(self):
        """
        Test a anonymous get request (async)
        """

        future = self.client.create_anonymous(oauth_token=self.oauth_token, callback=self.on_async_callback)
        self.wait_running_future(future)

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

            future = self.client.bind(anonymous, customer.customer, oauth_token=self.oauth_token,
                                      callback=self.on_async_callback)
            self.wait_running_future(future)

        future = self.client.create_anonymous(oauth_token=self.oauth_token, callback=on_anon)
        self.wait_running_future(future)

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

                future = self.client.get_bound_customer(anonymous.id, oauth_token=token,
                                                        callback=self.on_async_callback)
                self.wait_running_future(future)

            future = self.client.create_anonymous(oauth_token=token, callback=on_anon)
            self.wait_running_future(future)

        future = self.client.get_auth_token("attune", "a433de60fe2311e3a3ac0800200c9a66", callback=on_token)
        self.wait_running_future(future)

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

            future = self.client.get_bound_customer('12345', oauth_token=self.oauth_token, callback=on_get)
            self.wait_running_future(future)

        customer = Customer()
        customer.customer = 'pytest-customer'

        future = self.client.bind('12345', customer.customer, oauth_token=self.oauth_token, callback=on_bind)
        self.wait_running_future(future)

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

        self.client.update_fallback_to_default(True)

        defaultList = self.client.get_rankings(params, oauth_token=self.oauth_token)
        self.assertEqual(self.with_default_id_list[0], defaultList.ranking[0])

    def test_scope_get_rankings_404(self):
        with self.assertRaises(ApiException) as x:
            self.make_scope_ranking_call('1007', self.with_default_id_list)

        self.assertEqual(x.exception.status, 404)
        self.assertIn('Cannot find ranking data', x.exception.body)

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

        return self.client.get_rankings(rankingParams, oauth_token=self.oauth_token)

    def test_commands_fallback(self):
        class Test(BaseCommand):
            def run(self): raise RuntimeError

            def fallback(self): return 'It works!'

        self.client.update_fallback_to_default(False)
        with self.assertRaises(RuntimeError):
            self.client.run(Test(self.client))

        self.client.update_fallback_to_default(True)

        self.assertEqual(self.client.config.commands_fallback, True)
        self.assertEqual('It works!', self.client.run(Test(self.client)))

        self.client.update_fallback_to_default(False)
        with self.assertRaises(RuntimeError):
            self.client.run(Test(self.client))

    def test_circuit_breaker(self):
        class Test(BaseCommand):
            def run(self):
                raise RuntimeError()

            def fallback(self):
                return True

        self.client.update_fallback_to_default(False)

        cmd = Test(self.client)

        for i in range(1, cmd.breaker.fail_max):
            with self.assertRaises(RuntimeError):
                self.client.run(cmd)

        for i in range(1, 100):
            with self.assertRaises(CircuitBreakerError):
                self.client.run(cmd)

        cmd.breaker.close()

        for i in range(1, cmd.breaker.fail_max - 1):
            with self.assertRaises(RuntimeError):
                self.client.run(cmd)

        self.client.update_fallback_to_default(True)

        self.assertEqual(True, self.client.run(cmd))
