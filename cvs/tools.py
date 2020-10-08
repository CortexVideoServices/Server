"""
This module contains a set of tools to help you build the backend part of
applications used the Cortex Video Services.
"""

from aiohttp import web, ClientSession


@web.middleware
async def proxy_pass_middleware(request, handler, url):
    try:
        return await handler(request)
    except web.HTTPException as resp:
        if request.method in 'GET, HEAD':
            session = ClientSession()
            url = url + request.url.path + '?' + request.url.query_string
            resp = await session.request(request.method, url, headers=request.headers, cookies=request.cookies)
        return web.Response(status=resp.status, reason=resp.reason, headers=resp.headers, body=resp.content)