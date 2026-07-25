from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_caching import Cache

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
talisman = Talisman(
    content_security_policy={
        'default-src': ["'self'"],
        'script-src': ["'self'", 'cdn.tailwindcss.com', "'unsafe-inline'"],
        'style-src': ["'self'", 'cdn.tailwindcss.com', "'unsafe-inline'"],
        'connect-src': ["'self'", 'https://cdn.tailwindcss.com'],
    }
)
cache = Cache()
