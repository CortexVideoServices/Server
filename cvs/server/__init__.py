import logging
import argparse
from aiohttp import web
from cvs.tools import proxy_pass_middleware
from cvs.server import api, signal

routes = web.RouteTableDef()


@routes.get('/state')
async def get_status(request: web.Request):
    app = request.app  # type: WebApplication
    return web.json_response({
        **app.settings,
        'status': 'OK'
    })


class WebApplication(web.Application):
    """ CVS Server
    """

    def __init__(self, **kwargs):
        self.settings = {
            'api_uri': kwargs.pop('api_uri', None),
            'signal_uri': kwargs.pop('signal_uri', None),
            'janus_url': kwargs.pop('janus_url', None)
        }
        middlewares = kwargs.pop('middlewares', [])
        proxy_pass = kwargs.pop('proxy_pass', None)
        if proxy_pass:
            middlewares.append(lambda request, handler: proxy_pass_middleware(request, handler, proxy_pass))
        super().__init__(middlewares=middlewares, **kwargs)
        if 'api_uri' in self.settings:
            self.add_subapp(self.settings['api_uri'], api.WebApplication(**kwargs))
        if 'signal_uri' in self.settings and 'janus_url' in self.settings:
            self.add_subapp(self.settings['signal_uri'], signal.WebApplication(self.settings['janus_url'], **kwargs))
        self.add_routes(routes)

    @classmethod
    async def factory(cls, options: argparse.Namespace):
        logging.basicConfig(level=(logging.DEBUG if options.debug else logging.WARNING))
        kwargs = dict((key, value) for key, value in options.__dict__.items() if
                      key in ('api_uri', 'signal_uri', 'janus_url', 'proxy_pass'))
        return cls(logger=logging.root, **kwargs)
