import logging
import argparse
from aiohttp import web
from aiopg.sa import create_engine
from cvs.tools import proxy_pass_middleware
from cvs.server import api, signal

routes = web.RouteTableDef()


@routes.get('/state')
async def get_status(request: web.Request):
    app = request.app  # type: WebApplication
    return web.json_response({
        **app.state,
        'status': 'OK'
    })


class WebApplication(web.Application):
    """ CVS Server
    """

    def __init__(self, db, **kwargs):
        api_uri = kwargs.pop('api_uri', None)
        signal_uri = kwargs.pop('signal_uri', None)
        janus_url = kwargs.pop('janus_url', None)
        middlewares = kwargs.pop('middlewares', [])
        proxy_pass = kwargs.pop('proxy_pass', None)
        if proxy_pass:
            middlewares.append(lambda request, handler: proxy_pass_middleware(request, handler, proxy_pass))
        super().__init__(middlewares=middlewares, **kwargs)
        self.db = db
        self.__state = dict()
        if isinstance(api_uri, str):
            self.add_subapp(api_uri, api.WebApplication(self.db, **kwargs))
            self.__state['api_uri'] = api_uri
        if isinstance(signal_uri, str) and isinstance(janus_url, str):
            self.add_subapp(signal_uri, signal.WebApplication(self.db, janus_url, **kwargs))
            self.__state['signal_uri'] = signal_uri
            self.__state['janus_url'] = janus_url
        self.add_routes(routes)

    @property
    def state(self):
        return dict((k, v) for k, v in self.__state.items())

    @classmethod
    async def factory(cls, options: argparse.Namespace):
        logging.basicConfig(level=(logging.DEBUG if options.debug else logging.WARNING))
        kwargs = dict((key, value) for key, value in options.__dict__.items() if
                      key in ('api_uri', 'signal_uri', 'janus_url', 'proxy_pass', 'postgres_url'))
        db_engine = await create_engine(kwargs.pop('postgres_url'))
        return cls(db_engine, logger=logging.root, **kwargs)
