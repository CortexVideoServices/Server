import logging
import asyncio
import aiohttp
from aiohttp import web

routes = web.RouteTableDef()


@routes.get('/state')
async def get_status(request: web.Request):
    app = request.app  # type: WebApplication
    return web.json_response({
        **app.state,
        'status': 'OK'
    })


@routes.get('/v1')
async def websocket_handler(request: web.Request):
    app = request.app  # type: WebApplication
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    await app._proxy2janus(ws)
    return ws


class WebApplication(web.Application):
    """ Signal
    """

    def __init__(self, janus_url, **kwargs):
        self.__state = {
            'requests': {
                'started': 0,
                'succeed': 0,
                'failed': 0,
            },
            'janus_url': janus_url
        }
        super().__init__(**kwargs)
        self.add_routes(routes)

    @property
    def state(self):
        return dict((k, v) for k, v in self.__state.items())

    async def __janus2ws(self, ws, janus):
        async for msg in janus:
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f'WS_PROXY(${id(ws)}) << ${msg.data}')
            if msg.type == aiohttp.WSMsgType.TEXT:
                await ws.send_str(msg.data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                exc = janus.exception()
                await ws.close(message=f'Remote exception: ${exc}')
                raise exc

    async def __ws2janus(self, ws, janus):
        async for msg in ws:
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f'WS_PROXY(${id(ws)}) >> ${msg.data}')
            if msg.type == aiohttp.WSMsgType.TEXT:
                await janus.send_str(msg.data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                exc = ws.exception()
                await janus.close(message=f'Remote exception: ${exc}')
                raise exc

    async def _proxy2janus(self, ws):
        session = aiohttp.ClientSession()
        try:
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f'WS_PROXY(${id(ws)}) establishing...')
            self.__state['requests']['started'] += 1
            async with session.ws_connect(self.__state['janus_url'], protocols=['janus-protocol']) as janus:
                await asyncio.gather(self.__ws2janus(ws, janus), self.__janus2ws(ws, janus))
            self.__state['requests']['succeed'] += 1
        except Exception:
            self.__state['requests']['failed'] += 1
            self.logger.exception(f'WS_PROXY(${id(ws)}) fail')
        finally:
            await session.close()
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f'WS_PROXY(${id(ws)}) done')
