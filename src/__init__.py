import os
from flask import Flask
from flask_session import Session

# Import Blueprints
from src.routes.auth import auth_bp
from src.routes.admin import admin_bp
from src.routes.main import main_bp
from src.routes.account import account_bp
from src.routes.courses import courses_bp

from src.extensions import db
from whitenoise import WhiteNoise
from flask_compress import Compress

def create_app():
    app = Flask(__name__,
               template_folder='templates',
               static_folder='static')

    # ── Optimizations ────────────────────────────────────────────────────────
    Compress(app)
    # Efficient static file serving (especially for Render)
    app.wsgi_app = WhiteNoise(app.wsgi_app, root='src/static/', prefix='static/')

    # ── Database ──────────────────────────────────────────────────────────────
    # Production: DATABASE_URL env var (PostgreSQL on Render)
    # Development: local SQLite fallback
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        # Render provides postgres:// but SQLAlchemy 2.x requires postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        os.makedirs(app.instance_path, exist_ok=True)
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            "sqlite:///" + os.path.join(app.instance_path, "project.db")
        )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Performance tuning for SQLAlchemy
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 10,
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # ── Extensions ────────────────────────────────────────────────────────────
    db.init_app(app)

    # ── Upload Folders ────────────────────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(app.root_path, "static/images/users")
    COURSE_UPLOAD_FOLDER = os.path.join(app.root_path, "static/images/courses")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(COURSE_UPLOAD_FOLDER, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["COURSE_UPLOAD_FOLDER"] = COURSE_UPLOAD_FOLDER

    # ── Session ───────────────────────────────────────────────────────────────
    # sqlalchemy type → sessions stored in DB → persistent across restarts
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "sqlalchemy"
    app.config["SESSION_SQLALCHEMY"] = db

    # Secret key from environment variable (set in Render dashboard)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    Session(app)

    # ── Templates ─────────────────────────────────────────────────────────────
    # Disable auto-reload in production for performance
    app.config["TEMPLATES_AUTO_RELOAD"] = os.environ.get("FLASK_DEBUG") == "1"

    # ── Blueprints ────────────────────────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(courses_bp)

    # ── After Request ─────────────────────────────────────────────────────────
    # @app.after_request
    # def after_request(response):
    #     """Disable client-side caching for all responses."""
    #     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    #     response.headers["Expires"] = 0
    #     response.headers["Pragma"] = "no-cache"
    #     return response

    return app
