import json
import random
from aiohttp import web
from datetime import datetime, timedelta
from sqlalchemy import select, insert, update, delete
from typing import Optional, Dict

from cvs.tools import JSONEncoder
from cvs.server.models import Session

routes = web.RouteTableDef()
json_dumps = lambda obj: json.dumps(obj, cls=JSONEncoder)
json_response = lambda obj, *args, **kwargs: web.json_response(obj, *args, dumps=json_dumps, **kwargs)

SESSION_EXPIRED_SEC = 15 * 60


@routes.get('/state')
async def get_status(request: web.Request):
    return web.json_response({
        'status': 'OK'
    })


@routes.post('/v1/session')
@routes.get('/v1/session/{id}')
async def get_status(request: web.Request):
    app = request.app  # type: WebApplication
    if request.method == 'POST':
        data = await request.post()
        started_at = data.get('started_at')
        if started_at:
            started_at = datetime.fromisoformat(started_at)
        else:
            started_at = datetime.utcnow()
        allow_anonymous = data.get('allow_anonymous', 'false')
        allow_anonymous = allow_anonymous.lower() in ('true', '1', 'yes', 'y', 'allow')
        display_name = data.get('display_name')
        expired_at = data.get('expired_at')
        if expired_at:
            expired_at = datetime.fromisoformat(expired_at)
        else:
            expired_at = started_at + timedelta(seconds=SESSION_EXPIRED_SEC)
        session = await app.create_session(started_at, expired_at, display_name, allow_anonymous)
        if session:
            return json_response(session, status=201)
        else:
            return web.HTTPUnprocessableEntity()
    else:
        session_id = request.match_info['id']
        if session_id:
            session = await app.get_session(session_id)
            if session:
                return json_response(session)
        return web.HTTPNotFound()


class WebApplication(web.Application):
    """ Server SDK API
    """

    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.add_routes(routes)

    async def get_session(self, session_id, expired=False):
        """ Returns session dict if exist and not expired, otherwise None
        """
        query = select([Session]).where(Session.id == session_id)
        if not expired:
            query = query.where(Session.expired_at > datetime.utcnow())
        async with self.db.acquire() as connection:
            if session := await(await connection.execute(query)).first():
                return session

    async def create_session(self,
                             started_at: Optional[datetime], expired_at: datetime,
                             display_name: Optional[str], allow_anonymous: bool):
        """ Creates new session
        """
        while True:
            room_num = random.getrandbits(64)
            session_id = '{:016X}'.format(room_num)
            if await self.get_session(session_id):
                continue
            break
        query = insert(Session).values(id=session_id,
                                       room_num=room_num, display_name=display_name,
                                       started_at=started_at, expired_at=expired_at,
                                       allow_anonymous=allow_anonymous)
        async with self.db.acquire() as connection:
            if await self.get_session(session_id, True):
                await connection.execute(delete(Session).where(Session.id == session_id))
            if (await connection.execute(query)).rowcount:
                return await self.get_session(session_id)
