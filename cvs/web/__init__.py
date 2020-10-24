"""
This module contains a set of tools to help you build the backend part of
applications used the Cortex Video Services.
"""
import json
from aiohttp.helpers import sentinel
from aiohttp.typedefs import LooseHeaders
from aiohttp.web import json_response as _json_response, RouteDef, Response
from typing import Sequence, Optional, Any
from .utils import JSONEncoder


def json_response(data: Any = sentinel, *,
                  status: int = 200,
                  reason: Optional[str] = None,
                  headers: LooseHeaders = None) -> Response:
    """ Makes JSON response
    """
    return _json_response(data, status=status, reason=reason, headers=headers,
                          dumps=lambda obj: json.dumps(obj, cls=JSONEncoder))


def with_prefix(prefix: str, routes: Sequence[RouteDef]) -> Sequence[RouteDef]:
    """ Adds prefix to routes
    """
    return [RouteDef(route.method, prefix + route.path, route.handler, route.kwargs) for route in routes]
