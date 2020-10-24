import logging
from aiohttp import web
from aiopg.sa import create_engine
from cvs.server import api, signal

routes = web.RouteTableDef()


@routes.get('/state')
async def get_status(request: web.Request):
    app = request.app  # type: WebApplication
    return web.json_response(app.state)


class WebApplication(web.Application):
    """ CVS Server
    """

    def __init__(self, db_engine, api_uri, signal_uri, janus_url, **kwargs):
        super().__init__(**kwargs)
        self.__state = dict(config=dict(api_uri=api_uri, signal_uri=signal_uri))
        self.add_subapp(api_uri, api.WebApplication(db_engine, **kwargs))
        self.add_subapp(signal_uri, signal.WebApplication(db_engine, janus_url, **kwargs))
        self.add_routes(routes)
        self.__state['status'] = 'OK'

    @property
    def state(self):
        """ Application state """
        return dict((k, v) for k, v in self.__state.items())

    @classmethod
    async def factory(cls, postgres_url, api_uri, signal_uri, janus_url, debug=False):
        logging.basicConfig(level=(logging.DEBUG if debug else logging.WARNING))
        db_engine = await create_engine(postgres_url)
        return cls(db_engine, api_uri, signal_uri, janus_url, logger=logging.root)
