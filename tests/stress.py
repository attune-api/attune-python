import json
import logging
import os
import sys
from datetime import datetime
from random import random, randint, choice
from threading import Thread, Lock
from time import sleep, time

import click
import coloredlogs as coloredlogs
from profilestats import profile

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from attune.client.model import RankingParams
from attune.client.client import Client
from attune.client.configuration import Settings

log = logging.getLogger('test')


class Test:
    def stats_increment(self, name, inc=1):
        self._lock.acquire()

        try:
            if name not in self.stats:
                self.stats[name] = 0

            self.stats[name] += inc
        finally:
            self._lock.release()

    def run(self):
        start = datetime.now()

        cfg = json.load(self.open_file('normalTestProd.conf'))

        configuration = Settings()
        configuration.host = cfg['serverUrl']
        configuration.debug = True

        configuration.http_pool_connections = 1000
        configuration.http_pool_size = 1000

        for k in configuration.threadpool_workers.keys():
            configuration.threadpool_workers[k] = 1000

        client = Client(configuration)

        log.info('Reading customers and entities ...')
        entities, customers = self.read_entities(cfg['entityFile']), self.read_customers(cfg['customerFile'])

        self.stats, self._lock = {}, Lock()

        log.info('Running %s customers threads' % cfg['concurrentCustomers'])
        threads = []
        for i in range(0, cfg['concurrentCustomers']):
            thread = Thread(target=self.worker, args=(i, client, cfg, entities, customers))
            thread.daemon = True
            thread.start()

            threads.append(thread)

        for th in threads:
            th.join()

        log.info('The test took %s' % (datetime.now() - start))

        log.info('Execution stats')
        for k, v in self.stats.items():
            log.info('    - %s: %s' % (k, v))

        if 'callTime' in self.stats and 'successfulCalls' in self.stats:
            log.info('    - Average time for request: %s' % (self.stats['callTime'] / self.stats['successfulCalls']))

        if 'successfulCalls' in self.stats:
            rps = self.stats['successfulCalls'] / (datetime.now() - start).total_seconds()
            log.info('    - Requests per second to attune.co %3.2f' % rps)

    def call_rank(self, client, cfg, aid, customer, entity):
        view, ids = json.loads(entity).popitem()

        p = RankingParams()
        p.anonymous = aid
        p.customer = customer
        p.view = view
        p.ids = ids
        p.application = cfg['application']
        p.entity_type = cfg['entityType']

        log.debug('Running client.get_rankings("%s", "%s", "%s", {...})' % (p.anonymous, p.customer, p.view))

        return client.get_rankings(p, oauth_token=cfg['authToken'])

    def worker(self, thread_id, client, cfg, entities, customers):
        end_time = time() + cfg['duration']

        alpha = 1 - 1. / cfg['avgNumCalls']

        while time() < end_time:
            while time() < end_time:
                gap = (0.2 + random()) * cfg['avgCallGap'] * 2
                log.debug('Sleeping %s' % gap)
                sleep(gap)

                self.stats_increment('totalCalls')

                try:
                    start = time()
                    try:
                        self.call_rank(client, cfg, randint(1000000, 10000000), choice(customers), choice(entities))

                        self.stats_increment('successfulCalls')
                    except Exception, e:
                        log.exception(e)
                        os._exit(-1)

                    self.stats_increment('callTime', time() - start)
                except Exception, e:
                    log.exception(e)

                if random() > alpha:
                    break

        log.debug('Exiting thread #%s' % thread_id)

    def open_file(self, filename):
        path = os.path.join(os.path.dirname(__file__), 'data', filename)
        if not os.path.isfile(path):
            log.error('Not found test data file %s' % path)
            raise click.Abort()

        return open(path)

    def read_entities(self, filename):
        return list(x.strip() for x in self.open_file(filename).readlines() if x.strip())

    def read_customers(self, filename):
        return list(x.strip() for x in self.open_file(filename).readlines() if x.strip())


@click.command()
@click.option('--profiling', '-P', help='Enable source code profiling', is_flag=True)
@click.option('--profiling-dump', '-D', help='Dump stats to files when profiling', is_flag=True)
@click.option('-v', '--verbose', help='Logging level. Can be used multiple times', count=True,
              type=click.IntRange(max=2, clamp=True))
def stress(profiling, profiling_dump, verbose):
    loglevel = {
        0: logging.INFO,
        1: logging.DEBUG
    }

    coloredlogs.install(level=loglevel.get(verbose, logging.INFO),
                        fmt='%(asctime)s.%(msecs)03d %(name)s[%(process)d] %(levelname)s %(message)s')

    test = Test()
    if profiling:
        profile(print_stats=25, dump_stats=profiling_dump)(test.run)()
    else:
        test.run()


if __name__ == '__main__':
    stress()
