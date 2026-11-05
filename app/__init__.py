import os
from threading import RLock

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

from app.config import Config, DATABASE_PATH


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # The app usually runs behind a reverse proxy (nginx) and optionally a
    # Cloudflare tunnel. Without ProxyFix, request.remote_addr is the proxy IP,
    # so every client shares a single rate-limit budget. Trusting one proxy hop
    # for X-Forwarded-For/Proto/Host restores the real client IP as the key.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    os.makedirs(app.config['CAPTURES_DIR'], exist_ok=True)
    DATABASE_PATH.parent.mkdir(exist_ok=True)
    return app


app = create_app()
Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
lock_app = RLock()

try:
    from flask_wtf import CSRFProtect
    csrf = CSRFProtect(app)
except Exception:
    # Dummy CSRF protection if flask_wtf is missing so the app still imports.
    class DummyCSRF:
        def init_app(self, app):
            pass

        def exempt(self, f):
            return f
    csrf = DummyCSRF()

try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
except Exception:
    # Dummy limiter if module is missing
    class DummyLimiter:
        def limit(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator

        def exempt(self, f):
            return f
    limiter = DummyLimiter()

from app import views
