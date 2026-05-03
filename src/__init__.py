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

def create_app():
    app = Flask(__name__,
               template_folder='templates',
               static_folder='static')

    # Configure SQLAlchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "project.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Configure upload folders
    UPLOAD_FOLDER = os.path.join(app.root_path, "static/images/users")
    COURSE_UPLOAD_FOLDER = os.path.join(app.root_path, "static/images/courses")
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["COURSE_UPLOAD_FOLDER"] = COURSE_UPLOAD_FOLDER

    # Ensure templates are auto-reloaded
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    # Configure session
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    app.secret_key = "your-secret-key-here"
    Session(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(courses_bp)

    @app.after_request
    def after_request(response):
        """Ensure responses aren't cached"""
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    return app
