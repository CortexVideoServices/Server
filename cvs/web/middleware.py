import aiohttp
from aiohttp import web
from aiohttp.streams import StreamReader


class ProxyPass(object):
    """ Middleware helps to develop frontend application
    """

    def __init__(self, pass_url):
        self.__pass_url = pass_url

    @property
    def pass_url(self):
        """ URL to frontend development server
        """
        return self.__pass_url

    @web.middleware
    async def __call__(self, app, handler):
        """ Middleware """
        async def wrapped_handler(request):
            try:
                return await handler(request)
            except web.HTTPNotFound:
                async with aiohttp.ClientSession() as session:
                    url = self.pass_url + request.url.path + '?' + request.url.query_string
                    resp = await session.request(request.method, url, headers=request.headers, cookies=request.cookies)
                    body = resp.content
                    headers = [(name, value) for name, value in resp.headers.items()
                               if name in ('Content-Type', 'ETag', 'Date')]
                    if isinstance(resp.content, StreamReader):
                        body = await resp.content.read()
                    return web.Response(status=resp.status, reason=resp.reason, headers=headers, body=body)

        return wrapped_handler
