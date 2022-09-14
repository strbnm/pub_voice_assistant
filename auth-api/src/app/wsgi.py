from gevent import monkey

monkey.patch_all()

from gevent.pywsgi import WSGIServer  # noqa

from app.main import create_app  # noqa
from app.settings.config import settings  # noqa

http_server = WSGIServer((settings.WSGI.HOST, settings.WSGI.PORT), create_app())
http_server.serve_forever()
