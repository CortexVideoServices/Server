"""
This module contains a set of tools to help you build the backend part of
applications used the Cortex Video Services.
"""
import json
from decimal import Decimal
from datetime import date, datetime
from aiohttp import web, ClientSession
from aiopg.sa.result import RowProxy


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


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, RowProxy):
            return dict(obj)
        return super().default(obj)
