import random
import hashlib
from aiohttp import web
from datetime import datetime, timedelta
from sqlalchemy import select, insert, update
from typing import Optional
from cvs.server.models import Session, Application
from cvs.web import json_response

routes = web.RouteTableDef()

SESSION_EXPIRED = 15 * 60


@routes.post('/v1/session')
@routes.get('/v1/session/{id}')
async def get_status(request: web.Request):
    """ Session managements handlers
    """
    app = request.app  # type: WebApplication
    if request.method == 'POST':
        if request.content_type.startswith('application/json'):
            data = await request.json()
        else:
            data = await request.post()
        try:
            app_id = data['app_id']
            started_at = data.get('started_at')
            if started_at:
                started_at = datetime.fromisoformat(started_at)
            else:
                started_at = datetime.utcnow()
            allow_anonymous = data.get('allow_anonymous', 'false')
            allow_anonymous = allow_anonymous.lower() in ('true', '1', 'yes', 'y', 'allow') if isinstance(
                allow_anonymous, str) else allow_anonymous
            display_name = data.get('display_name')
            expired_at = data.get('expired_at')
            if expired_at:
                expired_at = datetime.fromisoformat(expired_at)
            else:
                expired_at = started_at + timedelta(seconds=SESSION_EXPIRED)
        except (KeyError, ValueError) as exc:
            raise web.HTTPBadRequest(reason=str(exc))
        session = await app.create_session(app_id, started_at, expired_at, display_name, allow_anonymous)
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


@routes.post('/v1/application')
async def application(request: web.Request):
    """ Application managements handlers
    """
    app = request.app  # type: WebApplication
    if request.content_type.startswith('application/json'):
        data = await request.json()
    else:
        data = await request.post()
    app_id = data.get('id')
    try:
        if app_id:
            # modification for exists application
            if await app.modify_application(app_id, data['jwt_secret'], data.get('description')):
                return web.HTTPOk()
        else:
            # new application to register
            app_id = await app.register_application(data['jwt_secret'], data['description'])
            if app_id:
                return json_response({'app_id': app_id}, status=201)
    except KeyError as exc:
        raise web.HTTPBadRequest(reason=str(exc))
    return web.HTTPUnprocessableEntity()


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

    async def create_session(self, app_id,
                             started_at: Optional[datetime], expired_at: datetime,
                             display_name: Optional[str], allow_anonymous: bool):
        """ Creates new session
        """
        while True:
            room_num = random.getrandbits(64)
            sha256 = hashlib.sha256(app_id.encode('utf8'))
            sha256.update('{:016X}'.format(room_num).encode('utf8'))
            session_id = sha256.hexdigest()
            if await self.get_session(session_id, True):
                continue
            break
        query = insert(Session).values(id=session_id, app_id=app_id,
                                       room_num=room_num, display_name=display_name,
                                       started_at=started_at, expired_at=expired_at,
                                       allow_anonymous=allow_anonymous)
        async with self.db.acquire() as connection:
            try:
                if (await connection.execute(query)).rowcount:
                    return await self.get_session(session_id)
            except Exception:
                self.logger.exception("Cannot create session_id")

    async def register_application(self, jwt_secret, description):
        """ Registers new application
        """
        sha256 = hashlib.sha256(description.encode('utf8'))
        sha256.update('{:016X}'.format(random.getrandbits(64)).encode('utf8'))
        app_id = sha256.hexdigest()
        query = insert(Application).values(id=app_id, description=description, jwt_secret=jwt_secret)
        async with self.db.acquire() as connection:
            try:
                if (await connection.execute(query)).rowcount:
                    return app_id
            except Exception:
                self.logger.exception("Cannot create app_id")

    async def modify_application(self, app_id, jwt_secret, description=None):
        """ Modifies data of exists application
        """
        query = update(Application).where(Application.id == app_id) \
            .values(jwt_secret=jwt_secret, modified_at=datetime.utcnow())
        if description:
            query = query.values(description=description)
        async with self.db.acquire() as connection:
            try:
                if (await connection.execute(query)).rowcount:
                    return app_id
            except Exception:
                self.logger.exception("Cannot modify app secret")
