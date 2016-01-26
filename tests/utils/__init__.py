from random import randint
from threading import Thread
from time import sleep

from bottle import Bottle, ServerAdapter, abort


class WSGIRefServer(ServerAdapter):
    server = None
    quiet = True

    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass

            self.options['handler_class'] = QuietHandler
        self.server = make_server(self.host, self.port, handler, **self.options)
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()


class Server(object):
    def __init__(self):
        self.web = Bottle()
        self.port = randint(55000, 60000)
        self.server = WSGIRefServer(port=self.port)

        self.inited = False

        self.errors_count = 0

        self.init_app()

    def reset_errors_count(self):
        self.errors_count = 0

    def init_app(self):
        if self.inited: return

        self.inited = True

        app = self.web

        @app.route('/ping')
        def index(*args, **kwargs):
            return 'It works!'

        @app.route('/error/<code>', method=['GET', 'HEAD', 'DELETE', 'POST', 'PUT', 'PATCH', 'OPTIONS'])
        def error(code):
            self.errors_count += 1

            try:
                code = int(code)
            except ValueError:
                code = 500

            abort(code, '%s error as requested' % code)

    def run(self):
        self.thread = Thread(target=lambda: self.web.run(server=self.server))
        self.thread.start()

        sleep(0.3)

    def stop(self):
        self.server.stop()

        self.thread.join()
