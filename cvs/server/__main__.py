import configargparse
from aiohttp import web
import cvs.server


parser = configargparse.ArgumentParser("CVS Server")
parser.add_argument('-c', '--config', is_config_file=True, help='config file path')
parser.add_argument('-j', '--janus-url', required=True, help='URL of Janus', env_var='JANUS_URL')
parser.add_argument('-u', '--postgres-dsn', required=True, help='URL of Postgres', env_var='POSTGRES_DSN')
parser.add_argument('-a', '--api-uri', default='/api', help='URI to server SDK API', env_var='SDK_API_URI')
parser.add_argument('-s', '--signal-uri', default='/ws', help='URI to websocket', env_var='SDK_SIGNAL_URI')
parser.add_argument('-p', '--port', default=5000, help='served on port', env_var='SERVER_PORT')
parser.add_argument('-d', '--debug', default=False, action='store_true', help='debug mode', env_var='DEBUG')
options, _ = parser.parse_known_args()
web.run_app(cvs.server.WebApplication.factory(options.postgres_dsn,
                                              options.api_uri,
                                              options.signal_uri,
                                              options.janus_url,
                                              options.debug), port=options.port)
