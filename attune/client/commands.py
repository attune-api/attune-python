import logging
import threading

from concurrent.futures import ThreadPoolExecutor
from pybreaker import CircuitBreaker

from attune.client.model import RankedEntities

_lock = threading.RLock()
_executors = {}
_breakers = {}

log = logging.getLogger(__name__)


class NonBlockingBreaker(CircuitBreaker):
    def call(self, func, *args, **kwargs):
        return self._state.call(func, *args, **kwargs)


class BaseCommand(object):
    def __init__(self, client, args=None, kwargs=None, timeout=None, oauth_token=None):
        self.timeout = timeout

        self.client = client

        self.kwargs = kwargs or {}
        self.args = args or tuple()

        self.executor = self.get_executor()
        self.breaker = self.get_breaker()
        if oauth_token:
            self.kwargs['oauth_token'] = oauth_token

    def get_executor(self):
        with _lock:
            key = self.__class__.__name__.lower()

            if not key in _executors:
                workers = self.client.config.threadpool_workers.get(key, self.client.config.threadpool_workers_default)

                _executors[key] = ThreadPoolExecutor(workers)

            return _executors[key]

    def get_breaker(self):
        with _lock:
            key = self.__class__.__name__.lower()

            if not key in _breakers:
                settings = self.client.config.circuit_breaker.get(key, self.client.config.circuit_breaker_default)

                # we add +1 to leave settings clean because they uses "< fail_max"
                _breakers[key] = NonBlockingBreaker(fail_max=settings[0] + 1, reset_timeout=settings[1])

            return _breakers[key]

    def command(self):
        raise NotImplementedError

    def fallback(self):
        raise NotImplementedError

    def run(self):
        return self.command()(*self.args, **self.kwargs)

    def _run_with_fallback(self):
        try:
            return self.breaker.call(self.run)
        except Exception, e:
            error = e

            log.warn('exception calling run for {}'.format(self))
            log.info('run raises {}'.format(e))

        if self.client.config.commands_fallback:
            try:
                log.info('trying fallback for {}'.format(self))

                return self.fallback()
            except Exception, e:
                if not isinstance(e, NotImplementedError): error = e

                log.warn('exception calling fallback for {}'.format(self))
                log.info('run() raised {}'.format(e))

        raise error

    def execute(self, timeout=None, callback=None):
        timeout = timeout or self.timeout

        future = self.executor.submit(self._run_with_fallback)
        if callback:
            future.add_done_callback(lambda x: callback(x.result()))

            return future
        else:
            return future.result(timeout)


class GetAuthToken(BaseCommand):
    def run(self):
        """
        Returns auth token for given client_id and client_secret
        :param callback function: The callback function
            for asynchronous request. (optional)
        :return: BatchRankingResult
                 If the method is called asynchronously,
                 returns the request thread.
        """
        client_id, client_secret, = self.args

        if client_id is None:
            raise ValueError("Missing the required parameter `client_id` when calling `get_auth_token`")

        if client_secret is None:
            raise ValueError("Missing the required parameter `client_secret` when calling `get_auth_token`")

        resource_path = '/oauth/token'

        form_params = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'
        }

        header_params = {
            'Content-Type': self.client.select_header_content_type(['application/x-www-form-urlencoded'])
        }

        response = self.client.call_api(resource_path, 'POST',
                                        post_params=form_params,
                                        response_type='object',
                                        header_params=header_params)
        return response


class Bind(BaseCommand):
    def command(self):
        return self.client.api.update


class CreateAnonymous(BaseCommand):
    def command(self):
        return self.client.api.create


class BoundCustomer(BaseCommand):
    def command(self):
        return self.client.api.get


class GetRankingsGET(BaseCommand):
    def command(self):
        def _get_rankings_get(params, **kwargs):
            resource_path = '/entities/ranking'.replace('{format}', 'json')

            if params.entity_source.upper() == 'SCOPE':
                params.scope = list('%s=%s' % (x.name, x.value) for x in params.scope or [])

                params.ids = None

            header_params = {
                'Content-Type': self.client.select_header_content_type([])
            }

            return self.client.call_api(resource_path, 'GET',
                                        query_params=params,
                                        header_params=header_params,
                                        response_type='RankedEntities',
                                        callback=kwargs.get('callback'),
                                        oauth_token=kwargs.get('oauth_token'))

        return _get_rankings_get


class GetRankingsPOST(BaseCommand):
    def command(self):
        return self.client.api.get_rankings

    def fallback(self):
        entities = RankedEntities()
        entities.ranking = self.args[0].ids

        return entities
