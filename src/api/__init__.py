import sys
import os
import logging
import secrets
from datetime import timedelta
from flask import Flask, render_template
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, "..")))

from models.user import db, User
from api.extensions import csrf, limiter, login_manager
from api.utils import IS_PRODUCTION, config

def create_app():
    # Load .env FIRST
    load_dotenv()

    # Flask App Setup
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "templates"),
        static_folder=os.path.join(BASE_DIR, "static"),
    )

    # Secret Key
    secret_key = os.environ.get("SECRET_KEY") or os.environ.get("FLOWTRACE_SECRET_KEY")
    if not secret_key:
        secret_key = config.get("auth", {}).get("secret_key", "")
        if not secret_key or secret_key in (
            "", "dev-fallback-key",
            "flowtrace-super-secret-key-change-me",
            "REPLACE_WITH_ENV_VAR",
        ):
            secret_key = secrets.token_hex(32)
            if IS_PRODUCTION:
                print("[WARNING] No SECRET_KEY set. Sessions will reset on restart.")
    app.secret_key = secret_key

    # Database
    database_url = os.environ.get("DATABASE_URL", "")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "connect_args": {
                "sslmode": "require",
                "connect_timeout": 10,
            },
        }
    else:
        # Local SQLite fallback
        local_db = os.path.abspath(os.path.join(BASE_DIR, "..", "flowtrace.db"))
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{local_db}"
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {}
        if IS_PRODUCTION:
            print("[WARNING] No DATABASE_URL set. Using local SQLite. Not for production!")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=IS_PRODUCTION,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        WTF_CSRF_ENABLED=True,
        WTF_CSRF_TIME_LIMIT=3600,
    )

    # Initialize Extensions
    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # Logging setup
    log_handlers = [logging.StreamHandler()]
    if not IS_PRODUCTION:
        try:
            log_dir = os.path.abspath(os.path.join(BASE_DIR, "..", "logs"))
            os.makedirs(log_dir, exist_ok=True)
            log_handlers.append(logging.FileHandler(os.path.join(log_dir, "flowtrace.log")))
        except (PermissionError, OSError):
            pass
    logging.basicConfig(
        level=logging.INFO if IS_PRODUCTION else logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=log_handlers,
    )
    logger = logging.getLogger("flowtrace")

    # Register Blueprints
    from api.routes.api import api_bp
    from api.routes.auth import auth_bp
    from api.routes.pages import pages_bp
    
    # Exempt CSRF for certain APIs
    csrf.exempt(api_bp)

    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(pages_bp)

    # Create tables
    with app.app_context():
        db.create_all()

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"500 error: {e}", exc_info=True)
        return render_template("errors/500.html"), 500

    # Security Headers
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if IS_PRODUCTION:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    return app
